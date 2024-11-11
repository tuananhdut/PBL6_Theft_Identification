from fastapi import FastAPI, Depends, HTTPException, WebSocket, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from picamera2 import Picamera2
from pydantic import BaseModel
from typing import Optional
import asyncio
import jwt
import time
import cv2

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình JWT
SECRET_KEY = "taos"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# Mô hình User
class User(BaseModel):
    username: str
    password: str

# Hàm tạo token
def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + 60 * ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Hàm xác thực người dùng
def authenticate_user(username: str, password: str):
    if username == "admin" and password == "password":  # Chỉ là ví dụ, không nên dùng mật khẩu đơn giản như vậy
        return {"username": username}
    return None

# Endpoint đăng nhập
@app.post("/token")
async def login(user: User):
    authenticated_user = authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Hàm giải mã JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

active_clients_stream = 0
picam2 = Picamera2()

def controlerPicam2(value):
    global picam2  # Đảm bảo sử dụng biến toàn cục

    if value == 1:
        # Khởi tạo Picamera2
        # Cấu hình camera trước khi bắt đầu stream
        picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))

        # Kiểm tra xem camera có được cấu hình thành công không
        if picam2.camera_config is None:
            raise Exception("Camera configuration failed.")

        # Khởi động camera
        picam2.start()
    elif value == 0:
        # Dừng camera khi giá trị khác 0
        picam2.stop()
    
# Hàm stream video
async def stream_video():
    try:
        while True:
            # Capture một frame từ camera
            frame = picam2.capture_array()

            # Mã hóa frame thành JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield video stream (MIME type image/jpeg)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # Điều khiển frame rate, nếu cần (30 FPS)
            await asyncio.sleep(1 / 30)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
# Endpoint stream video
@app.get("/stream")
async def get_video_stream():
    global active_clients_stream
    active_clients_stream += 1
    controlerPicam2(active_clients_stream)
    try:
        return StreamingResponse(stream_video(), media_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        print(f"Error in streaming: {e}")
        raise HTTPException(status_code=500, detail="Error streaming video")
    # finally:
        # active_clients_stream -= 1
        # controlerPicam2(active_clients_stream)
        # print("disconnect")

# Endpoint gửi file đến client
@app.post("/send-file")
async def send_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    file_content = await file.read()
    with open(f"./uploaded_{file.filename}", "wb") as f:
        f.write(file_content)
    return {"message": f"File {file.filename} received"}

# Endpoint gửi message đến client qua WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        await websocket.accept()
        while True:
            await websocket.send_text("Hello from Raspberry Pi!")
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except jwt.ExpiredSignatureError:
        await websocket.close()

# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=" 192.168.46.198", port=8000)
    
