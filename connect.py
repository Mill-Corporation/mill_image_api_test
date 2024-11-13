import paramiko
import sys
import subprocess
from sys_cmd import reboot
from api import send_connect
import json
import time
from datetime import datetime

cur_version = 1112
real_version = 1112

def read_update(deviceId):
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
            subprocess.run(cmdReboot, shell=True)
            time.sleep(8)

            print("cp")
            cmdReboot = "cp -rf mill_image_api_test/* mvpc/"
            subprocess.run(cmdReboot, shell=True)
            time.sleep(3)
            
            print("rm")
            cmdReboot = "sudo rm -rf mill_image_api_test/"
            subprocess.run(cmdReboot, shell=True)
            time.sleep(3)
            
            print("system reboot")
            reboot()
          
    except Exception as e:
        print('network update error', e)
        reboot()
    finally:
        stft.close()
        transport.close()


if __name__ == '__main__':
    time.sleep(10)
    if len(sys.argv) < 2:
        print('장치id를 입력하지 않았습니다.')
        print('% python sender.py 1234')
        sys.exit()
    else :
        deviceId = sys.argv[1]

    if len(deviceId) < 3:
        print('장치id를 4자리이상 7자리 미만의 숫자를 입력 하세요')
        sys.exit()
    elif len(deviceId) > 6:
        print('4자리이상 7자리 미만의 숫자를 입력 하세요')
        sys.exit()

    while True:
        try:
            print("connect loop program")

            time.sleep(30)
            # wifi check
            start_datetime = datetime.now()
            while True:
                if (datetime.now() - start_datetime).seconds > 60:
                    print('reboot')
                    reboot()
                if send_connect(deviceId, cur_version, real_version, api_url='network') == 1:
                    break

            time.sleep(30)
            read_update(deviceId)

        except:
            print('reboot')
            reboot()
