import numpy as np
import cv2
import sys
import base64                
import requests
from Lepton3 import Lepton3
from datetime import datetime
import time
import paramiko
import json
import os
import shutil
import schedule
import subprocess



api = 'http://115.68.41.205:8082/file/upload'
FRAME_LENGTH = 3
DEFAULT_THRESHOLD = 960
IMG_DIR = '/home/pi/Lepton/data'
source_version = 1112


def read_stft_threshold(deviceId):
    '''
    stft로 threshold.json 파일 읽어서 deviceID 각각의 th값 읽음
    '''
    host = '115.68.41.205'
    port = 22022
    username = 'mill'
    password = 'tkdydwkdlqslek'

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    stft = paramiko.SFTPClient.from_transport(transport)

    file_path = f'/home/mill/imageUpload/threshold.json'
    threshold = DEFAULT_THRESHOLD
    try:
        with stft.open(file_path, 'r') as file:
            file_content = file.read()
        json_data = json.loads(file_content.decode('utf-8'))
        threshold = json_data.get(deviceId, DEFAULT_THRESHOLD)
    except Exception as e:
        print('stft threshold error', str(e))
    finally:
        stft.close()
        transport.close()
    return threshold


def read_stft_update(deviceId):
    '''
    stft로 update.json 파일 읽어서 deviceID 각각의 업데이트 여부 판단
    '''
    host = '115.68.41.205'
    port = 22022
    username = 'mill'
    password = 'tkdydwkdlqslek'

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    stft = paramiko.SFTPClient.from_transport(transport)

    file_path = f'/home/mill/imageUpload/update.json'
    version = source_version
    try:
        with stft.open(file_path, 'r') as file:
            file_content = file.read()
        json_data = json.loads(file_content.decode('utf-8'))
        version = json_data.get(deviceId, source_version)
    except Exception as e:
        print('stft update error', str(e))
    finally:
        stft.close()
        transport.close()
    return version


def capture(before_image=None):
  '''
  input 이전 프레임
  output 현재 프레임, 이전프레임과의 차이(th이상일경우)
  '''
  with Lepton3('/dev/spidev0.0') as l:
    frame, _ = l.capture()
  cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(frame, 8, frame)
  now_image = np.uint8(frame)

#   now_image = cv2.rotate(now_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#   now_image = now_image[..., np.newaxis]
  if before_image is None:
    before_image = now_image
    return now_image, 0

  _, th_now_image = cv2.threshold(now_image, 127, 255, cv2.THRESH_BINARY)
  th_now_image = th_now_image[..., np.newaxis]

  _, th_before_image = cv2.threshold(before_image, 127, 255, cv2.THRESH_BINARY)
  th_before_image = th_before_image[..., np.newaxis]

  dif = np.sum(np.abs(th_now_image - th_before_image)/255.)
  
  before_image = now_image

  return now_image, dif


if len(sys.argv) < 2:
    print("장치id를 입력하지 않았습니다.")
    print("% python sender.py 1234")
    sys.exit()
else :
    deviceId = sys.argv[1]
    
if len(deviceId) < 3:
    print("장치id를 4자리이상 7자리 미만의 숫자를 입력 하세요")
    sys.exit()
elif len(deviceId) > 6:
    print("4자리이상 7자리 미만의 숫자를 입력 하세요")
    sys.exit()
    
print("deviceId",deviceId)

while True:
    try:
        response = requests.get('https://www.google.com', timeout=5)
        break
    except:
        pass
    time.sleep(5)


print('stft device id read threshold file')

thold = read_stft_threshold(deviceId)
print('threshold=', thold)

rec_version = read_stft_update(deviceId)
print('rec_version=', rec_version)


int_recversion = int(rec_version)
int_sourceversion = int(source_version)

if int_recversion > int_sourceversion :
    print("update")
    cmdDelete = "rm -rf mill_image_api_test"
    resultDelete = subprocess.run(cmdDelete, shell=True)
    time.sleep(1)
    cmdClone = "git clone https://github.com/Mill-Corporation/mill_image_api_test.git"
    resultClone = subprocess.run(cmdClone, shell=True)
    time.sleep(5)
    cmdCopy = "cp -f ./mill_image_api_test/client.py ."
    resultCopy = subprocess.run(cmdCopy, shell=True)
    time.sleep(1)
    #cmdReboot = "sudo reboot"
    #resultReboot = subprocess.run(cmdReboot, shell=True)

frames = []
f_id = []
for _ in range(FRAME_LENGTH):
    if len(frames) == 0:
        before_frame = None
    else:
       before_frame = frames[-1]
    print(_)
    frame, dif = capture(before_frame)
    frames.append(frame)

    fileName = deviceId + "_" +  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f_id.append(fileName)
    print(fileName)

    time.sleep(1)
print('warmup end')

while True:
    os.makedirs(IMG_DIR, exist_ok=True)
    if len(os.listdir(f'{IMG_DIR}')) > 50000:
        shutil.rmtree(IMG_DIR)

    frame, dif = capture(frames[-1])
    
    frames = frames[1:]
    frames.append(frame)

    fileName = deviceId + "_" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f_id = f_id[1:]
    f_id.append(fileName)
    print(fileName)
    
    # print(dif)

    if dif > thold:#default : 960(5%)
        cv2.imwrite(f'{IMG_DIR}/{f_id[0]}.jpg', frames[0])
        cv2.imwrite(f'{IMG_DIR}/{f_id[1]}.jpg', frames[1])
        cv2.imwrite(f'{IMG_DIR}/{f_id[2]}.jpg', frames[2])
        time.sleep(1)
        for i in range(FRAME_LENGTH):
           with open(f'{IMG_DIR}/{f_id[i]}.jpg', "rb") as f:
            im_bytes = f.read()
            
            im_b64 = base64.b64encode(im_bytes).decode("utf8")
            # print(im_b64)
            headers = {'Accept': 'application/json'}

            payload = {"image": im_b64, "fname": f_id[i]}

            response = requests.post(api, data=payload, headers=headers)

            try:
                data = response.json()
                
                print('data', data)                
            # except requests.exceptions.RequestException:
            except Exception as e:
                print('except', e)


    time.sleep(1)


