import os
import cv2
import time
import pytz
import asyncio
import datetime
import threading
import subprocess 
import numpy as np
import mediapipe as mp
import imageio.v3 as iio
import imageio_ffmpeg as ffmpeg
import tensorflow.lite as tflite
from config import RTMP_URL
from picamera2 import Picamera2
from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from config import CAMERAID
from subprocess import Popen, PIPE
from api_client import fetch_detection_report,send_video_request

#globa const
FRAME_RATE = 15
FRAME_AGO = 120 # số frame trước
SECONDS_MAX = 20
output_path = "./videos/"
n_time_steps = 20
input_details = []
output_details = []

timezone = pytz.timezone('Etc/GMT-7')

# read model cheating
def initialize_interpreter(model_path="./model/model_cheating_recognize_v0_lite.tflite"):
    """Khởi tạo TFLite Interpreter"""
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

#read mediapipe and config
def initialize_pose_detector(model_path="./model/pose_landmarker_full.task"):
    """Khởi tạo MediaPipe Pose Landmarker"""
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=2,
        min_pose_detection_confidence=0.8,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False
    )
    return vision.PoseLandmarker.create_from_options(options)

# init camera
def initializeCamera(FRAME_RATE):
    """Khởi tạo và cấu hình Picamera2"""
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size":(640, 480) , "format": "RGB888"},
        controls={'FrameRate': FRAME_RATE}
    )
    picam2.configure(config)
    picam2.start()
    return picam2

def process_pose_landmarks(detector, frame, current_frame):
    """Phát hiện và xử lý Pose Landmarks"""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    results = detector.detect_for_video(mp_image, current_frame)
    return results

def stream_RTMP():
    command = ['ffmpeg',
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',  # format
            '-s', '640x480',
            '-r', '15', 
            '-i', '-',  # The input comes from a pipe
            '-c:v', 'libx264',
            '-g', '15',  
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'flv',
            #'-tag:v', 'h264',
            '-nostats',
            RTMP_URL]

    return subprocess.Popen(command, stdin=subprocess.PIPE)
    # stderr=subprocess.PIPE

def make_landmark_timestep(results):
    c_lm_0 = []
    c_lm_1 = []
    def add_lanmark(index):
        landmark = results.pose_landmarks[0][index]
        c_lm_0.append(landmark.x)
        c_lm_0.append(landmark.y)
        c_lm_0.append(landmark.z)
        c_lm_0.append(landmark.visibility)
        if len(results.pose_landmarks) > 1: 
            landmark = results.pose_landmarks[1][index]
            c_lm_1.append(landmark.x)
            c_lm_1.append(landmark.y)
            c_lm_1.append(landmark.z)
            c_lm_1.append(landmark.visibility)

    for i in range(25):
        add_lanmark(i)    
    return c_lm_0,c_lm_1


def detect(interpreter, lm_list, shoplifting_continous_count, sensitivity, pre_label):
    lm_list = np.array(lm_list, dtype=np.float32)
    lm_list = np.expand_dims(lm_list, axis=0)
    
    interpreter.set_tensor(input_details[0]['index'], lm_list)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])

    if output_data[0][0] > 0.5:
        label = "SHOPLIFTING"
        print("SHOPLIFTING ", shoplifting_continous_count)
        shoplifting_continous_count += 1
        if shoplifting_continous_count >= 3:
            print("Sending alarm...", shoplifting_continous_count)
            sensitivity = shoplifting_continous_count
    else:
        label = "NORMAL"
        if (pre_label == "SHOPLIFTING"): 
            sensitivity = shoplifting_continous_count
            
        shoplifting_continous_count = 0
        
    return label,shoplifting_continous_count, sensitivity


