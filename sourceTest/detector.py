import argparse
import sys
import time
import datetime
import pytz
import cv2
import numpy as np
from picamera2 import Picamera2
from collections import deque
import subprocess

# Initialize RTMP URL and command
rtmp_url = 'rtmp://192.168.46.198/live/stream1'
command = [
    'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24',
    '-s', '640x480', '-r', '15', '-i', '-', '-c:v', 'libx264', '-g', '30', 
    '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', '-f', 'flv', rtmp_url
]

process = subprocess.Popen(command, stdin=subprocess.PIPE)

# Initialize settings
CAMERA_FPS = 30
timezone = pytz.timezone('Etc/GMT-7')
frame_buffer = deque(maxlen=CAMERA_FPS * 15)  # Holds the last 15 seconds of footage

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

def run():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}, controls={'FrameRate': CAMERA_FPS}))
    picam2.start()

    while True:
        frame = picam2.capture_array()
        camera_feed_frame = draw_datetime_to_frame(frame)

        rgb_image = cv2.cvtColor(camera_feed_frame, cv2.COLOR_BGR2RGB)
        frame_buffer.append(rgb_image)
        process.stdin.write(rgb_image.tobytes())

        # Stop the program if the ESC key is pressed
        if cv2.waitKey(1) == 27:
            break

    picam2.close()
    process.stdin.close()
    process.wait()
    cv2.destroyAllWindows()

def main():
    run()

if __name__ == '__main__':
    main()
