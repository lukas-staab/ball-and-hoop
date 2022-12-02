# import the necessary packages
import os.path
import time
import cv2
from imutils.video import FPS


class VideoStream:
    """
    A wrapper for :py:class:`picamera.PiCamera`, so that config file input can be used

    :param resolution_no: the resolution number which can be picked in sensor mode 7
    :param framerate: the framerate, should be between 60 and 90 in sensor mode 7
    :param rotation: the rotation
    :param as_hsv: if output should be hsv or bgr
    :param wb_gains: the white_balancing gains
    :param faker_path: if this directory is set, the camera will not be used, but the pictures saved there. Can be recorded through debug.py
    :param kwargs: catch-all parameter, so more entries in the config do not throw an error
    """
    resolutions = {
        0: (160, 128),
        1: (320, 240),
        2: (640, 480),
    }
    """
    The available resolutions in sensor mode 7.`
    """

    rotations = {
        1: cv2.ROTATE_90_CLOCKWISE,
        2: cv2.ROTATE_180,
        3: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }
    """
    The available rotation numbers
    """

    def __init__(self, resolution_no=1, framerate=60, rotation=0, as_hsv=True, wb_gains=None, faker_path=None, **kwargs):
        resolution = self.resolutions[resolution_no]
        # initialize the camera and stream
        self.is_faked = faker_path is not None
        self.framerate = framerate
        if self.is_faked:
            print('WARN: using video material from "' + faker_path + '", instead of live footage. '
                                                                     'Please change in config if you want live data')
            self.stream = self.faker_stream_generator(faker_path)
        else:
            # assume we are on a raspberry pi then
            from picamera.array import PiRGBArray
            from src.ballandhoop.piHSVArray import PiHSVArray
            from picamera import PiCamera

            self.camera = PiCamera(sensor_mode=7)
            self.camera.resolution = resolution
            self.camera.framerate = framerate

            if type(wb_gains) is tuple or type(wb_gains) is list:
                self.camera.awb_mode = 'off'
                self.camera.awb_gains = wb_gains

            if as_hsv:
                self.rawCapture = PiHSVArray(self.camera, size=resolution)
            else:
                self.rawCapture = PiRGBArray(self.camera, size=resolution)
            self.stream = self.camera.capture_continuous(self.rawCapture,
                                                         format='bgr',  # this is also needed for hsv
                                                         use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.raw_frame = None
        self.rotation = rotation
        self.fps = FPS()

    def __iter__(self):
        """
        Getting the iterator, starting the fps counter
        :return: self
        """
        self.fps.start()
        return self

    def __next__(self):
        """
        Called to get the next frame.

        :return: frame array
        """
        f = next(self.stream)
        if not self.is_faked:
            # reset pointer to first place (just to be sure)
            self.rawCapture.seek(0)
            # copy frame
            f = f.array.copy()
            # reset pointer to first place (this usually should have been enough)
            self.rawCapture.seek(0)
            # delete content of frame
            self.rawCapture.truncate(0)
        self.fps.update()
        # rotate frame if wanted
        if self.rotation != 0:
            f = cv2.rotate(f, self.rotations[self.rotation])
        # return frame
        return f

    def close(self):
        self.fps.stop()
        if not self.is_faked:
            self.stream.close()
            self.rawCapture.close()
            self.camera.close()

    def faker_stream_generator(self, faker_path):
        idx = 1  # 0th pic is sometimes weird
        file = faker_path + "/" + str(idx) + ".png"
        while os.path.isfile(file):
            yield cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2HSV)
            idx = idx + 1
            file = faker_path + "/" + str(idx) + ".png"
