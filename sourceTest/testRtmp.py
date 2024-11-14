# test rtmp
import cv2  # Import OpenCV lib

# Mở kết nối đến video RTMP stream
cap = cv2.VideoCapture('rtmp://192.168.46.198/live/stream1')

# Kiểm tra nếu kết nối thành công
while cap.isOpened():
    ret, frame = cap.read()  # Đọc từng frame

    if ret:
        # Hiển thị frame lên cửa sổ
        cv2.imshow('Video Stream', frame)

        # Kiểm tra xem người dùng có nhấn phím 'q' để thoát không
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Giải phóng tài nguyên khi kết thúc
cap.release()
cv2.destroyAllWindows()
