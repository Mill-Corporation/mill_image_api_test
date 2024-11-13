import io
import json
import base64
import logging
import os
import zipfile
from flask import Flask, request, jsonify, abort, render_template, Response
from flask import send_file
import numpy as np
import time
from PIL import Image
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)



@app.route('/1')
def init():
    return render_template("info.html")
    
@app.route('/status-list')
@app.route('/status-list1')
def status_list():
    # HTML 페이지에 데이터를 전달하며 렌더링
    return render_template('status.html')
    
@app.route('/network-status-list')
@app.route('/network-status-list1')
def network_status_list():
    # HTML 페이지에 데이터를 전달하며 렌더링
    return render_template('network-status.html')
    
@app.route('/not_dump')
@app.route('/not_dump1')
def not_dump_status():
    # HTML 페이지에 데이터를 전달하며 렌더링
    return render_template('not-dump.html')

@app.route('/list-status')
@app.route('/list-status1')
def list_status():
    # HTML 페이지에 데이터를 전달하며 렌더링
    return render_template('list-status.html')

@app.route('/list-state')
@app.route('/list-state1')
def list_state():
    # HTML 페이지에 데이터를 전달하며 렌더링
    return render_template('list-state.html')


@app.route('/filenum', methods=['POST'])
@app.route('/filenum1', methods=['POST'])
def setup():
    rdate = request.args['dateType']
    #date = int(rdate)

    rid = request.args["deviceType"]
    #deviceid = int(rid)

    #file = open("setup.txt", "w")
    #file.write(pdate +',' + pdeviceid)

    #print("rdate=",rdate)
    #print("rid=",rid)

    file_path = './upload/' + rdate + '/'
    zip_filename = rid + '_' + rdate + '.zip'

    #print("file_path=", file_path)
    #print("zip_filename=", zip_filename)

    fileNum = 0
    for file in os.listdir(file_path):

        if file.endswith('.jpg'):
            #print("same folder filename=",file)
        
            if rid in file:
                #print("specific ID=",file)
                fileNum += 1
    
    return "<h2>업로드 할수 있는 파일의 갯수는 %d </h2>" % (fileNum)


#http://192.168.32.162:8080/listinfo
@app.route('/listinfo')
@app.route('/listinfo1')
def init_list():
    return render_template("list.html")

@app.route('/listcon', methods=['POST'])
@app.route('/listcon1', methods=['POST'])
def setup1():
    state_dic = {
        '1001': 'off', '1002': 'off', '1003': 'off', '1004': 'off', '1005': 'off',
        '1006': 'off', '1007': 'off', '1008': 'off', '1009': 'off', '1010': 'off', '1011': 'off',
        '2001': 'off', '2002': 'off', '2003': 'off', '2004': 'off', '2005': 'off',
        '2006': 'off', '2007': 'off', '2008': 'off', '2009': 'off', '2010': 'off',
        '2011': 'off', '2012': 'off', '2013': 'off', '2014': 'off', '2015': 'off',
        '2016': 'off', '2017': 'off', '2018': 'off', '2019': 'off', '2020': 'off',
        '2021': 'off', '2022': 'off', '3001': 'off'
    }
    
    rdate = request.form['dateType']
    file_path = './upload/' + rdate + '/'
    
    for key, val in state_dic.items():
        for file in os.listdir(file_path):
            if key in file:
                state_dic[key] = 'on'
    
    # Pretty print the JSON response
    pretty_json = json.dumps(state_dic, indent=4)
    
    return pretty_json, 200, {'Content-Type': 'application/json'}
@app.route("/downinfolist")
@app.route("/downinfolist1")
def downinfolist():
    rdate = request.args['date']
    rid = request.args['deviceid']
    print("rdate=",rdate)
    print("rid=",rid)
    file_path = './upload/' + rdate + '/'
    zip_filename = rid + '_' + rdate + '.zip'
    print("file_path=", file_path)
    print("zip_filename=", zip_filename)
    array = []
    fileNum = 0
    for file in os.listdir(file_path):
        if file.endswith('.jpg'):
            #print("same folder filename=",file)
            if rid in file:
                print("specific ID=",file)
                #print("same id filename=",file)
                array.append(file)
                fileNum += 1
    data = {'fileTotal' : fileNum, 'fileList=' : array}
    return jsonify(data)
