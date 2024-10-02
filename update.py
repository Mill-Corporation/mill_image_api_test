import cv2

camera = cv2.VideoCapture(0, cv2.CAP_V4L)
ret, image = camera.read()
if ret == True:
    cv2.imwrite('image_smaple.jpg', image)
else:
    print('카메라로부터 프레임을 캡쳐할 수 없습니다.')
camera.release()