def draw_datetime_to_frame(frame):
    current_time = datetime.datetime.now(pytz.utc).astimezone(timezone).strftime('%d-%m-%Y %H:%M:%S')
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.5
    font_color = (255, 255, 255)
    font_thickness = 1
    (text_width, text_height), _ = cv2.getTextSize(current_time, font, font_scale, font_thickness)
    top_left_corner_x = 0
    top_left_corner_y = 0
    bottom_right_corner_x = top_left_corner_x + text_width + 4
    bottom_right_corner_y = top_left_corner_y + text_height + 4
    cv2.rectangle(frame, (top_left_corner_x, top_left_corner_y), (bottom_right_corner_x, bottom_right_corner_y), (0, 0, 0), -1)
    text_x = top_left_corner_x + 2
    text_y = bottom_right_corner_y - 2
    cv2.putText(frame, current_time, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
    return frame
    

async def save_video_and_send(frames, action_id, timestamp):
    t = time.time()
    global output_path
    if not frames or not all(isinstance(frame, np.ndarray) for frame in frames):
        print("Danh sách frames không hợp lệ hoặc rỗng. Không thể tạo video.")
        return

    video_filename = f"{action_id}.mp4"
    full_path = os.path.join(output_path, video_filename)

    # Lưu video với codec libx264
    iio.imwrite(full_path, frames, fps=FRAME_RATE, codec="libx264")
    print(f"Video đã được lưu tại: {full_path}")
    print("thời gian lưu video", time.time()-t)

    try:
        t = time.time()
        # Gửi video
        results = await send_video_request(full_path, action_id)
        print("Upload video : ", results)

        # Xóa video sau khi gửi thành công
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Video đã được xóa: {full_path}")
        else:
            print(f"Không tìm thấy file để xóa: {full_path}")
        print("thời gian gửi video : ", time.time()-t)

    except Exception as e:
        print(f"Lỗi khi gửi hoặc xóa video: {str(e)}")
        


def threaded_save_video_and_send(frames, action_id, timestamp):
    def task():
        asyncio.run(save_video_and_send(frames, action_id, timestamp))

    thread = threading.Thread(target=task)
    thread.start()
   

async def run():
    global current_frame,input_details,output_details

    picam2 = initializeCamera(FRAME_RATE)
    interpreter = initialize_interpreter()
    detector = initialize_pose_detector()
    frame_buffer = deque(maxlen=FRAME_RATE * SECONDS_MAX)
    process = stream_RTMP()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    shoplifting_continous_count_0 = 0
    shoplifting_continous_count_1 = 0 
    lm_list_0 = []
    lm_list_1 = []
    label_0 = "NORMAL"
    label_1 = "NORMAL"
    sensitivity_0 =0
    sensitivity_1 =0
    current_frame =0
    action_id = "0"
    timestamp = datetime.datetime.now().timestamp()

    try:
        while True:
            frame = picam2.capture_array("main")
            # cv2.imshow("Frame", frame)
            timestamp = datetime.datetime.now().timestamp()
            pre_label_0 = label_0
            pre_label_1 = label_1
            frame_buffer.append(frame)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      
            frame = draw_datetime_to_frame(frame)     

            # detect cheating
            results = process_pose_landmarks(detector, frame, current_frame)
            if results.pose_landmarks:
                c_lm_0, c_lm_1 = make_landmark_timestep(results)
                if len(c_lm_0) > 0 : 
                    lm_list_0.append(c_lm_0)
                if len(c_lm_1) > 0 :
                    lm_list_1.append(c_lm_1) 
                if (len(lm_list_0) >= n_time_steps):
                    lm_data_to_predict_0 = lm_list_0[-n_time_steps:]
                    label_0, shoplifting_continous_count_0,sensitivity_0 = detect(interpreter, lm_data_to_predict_0,shoplifting_continous_count_0, sensitivity_0, pre_label_0)
                    if label_0 == "NORMAL" and pre_label_0 == "SHOPLIFTING":
                        try:
                            print("sensitivity_0  : ", sensitivity_0,"sensitivity_1: ",sensitivity_1)
                            report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity_0,80)
                            sensitivity_0 = 0
                            shoplifting_continous_count_0 =0
                            action_id = report.get('actionId', "0")
                            if action_id:
                                threaded_save_video_and_send(frame_buffer.copy(), action_id[:], int(timestamp))
                        except Exception as e:
                            print(f"Lỗi khi gửi : {str(e)}")

                    #lưu 32 frame trước đó - done
                    if label_0 == "NORMAL" and sensitivity_1 == 0 and len(frame_buffer) > (FRAME_AGO + n_time_steps):
                        frame_buffer = list(frame_buffer)[-(FRAME_AGO + n_time_steps):]
                    lm_list_0.pop(0)

                if (len(lm_list_1) >= n_time_steps):
                    lm_data_to_predict_1 = lm_list_1[-n_time_steps:]
                    label_1, shoplifting_continous_count_1,sensitivity_1 = detect(interpreter, lm_data_to_predict_1,shoplifting_continous_count_1, sensitivity_1, pre_label_1)
                    if label_1 == "NORMAL" and pre_label_1 == "SHOPLIFTING":
                        try:
                            print("sensitivity_0  : ", sensitivity_0,"sensitivity_1: ",sensitivity_1)
                            report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity_1,80)
                            sensitivity_1 =0
                            shoplifting_continous_count_1 =0
                            action_id = report.get('actionId', "0")
                            if action_id:
                                threaded_save_video_and_send(frame_buffer.copy(), action_id[:], int(timestamp))
                        except Exception as e:
                            print(f"Lỗi khi gửi : {str(e)}")

                    #lưu 32 frame trước đó - done
                    if label_1 == "NORMAL" and sensitivity_0 == 0 and len(frame_buffer) > (FRAME_AGO + n_time_steps):
                        frame_buffer = list(frame_buffer)[-(FRAME_AGO + n_time_steps):]
                    lm_list_1.pop(0)

                for pose_landmarks in results.pose_landmarks:
                        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                        pose_landmarks_proto.landmark.extend([
                            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                            z=landmark.z) for landmark
                            in pose_landmarks
                        ])
            else:
                lm_list_0 = []
                lm_list_1 = []
                if label_0 == "SHOPLIFTING" :
                    try:
                        print("sensitivity_0  : ", sensitivity_0,"sensitivity_1: ",sensitivity_1)
                        report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity_0,80)
                        action_id = report.get('actionId', "0")
                        if action_id:
                            threaded_save_video_and_send(frame_buffer.copy(), action_id[:], int(timestamp))
                    except Exception as e:
                        print(f"Lỗi khi gửi : {str(e)}")
                label_0 = "NORMAL"

                if label_1 == "SHOPLIFTING" :
                    try:
                        print("sensitivity_0  : ", sensitivity_0,"sensitivity_1: ",sensitivity_1)
                        report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity_1,80)
                        action_id = report.get('actionId', "0")
                        if action_id:
                            threaded_save_video_and_send(frame_buffer.copy(), action_id[:], int(timestamp))
                    except Exception as e:
                        print(f"Lỗi khi gửi : {str(e)}")
                label_1 = "NORMAL"
                sensitivity_0 = 0
                sensitivity_1 = 0
                shoplifting_continous_count_0 =0
                shoplifting_continous_count_1 = 0
                if len(frame_buffer)>(FRAME_AGO):
                    frame_buffer = list(frame_buffer)[-(FRAME_AGO):]

            current_frame += 1       
            process.stdin.write(frame.tobytes())

            # Thoát khi nhấn 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Stream ended.")
    finally:
        picam2.close()
        process.stdin.close()
        process.wait()
        cv2.destroyAllWindows()
