# src/main.py

from src.api import auth, upload, stream
from src.config.settings import TOKEN
import threading
def main():
    print("1. Đăng nhập")
    print("2. Upload file")
    print("3. Stream video")
    print("4. Đăng ký")
    choice = input("Chọn chức năng: ")

    if choice == "1":
        username = input("Tên đăng nhập: ")
        password = input("Mật khẩu: ")
        try:
            token = auth.login(username, password)
            print("Đăng nhập thành công!")
            with open(".env", "a") as env_file:
                env_file.write(f"TOKEN={token}\n")
        except Exception as e:
            print(f"Đăng nhập thất bại: {e}")

    elif choice == "2":
        if TOKEN:
            file_path = input("Đường dẫn đến file: ")
            response = upload.upload_file(file_path)
            print("Kết quả upload:", response)
        else:
            print("Vui lòng đăng nhập trước.")

    elif choice == "3":
        stream_thread = threading.Thread(target=stream.run, daemon=True)
        stream_thread.start()
        print("Đang stream video...")
        stream.run()
        # if TOKEN:
        #     video_source = input("Đường dẫn đến nguồn video: ")
        #     process = stream.start_stream(video_source)
        #     print("Đang stream... Nhấn Ctrl+C để dừng.")
        #     try:
        #         process.wait()
        #     except KeyboardInterrupt:
        #         process.terminate()
        #         print("Đã dừng stream.")
        # else:
        #     print("Vui lòng đăng nhập trước.")
    elif choice == "4":
        username = input("Tên đăng nhập: ")
        password = input("Mật khẩu: ")
        try:
            token = auth.register(username, password)
            print("Đăng ký thành công!")
        except Exception as e:
            print(f"Đăng ký thất bại: {e}")

if __name__ == "__main__":
    main()
