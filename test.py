from picamera2 import Picamera2
import subprocess
import cv2
import datetime
import pytz


# Kh?i t?o d?i tu?ng Picamera2
picam2 = Picamera2()

# C?u hình camera v?i d?nh d?ng YUV420
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "YUV420"})
picam2.configure(config)
# picam2.set_controls({"FrameDurationLimits": (33333, 33333)})  # Tuong duong v?i 30 FPS
picam2.set_controls({"FrameDurationLimits": (66666, 66666)}) 
picam2.start()

rtmp_url = "rtmp://192.168.46.198/live/stream1"

timezone = pytz.timezone('Etc/GMT-7')
# ổn định nhất độ trễ tầm 6s
ffmpeg_cmd = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-pix_fmt', 'yuv420p',
    '-s', '640x480',
    '-r', '15',
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',  # Gi?m d? tr? cho FFmpeg
    '-b:v', '1000k',         # Bitrate cho video
    '-bufsize', '500k',      # Gi?m kích thu?c b? d?m
    '-f', 'flv',
    rtmp_url
]

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

try:
    while True:
        # Ch?p m?t khung hình t? camera
        frame = picam2.capture_array("main")
        frame = draw_datetime_to_frame(frame)

        # G?i d? li?u khung hình d?n FFmpeg qua pipe stdin
        process.stdin.write(frame.tobytes())

        # Hi?n th? khung hình b?ng OpenCV (tùy ch?n)
        # cv2.imshow('Camera', frame)

        # Thoát khi nh?n 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("K?t thúc stream.")

finally:
    picam2.close()
    process.stdin.close()
    process.wait()
    cv2.destroyAllWindows()
