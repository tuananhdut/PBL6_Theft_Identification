file_name = "./test_dataset/test_ras.mp4"
shoplifting_continous_count = 0 
video_reader = cv2.VideoCapture(file_name)

out_path = "./evaluation/output_ras1.mp4"
    # Get the width and height of the video.
original_video_width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
original_video_height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize the VideoWriter Object to store the output video in the disk.
video_writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc('M', 'P', '4', 'V'), 
                                   video_reader.get(cv2.CAP_PROP_FPS), (original_video_width, original_video_height))

fps = video_reader.get(cv2.CAP_PROP_FPS)
detector = vision.PoseLandmarker.create_from_options(options)
lm_list = []
label = "N/A"
current_frame = 0
# Thiết lập cửa sổ có tên "Image"
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
# Đặt kích thước cửa sổ là rộng 400 và cao 600
cv2.resizeWindow("Image", 400, 600)
# Hiển thị text tại góc trên bên phải
while True:
    success, frame = video_reader.read()
    if not success:
        break

    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    # Calculate timestamp based on frame count and fps
    current_timestamp = int((current_frame / fps) * 1000)

    # tren rpi, toc do toi da 5 fps
    results = detector.detect_for_video(mp_image, current_frame) 
    if results.pose_landmarks:
        if current_frame % 2 == 0: # moi truong video, cu 2 frame thi lay keypoint day vao model, 
                                    # tren rpi k can phai check frame, day thang vao (vi co delay san)
            c_lm = make_landmark_timestep(results)
            lm_list.append(c_lm)
            if len(lm_list) >= n_time_steps:
                lm_data_to_predict = lm_list[-n_time_steps:]
                label = detect(interpreter, lm_data_to_predict)
                #executor.submit(threaded_detect, interpreter, lm_data_to_predict)
                lm_list.pop(0)
                #lm_list = []

        for pose_landmarks in results.pose_landmarks:
                # Draw the pose landmarks.
                pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                pose_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                    z=landmark.z) for landmark
                    in pose_landmarks
                ])
                mp_drawing.draw_landmarks(
                    frame,
                    pose_landmarks_proto,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing_styles.get_default_pose_landmarks_style())

    else:
        lm_list = []
    current_frame += 1       
    frame = draw_class_on_image(label, frame)
    cv2.imshow("Image", frame)
    video_writer.write(frame)
    if cv2.waitKey(1) == ord('q'):
        break

print(current_frame)
video_reader.release()
video_writer.release()
cv2.destroyAllWindows()