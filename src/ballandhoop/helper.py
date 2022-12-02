import os
import shutil
import cv2


def get_bgr_picture(faker_path: str = None, wb_gains=None):
    """
    Gives a bgr picture from the camera or the image in the `faker_path`

    :param faker_path: a path from which the image will be loaded if given, defaults to None
    :param wb_gains: if not given, it will be auto-calculated, if a picture is taken
    :type wb_gains: tuple
    :return: the image from file or from the camera
    :rtype: numpy.array

    """
    if faker_path is not None:
        print("WARNING: Taking a virtual picture from file, not from cam: " + faker_path)
        return cv2.imread(faker_path)
    else:
        # no fake picture given. expecting to be on a raspberry pi
        import picamera.array
        camera = picamera.PiCamera(sensor_mode=7)
        camera.resolution = (320, 240)
        if wb_gains is not None:
            camera.awb_mode = 'off'
            camera.awb_gains = wb_gains
        else:
            print('[WARN] a picture with white balancing auto is taken - results can widely differ')
        output = picamera.array.PiRGBArray(camera)
        camera.capture(output, format='bgr', use_video_port=True)
        if output.array.shape[1] == 0 or output.array.shape[2] == 0:
            raise Exception('Pi Camera returned an empty picture, please check your cam config')
        return output.array


def get_hsv_picture(faker_path: str = None, wb_gains=None):
    """
    Same as :py:meth:`get_bgr_picture()`, but transformed to HSV colorspace

    :return: the picture as array in HSV color space
    :rtype: numpy.array
    """
    return cv2.cvtColor(get_bgr_picture(faker_path, wb_gains=wb_gains), cv2.COLOR_BGR2HSV)


def reset_content_of_dir(dir_name: str):
    """
    Small helper method which empties all files and folders inside a given folder

    :param dir_name: the path to the folder
    """

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
