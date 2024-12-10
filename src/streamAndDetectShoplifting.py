import subprocess
import cv2
import datetime
import pytz
import os
from picamera2 import Picamera2
from config import RTMP_URL
import mediapipe as mp
import numpy as np
import tensorflow.lite as tflite
from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from concurrent.futures import ThreadPoolExecutor
from config import CAMERAID
from api_client import fetch_detection_report,send_video_request

#globa const
FRAME_RATE = 15
FRAME_AGO = 120 # số frame trước
SECONDS_MAX = 20
lm_list = []
label = "NORMAL"
current_frame = 0
shoplifting_continous_count = 0 
frame_buffer = deque(maxlen=FRAME_RATE * SECONDS_MAX)
output_path = "./videos/"
action_id = ""
confidenceGlobal = 0
sensitivity = 0
pre_label = "NORMAL"

#declaration mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# read model shoplifting
n_time_steps = 12
interpreter = tflite.Interpreter(model_path="./model/model_shoplifting_recognize_v0_lite.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#read mediapipe and config
mediapipe_pose_model_asset = "./model/pose_landmarker_full.task"
base_options = python.BaseOptions(model_asset_path=mediapipe_pose_model_asset)
options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.8,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False)

detector = vision.PoseLandmarker.create_from_options(options)


# config picamera2
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={'FrameRate': FRAME_RATE})
picam2.configure(config)
picam2.start()


timezone = pytz.timezone('Etc/GMT-7')
ffmpeg_cmd = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-pix_fmt', 'rgb24',
    '-s', '640x480',
    '-r', '15',
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-b:v', '1000k',
    '-bufsize', '500k',
    '-f', 'flv',
    RTMP_URL
]


# Tạo process để truyền dữ liệu qua FFmpeg
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

executor = ThreadPoolExecutor(max_workers=1)
def make_landmark_timestep(results):
    c_lm = []
    def add_lanmark(index):
        landmark = results.pose_landmarks[0][index]
        c_lm.append(landmark.x)
        c_lm.append(landmark.y)
        c_lm.append(landmark.z)
        c_lm.append(landmark.visibility)

    for i in range(27):
        add_lanmark(i)
    
    return c_lm


def draw_landmark_on_image(mpDraw, results, img):
    mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
    for id, lm in enumerate(results.pose_landmarks.landmark):
        h, w, c = img.shape
        print(id, lm)
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
    return img


def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 30)
    fontScale = 1
    fontColor = (0, 255, 0)
    thickness = 2
    lineType = 2
    cv2.putText(img, label,
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                thickness,
                lineType)
    return img


def detect(interpreter, lm_list):
    global label, shoplifting_continous_count, input_details, output_details, confidenceGlobal,pre_label

    lm_list = np.array(lm_list, dtype=np.float32)
    lm_list = np.expand_dims(lm_list, axis=0)
    
    interpreter.set_tensor(input_details[0]['index'], lm_list)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    confidence = output_data[0][0]

    if confidence > 0.5:
        label = "SHOPLIFTING"
        print("shoplifting ", shoplifting_continous_count)
        shoplifting_continous_count += 1
        confidenceGlobal += confidence
        if shoplifting_continous_count >= 3:
            print("Sending alarm...", shoplifting_continous_count, "confidence : ",int(confidenceGlobal/shoplifting_continous_count*100))
    else:
        label = "NORMAL"
        if (pre_label == "SHOPLIFTING") : 
            sensitivity = int(confidenceGlobal/shoplifting_continous_count*100)
        shoplifting_continous_count = 0
        confidenceGlobal = 0
        
    return label


def threaded_detect(interpreter, lm_data):
    global label
    label = detect(interpreter, lm_data)


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
    global output_path
    if not frames or not all(isinstance(frame, np.ndarray) for frame in frames):
        print("Danh sách frames không hợp lệ hoặc rỗng. Không thể tạo video.")
        return

    size = (frames[0].shape[1], frames[0].shape[0])
    video_filename = f"{action_id}.mp4"
    full_path = os.path.join(output_path, video_filename)

    # Định nghĩa codec và VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec MP4
    out = cv2.VideoWriter(full_path, fourcc, FRAME_RATE, size)
    for frame in frames:
        out.write(frame)
    out.release()

    try:
        # Gửi video
        results = await send_video_request(full_path, action_id)
        print("Upload video : ", results)

        # Xóa video sau khi gửi thành công
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Video đã được xóa: {full_path}")
        else:
            print(f"Không tìm thấy file để xóa: {full_path}")

    except Exception as e:
        print(f"Lỗi khi gửi hoặc xóa video: {str(e)}")



async def run():
    global lm_list,label,current_frame,detector, shoplifting_continous_count, n_time_steps, frame_buffer, action_id, confidenceGlobal, pre_label

    timestamp = datetime.datetime.now().timestamp()

    try:
        while True:
            frame = picam2.capture_array("main")
            timestamp = datetime.datetime.now().timestamp()
            pre_label = label
            frame_buffer.append(frame)

            #add frame in deque
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      
            frame = draw_datetime_to_frame(frame)     
            # cv2.imshow("Frame", rgb_image)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

            # detect shoplifting
            results = detector.detect_for_video(mp_image, current_frame) 
            if results.pose_landmarks:
                c_lm = make_landmark_timestep(results)
                lm_list.append(c_lm)

                if len(lm_list) >= n_time_steps:
                    lm_data_to_predict = lm_list[-n_time_steps:]
                    label = detect(interpreter, lm_data_to_predict)

                    # hết shoplifting thì lưu video lại và gửi lên server
                    if label == "NORMAL" and pre_label == "SHOPLIFTING":
                        report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity)
                        action_id = report['actionId']
                        await save_video_and_send(frame_buffer, action_id, timestamp)

                    #lưu 32 frame trước đó - done
                    if label == "NORMAL" and len(frame_buffer) > (FRAME_AGO + n_time_steps):
                        frame_buffer = list(frame_buffer)[-(FRAME_AGO + n_time_steps):]

                    #nếu phát hiện shoplifting thì gửi thông báo - done
                    if label == "SHOPLIFTING" and pre_label == "NORMAL":
                        print("sen message")
                        # report = await fetch_detection_report(CAMERAID, "11111", "222222", 16)
                        # action_id = report['actionId']
                    lm_list.pop(0)

                for pose_landmarks in results.pose_landmarks:
                        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                        pose_landmarks_proto.landmark.extend([
                            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                            z=landmark.z) for landmark
                            in pose_landmarks
                        ])
            else:
                lm_list = []
                if label == "SHOPLIFTING" :
                    report = await fetch_detection_report(CAMERAID, int(timestamp - len(frame_buffer)/FRAME_RATE), int(timestamp), sensitivity)
                    action_id = report['actionId']
                    await save_video_and_send(frame_buffer, action_id, timestamp)
                label = "NORMAL"
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
