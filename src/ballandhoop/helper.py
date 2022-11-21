import os
import shutil

import cv2


def get_bgr_picture(faker_path:str = None, wb_gains=None):
    """ If faker_path is given, return the picture in path, otherwise take a picture from pi cam """
    if faker_path is not None:
        print("WARNING: Taking a virtual picture from file, not from cam: " + faker_path)
        return cv2.imread(faker_path)
    else:
        # no fake picture given. expecting to be on a raspberry pi
        import picamera.array
        camera = picamera.PiCamera(sensor_mode=7)
        camera.resolution = (320, 240)
        camera.awb_mode = 'off'
        camera.awb_gains = wb_gains
        output = picamera.array.PiRGBArray(camera)
        camera.capture(output, format='bgr', use_video_port=True)
        if output.array.shape[1] == 0 or output.array.shape[2] == 0:
            raise Exception('Pi Camera returned an empty picture, please check your cam config')
        return output.array


def get_hsv_picture(faker_path:str = None):
    """ See @get_bgr_picture - but transformed to HLS Colors """
    return cv2.cvtColor(get_bgr_picture(faker_path), cv2.COLOR_BGR2HSV)

def reset_content_of_dir(dir_name : str):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