#http://192.168.32.162:8080/downfile?date=20241010&deviceid=1001
@app.route("/downfile")
@app.route("/downfile1")
def downfile():
    rdate = request.args['date']
    rid = request.args['deviceid']
    print("rdate=",rdate)
    print("rid=",rid)
    file_path = './upload/' + rdate + '/'
    zip_filename = rid + '_' + rdate + '.zip'
    print("file_path=", file_path)
    print("zip_filename=", zip_filename)
    zip_file = zipfile.ZipFile(file_path + zip_filename,'w')
    for file in os.listdir(file_path):
        if file.endswith('.jpg'):
            #print("same folder filename=",file)
            if rid in file:
                print("specific ID=",file)
                zip_file.write(os.path.join(file_path,file), compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    return send_file(file_path + zip_filename, mimetype="text/plain", as_attachment=True)
#http://192.168.32.162:8080/downcsv?folder=20241010&date=2024-10-04&deviceid=1001&time=03:21:56
@app.route("/downcsv")
@app.route("/downcsv1")
def downcsv():
    rfolder = request.args['folder']
    rdate = request.args['date']
    rid = request.args['deviceid']
    rtime = request.args['time']
    print("rdate=",rdate)
    print("rid=",rid)
    print("rtime=",rtime)
    file_path = './upload/' + rfolder + '/'
    img_file_name = rid + "_" + rdate + " " + rtime + ".jpg"
    csv_file_name = rid + "_" + rdate + " " + rtime + ".csv"
    print("ile_path=",file_path)
    print("img_file_name=", img_file_name)
    print("csv_file_name=",csv_file_name)
    im = Image.open(file_path + img_file_name)
    pixels = list(im.getdata())
    pixel_list =[]
    print(len(pixels))
    myArray = np.array(pixels)
    myArray = myArray.astype(int)
    np.savetxt(csv_file_name, myArray, delimiter=", ", newline=" ",fmt='%i')
    return send_file(csv_file_name, mimetype="text/plain", as_attachment=True)
@app.route('/imageupload', methods=['POST'])
@app.route('/imageupload1', methods=['POST'])
def image_upload():
    # print(request.json)
    if not request.json or 'image' not in request.json:
        abort(400)
    # get the base64 encoded string
    im_b64 = request.json['image']
    fname = request.json['fname']
    print('fname=',fname)
    # convert it into bytes
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))
    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))
    img.save(fname,"JPEG")
    # PIL image object to numpy array
    img_arr = np.asarray(img)
    print('img shape', img_arr.shape)
    # process your img_arr here
    # access other keys of json
    # print(request.json['other_key'])
    result_dict = {'output': 'output_key'}
    return result_dict
    

