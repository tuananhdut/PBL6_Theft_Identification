from config import CAMERAID, update_env_variable
from api_client import fetch_camera_register_data
import asyncio 
# import streamer
# import streamAndDetectCheating
# import detect_thread
import final_detect

async def main():
    # check camera ID
    global CAMERAID  
    if not CAMERAID:
        result = await fetch_camera_register_data()
        update_env_variable('CAMERAID',result['cameraId'])
        update_env_variable('LINK_CODE',result['linkingCode'])
        print("camera id = ",result['cameraId'])
    print("camera id = ",CAMERAID)

    # streamer
    await final_detect.run()

if __name__ == "__main__":
    asyncio.run(main())
