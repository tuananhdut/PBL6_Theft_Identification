import requests
from config import SERVER_URL,RTMP_URL


# create camera (output:cameraId, linkingCode)
def fetch_camera_register_data():
    url = f"{SERVER_URL}/camera/register"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            cameraId = data["cameraId"]
            linkingCode = data["linkingCode"]
            return data
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def fetch_detection_report(camera_id, begin_time, end_time, sensitivity):
    url = f"{SERVER_URL}/detect/report"
    params = {
        "cameraId": camera_id,
        "beginTime": begin_time,
        "endTime": end_time,
        "sensitivity": sensitivity
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP
        return response.json()  # Trả về dữ liệu JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

def upload_video(action_id, video_file_path):
    url = f"{SERVER_URL}/detect/video"
    
    try:
        with open(video_file_path, 'rb') as video_file:
            # Tạo data (actionID) và tệp video dưới dạng form-data
            files = {
                'file': (video_file_path, video_file, 'video/mp4')  # Đảm bảo bạn chỉ định đúng loại MIME của tệp
            }
            data = {
                'actionID': action_id
            }

            # Gửi yêu cầu POST với file và tham số actionID
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP
            return response.json()  # Trả về dữ liệu JSON

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
    except FileNotFoundError:
        print(f"File {video_file_path} not found.")
        return {"error": f"File {video_file_path} not found."}


