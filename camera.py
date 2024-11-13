import numpy as np
import cv2
from Lepton3 import Lepton3
import time
from datetime import datetime


class CAMERA():
    def __init__(self):
        '''
        camera_frame_length : camera capture count
        camera_capture_cycle : between camera capture time(s)
        camera_capture_delay : between frame capture time(s)
        camera_rotate
            -1  original
            0   cv2.ROTATE_90_CLOCKWISE
            1   cv2.ROTATE_180
            2   cv2.ROTATE_90_COUNTERCLOCKWISE
        camera_capture_timeout : capture timeout(s)
        '''
        self.js_camera = {
            "camera_frame_length": 3,
            "camera_capture_cycle": 120,
            "camera_capture_delay": 5,
            "camera_rotate": -1,
            "camera_capture_timeout": 20
        }

    def set_camera_option(self, js_camera):
        print('set_camera_option')
        for key in self.js_camera:
            if key in js_camera:
                self.js_camera[key] = js_camera[key]
        print(self.js_camera)

    def capture_one(self):
        print('capture_one')
        try:
            with Lepton3('/dev/spidev0.0') as l:
                frame, _ = l.capture(reset_timeout=self.js_camera['camera_capture_timeout'])
            if frame is None:
                print('Failed to capture frame.')
                return None
            cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(frame, 8, frame)
            now_image = np.uint8(frame)
            # now_image shape = (120, 160, 1)
            if self.js_camera['camera_rotate'] != -1:
                now_image = cv2.rotate(now_image, self.js_camera['camera_rotate'])
                # (120, 160, 1) > rotate > (120, 160)
                now_image = now_image[..., np.newaxis]
            return now_image
        except Exception as e:
            print('Failed capture_one.', e)
            return None

    def capture_one_test(self, img_path):
        print('capture_one_test')
        img = self.capture_one()
        cv2.imwrite(img_path, img)

    def capture_continue(self):
        print('capture_continue')
        frames = []
        for i in range(self.js_camera['camera_frame_length']):
            frame = self.capture_one()
            if frame is None:
                return None
            frames.append(frame)
            time.sleep(self.js_camera['camera_capture_delay'])
            print(f'frame index : {i}')
        return frames

    def capture_continue_with_time(self):
        print('capture_continue_with_time')
        frames = []
        f_ids = []
        for i in range(self.js_camera['camera_frame_length']):
            frame = self.capture_one()
            if frame is None:
                return None, None
            fileName = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            f_ids.append(fileName)
            frames.append(frame)
            time.sleep(self.js_camera['camera_capture_delay'])
            print(f'fileName : {fileName}')
        return f_ids, frames

