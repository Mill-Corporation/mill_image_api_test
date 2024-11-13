import sys
from api import *
from camera import CAMERA
from sys_cmd import reboot

cur_version = 1112
real_version = 1112
ALIVE_TIME = 30 # send alive in 30s

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

    #wifi check
    start_datetime = datetime.now()
    while True:
        if (datetime.now() - start_datetime).seconds > 120:
            print('reboot')
            reboot()
        if send_connect(deviceId, cur_version, real_version, api_url='camera') == 1:
            break

    # camera_js
    js_camera = request_camera_setting(deviceId)


    camera = CAMERA()
    if js_camera is not None:
        camera.set_camera_option(js_camera)


    #camera warmup
    print('camera warmup')
    f_ids, frames = camera.capture_continue_with_time()
    if f_ids is None:
        print('reboot')
        reboot()
    else:
        for index in range(len(f_ids)):
            status = upload_img(deviceId, f_ids[index], frames[index])
    print('camera warmup end')


    print('main start')
    loopCaptureStatus = 0
    start_datetime = datetime.now()
    boot_datetime = datetime.now()
    while True:
        try:
            now_datetime = datetime.now()

            #run 6h
            if ((now_datetime - boot_datetime).total_seconds()// 3600) % 24 >= 6:
                print('reboot')
                reboot()

            if (now_datetime - start_datetime).total_seconds() > camera.js_camera['camera_capture_cycle']:
                #capture
                f_ids, frames = camera.capture_continue_with_time()
                if f_ids is None:
                    print('reboot')
                    reboot()
                else:
                    for index in range(len(f_ids)):
                        status = upload_img(deviceId, f_ids[index], frames[index])
                start_datetime = now_datetime

            loopCaptureStatus += 1
            if loopCaptureStatus > ALIVE_TIME:
                send_connect(deviceId, cur_version, real_version, api_url='camera')
                loopCaptureStatus = 0

            time.sleep(1)
        except:
            print('reboot')
            reboot()