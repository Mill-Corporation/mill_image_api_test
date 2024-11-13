from datetime import datetime
import json
import requests
import base64
from sys_cmd import reboot
import cv2
import time

#url
api_network_connect = 'http://115.68.41.205:5050/networkconnect'
api_camera_connect = 'http://115.68.41.205:5050/cameraconnect'
api_camerasetting = 'http://115.68.41.205:5050/camerasetting'
api_upload = 'http://115.68.41.205:8082/file/upload'

def send_connect(deviceId, cur_version, real_version, api_url='network', max_request_count=3):
	'''
	2024.10.30 ADK
	- request
	add : timeout
		  retry mechanism on request fail
	'''
	print('func send_connect')
	if api_url == 'network':
		api_connect = api_network_connect
	elif api_url == 'camera':
		api_connect = api_camera_connect
	cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	cur_ver = cur_version
	real_ver = real_version
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	payload = json.dumps({"deviceid": deviceId, "nowtime": cur_time, "version": cur_ver, "realverion": real_ver})

	for _ in range(max_request_count):
		try:
			response = requests.post(api_connect, data=payload, headers=headers, timeout=5)
			data = response.json()
			rebooting = data.get(deviceId)
			print("send_connect deviceid=",deviceId)
			print("send_connect rebooting=",rebooting)
			if rebooting == 1:
				print('send_connect rebooting')
				reboot()

			print(data)
			return 1
		except Exception as e:
			print('except', e)
			time.sleep(1)
	return -1

def upload_img(devicd_id, fileName, img, img_type='.jpg', max_request_count=3):
	'''
	2024.10.30 ADK
	- request
	add : timeout
		  retry mechanism on request fail

	- img convert
	now :    img(file) > base64
	change : img(np) > base64
	'''
	print('func send_img')
	#img convert
	_, im_bytes = cv2.imencode(img_type, img)
	im_b64 = base64.b64encode(im_bytes).decode("utf8")
	headers = {'Accept': 'application/json'}
	payload = {"image": im_b64, "fname": f'{devicd_id}_{fileName}'}

	# retry mechanism on request fail
	for _ in range(max_request_count):
		try:
			response = requests.post(api_upload, data=payload, headers=headers, timeout=5)
			data = response.json()
			print('send_img data', data)
			return 1
		except Exception as e:
			print('except', e)
			time.sleep(1)
	return -1

def request_camera_setting(deviceId, max_request_count=3):
	'''
	2024.10.30 ADK
	- request camera setting
	{
    "1001": {
        "camera_frame_length" : 3,
        "camera_capture_cycle": 3,
        "camera_capture_delay" : 2,
        "camera_rotate" : -1,
        "camera_capture_timeout" :20
        }
    }
	'''

	print('func request_camera_setting')
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	payload = json.dumps({"deviceid": deviceId})
	for _ in range(max_request_count):
		try:
			response = requests.post(api_camerasetting, data=payload, headers=headers, timeout=5)
			data = response.json()
			print("data=",data)
			if deviceId not in data:
				return {}
			camera_js = data[deviceId]
			return camera_js
		except Exception as e:
			print('except', e)
			time.sleep(1)
	return {}