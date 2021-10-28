# import the necessary packages
import time

from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera.array import PiYUVArray
from picamera import PiCamera
from threading import Thread
import cv2


class PiVideoStream:

    resolutions = {
        0: (160, 120),
        1: (320, 240),
        2: (640, 480),
        3: (1280, 920),
        4: (1600, 1200),
    }

    rotations = {
        1: cv2.ROTATE_90_CLOCKWISE,
        2: cv2.ROTATE_180,
        3: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }

    encodings = {
        0: 'yuv',
        1: 'bgr'
    }

    def __init__(self, resolution_no=1, framerate=30, rotation=0, encode=1):
        resolution = self.resolutions[resolution_no]
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        if self.encodings[encode] == 'bgr':
            self.rawCapture = PiRGBArray(self.camera, size=resolution)
        else:
            self.rawCapture = PiYUVArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format=self.encodings[encode], use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.rotation = rotation
        self.stopped = False
        self.closed = False
        self.fpsIn = FPS()
        self.fpsOut = FPS()

    def start(self):
        # start the thread to read frames from the video stream
        self.fpsIn = self.fpsIn.start()
        self.fpsOut = self.fpsOut.start()
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            img = f.array
            if self.rotation != 0:
                img = cv2.rotate(img, self.rotations[self.rotation])
            self.frame = img
            self.rawCapture.truncate(0)
            self.fpsIn.update()
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                self.fpsIn.stop()
                self.closed = True
                return

    def read(self):
        # return the frame most recently read
        self.fpsOut.update()
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.fpsOut.stop()
        while not self.closed:
            time.sleep(1)

    def print_stats(self):
        if not self.stopped:
            print("[ERROR] thread not closed (yet)")
            return
        print("[IN] elasped time: {:.2f}".format(self.fpsIn.elapsed()))
        print("[IN] approx. FPS: {:.2f}".format(self.fpsIn.fps()))
        print("[OUT] elasped time: {:.2f}".format(self.fpsOut.elapsed()))
        print("[OUT] approx. FPS: {:.2f}".format(self.fpsOut.fps()))

