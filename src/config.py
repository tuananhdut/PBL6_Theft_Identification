import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
RTMP_URL = os.getenv("RTMP_URL", "rtmp://localhost/live/stream")

