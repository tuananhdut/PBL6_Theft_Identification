import requests
from src.config.settings import SERVER_URL

def login(username, password):
    url = f"{SERVER_URL}/api/v1/login"
    response = requests.post(url, json={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        raise Exception("Login failed!")

def register(username, password):
    url = f"{SERVER_URL}/api/v1/register"
    response = requests.post(url, json={"username": username, "password": password})
    return response.json()