@app.route("/download", methods=['POST'])
@app.route("/download1", methods=['POST'])
def download():
     # form name value
    rdate = request.form.get('targetDate')
    # Downloads 경로 가져오기
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    # Flask의 업로드 경로로 설정
    app.config['UPLOAD_FOLDER'] = downloads_folder
    
    # file_path = './upload/' + rdate + '/'
    file_path = os.path.join('./upload', rdate)

    # ZIP 파일이 이미 존재하면 뒤에 숫자를 붙여서 새로운 이름으로 만듦
    ir_name = 'IR_Image'
    extension = ".zip"
    zip_filename = f"{ir_name}{rdate}{extension}"
    zip_file_path = os.path.join(file_path, zip_filename)

    if not os.path.isdir(file_path):
        return "해당 날짜의 폴더를 찾을 수 없습니다.", 404

    # output.zip 또는 수정된 파일명을 생성
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        for file in os.listdir(file_path):
            if file.endswith('.jpg'):
                zip_file.write(os.path.join(file_path, file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)

    # 생성된 zip 파일을 사용자에게 전송 (다운로드)
    return send_file(zip_file_path, mimetype="application/zip", as_attachment=True, download_name=zip_filename)


















#카메라 상태확인 라즈베리 파이에서 옴
@app.route('/cameraconnect', methods=['POST'])
@app.route('/cameraconnect1', methods=['POST'])
def camera_connect():
    deviceid = request.json['deviceid']
    print('camerastatus_deviceId=', deviceid)
    nowtime = request.json['nowtime']
    print('camerastatus_nowtime=', nowtime)
    
    status_file = './list-state.json'
    
    # 파일이 존재하면 내용을 읽어옴
    if os.path.exists(status_file):
        with open(status_file, 'r', encoding='utf-8') as status_json:
            try:
                status_json_data = json.load(status_json)
            except json.JSONDecodeError:
                status_json_data = {}  # 파일이 깨져 있으면 빈 dict로 초기화
    else:
        status_json_data = {}  # 파일이 없으면 빈 dict로 초기화

    # deviceid에 해당하는 값만 업데이트
    status_json_data[deviceid] = {
        'cameraTime': nowtime
    }

    # 파일에 업데이트된 데이터 기록
    with open(status_file, 'w', encoding='utf-8') as status_json_file:
        json.dump(status_json_data, status_json_file, indent=4, ensure_ascii=False)

    # reboot.json 파일 읽기
    with open('./reboot.json', "r", encoding='utf-8') as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            json_data = {}  # reboot.json 파일이 깨져 있으면 빈 dict로 초기화

    return jsonify(json_data)
    
    
#네트워크 상태확인 라즈베리 파이에서 옴
@app.route('/networkconnect', methods=['POST'])
@app.route('/networkconnect1', methods=['POST'])
def network_connect():
    deviceid = request.json['deviceid']
    print('networkstatus_deviceId=', deviceid)
    nowtime = request.json['nowtime']
    print('networkstatus_nowtime=', nowtime)
    
    status_file = './list-state.json'
    
    # 파일이 존재하면 내용을 읽어옴
    if os.path.exists(status_file):
        with open(status_file, 'r', encoding='utf-8') as status_json:
            try:
                status_json_data = json.load(status_json)
            except json.JSONDecodeError:
                status_json_data = {}  # 파일이 깨져 있으면 빈 dict로 초기화
    else:
        status_json_data = {}  # 파일이 없으면 빈 dict로 초기화

    # deviceid에 해당하는 값만 업데이트
    status_json_data[deviceid] = {
        'networkTime': nowtime
    }

    # 파일에 업데이트된 데이터 기록
    with open(status_file, 'w', encoding='utf-8') as status_json_file:
        json.dump(status_json_data, status_json_file, indent=4, ensure_ascii=False)

    # reboot.json 파일 읽기
    with open('./reboot.json', "r", encoding='utf-8') as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            json_data = {}  # reboot.json 파일이 깨져 있으면 빈 dict로 초기화

    return jsonify(json_data)
    

@app.route('/status')
@app.route('/status1')
def status():
    # JSON 파일 읽기
    file_path = './camera-status.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}
    else:
        json_data = {}

    # JSON 데이터를 반환
    return jsonify(json_data)

@app.route('/network-status')
@app.route('/network-status1')
def network_status():
    # JSON 파일 읽기
    file_path = './network-status.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}
    else:
        json_data = {}

    # JSON 데이터를 반환
    return jsonify(json_data)

@app.route('/not-dump')
@app.route('/not-dump1')
def not_dump_list():
    # JSON 파일 읽기
    file_path = './not-dump-status.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}
    else:
        json_data = {}

    # JSON 데이터를 반환
    return jsonify(json_data)
    

@app.route('/state')
@app.route('/state1')
def state():
    # JSON 파일 읽기
    file_path = './list-state.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}
    else:
        json_data = {}

    # JSON 데이터를 반환
    return jsonify(json_data)


# 서버 실행 함수
def run_server_api():
    app.run(host='0.0.0.0', port=5000, debug=True)

# 메인 엔트리 포인트
if __name__ == "__main__":
    run_server_api()
