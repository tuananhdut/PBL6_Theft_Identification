import threading
import time
import subprocess
import cv2
import datetime
import pytz

# Đường dẫn đến tệp video
video_path = "./video.mp4"

rtmp_url = "rtmp://167.71.195.130/live"

timezone = pytz.timezone('Etc/GMT-7')
ffmpeg_cmd = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-pix_fmt', 'bgr24',  # OpenCV đọc khung hình với định dạng BGR
    '-s', '640x480',
    '-r', '30',
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-b:v', '1000k',
    '-bufsize', '500k',
    '-f', 'flv',
    rtmp_url
]

# Tạo process để truyền dữ liệu qua FFmpeg
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

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

def write_to_ffmpeg():
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Không thể mở tệp video.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Kết thúc tệp video.")
            break

        # Thay đổi kích thước khung hình thành 640x480 (nếu cần)
        frame = cv2.resize(frame, (640, 480))

        # Vẽ thời gian hiện tại lên khung hình
        frame = draw_datetime_to_frame(frame)

        # Ghi dữ liệu vào FFmpeg
        process.stdin.write(frame.tobytes())

    cap.release()

def main():
    thread = threading.Thread(target=write_to_ffmpeg, daemon=True)
    thread.start()

    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stream ended.")
    finally:
        process.stdin.close()
        process.wait()

if __name__ == "__main__":
    main()
