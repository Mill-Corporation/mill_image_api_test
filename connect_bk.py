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
import subprocess
from gpiozero import LED


deviceId = '3003'
cur_version = 1111
api_connect = 'http://115.68.41.205:5000/networkconnect'



def read_booting():
    print('read_booting')
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

    file_path = f'/home/mill/imageUpload/reboot.json'
    
    try:
        with stft.open(file_path, 'r') as file:
            file_content = file.read()
        json_data = json.loads(file_content.decode('utf-8'))
        booting = json_data.get(deviceId)

        if booting == 1:
            print("network system reboot")
            cmdReboot = "sudo shutdown -r now"
            resultCapture = subprocess.run(cmdReboot, shell=True)
          
    except Exception as e:
        print('network stft error', str(e))
        cmdReboot = "sudo shutdown -r now"
        resultCapture = subprocess.run(cmdReboot, shell=True)
    finally:
        stft.close()
        transport.close()



def read_update():
    print('read_update')
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

    file_path = f'/home/mill/imageUpload/update.json'
    
    try:
        with stft.open(file_path, 'r') as file:
            file_content = file.read()
        json_data = json.loads(file_content.decode('utf-8'))
        update_version = json_data.get(deviceId)

        print("cur_version=",cur_version)
        print("update_version=", update_version)
        
        if cur_version < update_version:
            print("git clone")
            cmdReboot = "sudo git clone https://github.com/Mill-Corporation/mill_image_api_test.git"
            resultCapture = subprocess.run(cmdReboot, shell=True)
            time.sleep(8)

            print("cp")
            cmdReboot = "cp -f mill_image_api_test/client.py Lepton/"
            resultCapture = subprocess.run(cmdReboot, shell=True)
            time.sleep(3)
            
            print("rm")
            cmdReboot = "sudo rm -rf mill_image_api_test/"
            resultCapture = subprocess.run(cmdReboot, shell=True)
            time.sleep(3)
            
            print("system reboot")
            cmdReboot = "sudo reboot"
            resultCapture = subprocess.run(cmdReboot, shell=True)
          
    except Exception as e:
        print('network update error', e)
        cmdReboot = "sudo shutdown -r now"
        resultCapture = subprocess.run(cmdReboot, shell=True)
    finally:
        stft.close()
        transport.close()


def send_www():
    print('send_www')
    try:
        response = requests.get('https://www.google.com', timeout=5)
    except:
        #pass
        time.sleep(1)
        cmdReboot = "sudo shutdown -r now"
        resultCapture = subprocess.run(cmdReboot, shell=True)


def send_connect():
    print("send_connect")

    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur_ver = cur_version
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    payload = json.dumps({"deviceid": deviceId, "nowtime": cur_time, "version": cur_ver})

    response = requests.post(api_connect, data=payload, headers=headers, timeout=None)

    try:
        data = response.json()
    
        rebooting = data.get(deviceId)
        print("network deviceid=",deviceId)
        print("network rebooting=",rebooting)
        if rebooting == 1:
            print("network system reboot")
            cmdReboot = "sudo shutdown -r now"
            resultCapture = subprocess.run(cmdReboot, shell=True)
            print(data)  

        print(data)                
    except requests.exceptions.RequestException:
        print(response.text)
        cmdReboot = "sudo shutdown -r now"
        resultCapture = subprocess.run(cmdReboot, shell=True)



while True:
    try:
        send_connect()
        break
    except:
        pass
    time.sleep(5)




while True:
    try:
        print("connect loop program")
        time.sleep(15)
        send_connect()

        time.sleep(15)
        read_update()

        time.sleep(15)
        read_booting()

        time.sleep(15)
        send_www()
        
    except:
        pass
