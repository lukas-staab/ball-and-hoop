# import the necessary packages
import os.path
import time
import cv2
from imutils.video import FPS

class VideoStream:
    resolutions = {
        0: (160, 128),
        1: (320, 240),
        2: (640, 480),
    }

    rotations = {
        1: cv2.ROTATE_90_CLOCKWISE,
        2: cv2.ROTATE_180,
        3: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }

    def __init__(self, resolution_no=2, framerate=30, rotation=0, as_hsv=True, wb_gains=None, faker_path=None):
        resolution = self.resolutions[resolution_no]
        # initialize the camera and stream
        self.is_faked = faker_path is not None
        self.framerate = framerate
        if self.is_faked:
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
                                                         format='rgb',  # this is also needed for hsv
                                                         use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.raw_frame = None
        self.rotation = rotation
        self.fps = FPS()

    def __iter__(self):
        self.fps.start()
        return self

    def __next__(self):
        f = next(self.stream)
        if self.is_faked:
            time.sleep(1 / self.framerate)
        else:
            f = f.array
            self.rawCapture.truncate(0)
        self.fps.update()
        if self.rotation != 0:
            f = cv2.rotate(f, self.rotations[self.rotation])
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
            yield cv2.imread(file)
            idx = idx + 1
            file = faker_path + "/" + str(idx) + ".png"
