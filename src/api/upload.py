# src/api/upload.py

import requests
from src.config.settings import SERVER_URL, TOKEN

def upload_file(file_path):
    url = f"{SERVER_URL}/api/v1/upload"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files)
        return response.json()
