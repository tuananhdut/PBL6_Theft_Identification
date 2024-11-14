#!/bin/bash

# Stream video from the camera using libcamera and ffmpeg

# Define the RTMP server URL
RTMP_SERVER="rtmp://192.168.46.198/live/stream1"

# Set video parameters
WIDTH=640
HEIGHT=480
FPS=15
BITRATE="1000k"
CODEC="yuv420"

# Capture video using libcamera and pipe it to FFmpeg for streaming
echo "Starting video stream from the camera..."

# libcamera-vid captures video from the camera
libcamera-vid -t 0 \                           # Capture video indefinitely
  --inline \                                    # Use inline metadata for FFmpeg
  --width $WIDTH \                              # Set video width
  --height $HEIGHT \                            # Set video height
  --framerate $FPS \                           # Set framerate to 15 fps
  --codec $CODEC \                              # Set codec to yuv420
  -o - |                                        # Output to stdout (pipe)

# Pipe the captured video into FFmpeg for streaming
ffmpeg -fflags nobuffer \                       # Disable buffering for low-latency streaming
  -f rawvideo \                                 # Specify input format as raw video
  -pix_fmt yuv420p \                            # Set pixel format to yuv420p
  -s ${WIDTH}x${HEIGHT} \                       # Set video resolution to 640x480
  -i - \                                        # Input from stdin (pipe)
  -c:v libx264 \                                # Use libx264 video codec
  -preset veryfast \                            # Use veryfast preset for encoding speed
  -tune zerolatency \                           # Tune for low-latency streaming
  -g 30 \                                       # Set keyframe interval to 30
  -b:v $BITRATE \                               # Set video bitrate to 1000k
  -f flv $RTMP_SERVER                           # Stream to RTMP server

#chmod +x stream.sh
#./stream.sh
