# import the necessary packages
from importlib.util import find_spec
import threading
import time
import cv2
from imutils.video import FPS

if find_spec('picamera') is not None:
    from picamera.array import PiRGBArray
    from picamera.array import PiYUVArray
    from picamera import PiCamera


class PiVideoStream:
    resolutions = {
        0: (160, 128),
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

    def __init__(self, resolution_no=1, framerate=30, rotation=0, encode=1, debug_path=None):
        self.debug_path = debug_path
        resolution = self.resolutions[resolution_no]
        # initialize the camera and stream
        self.isPi = find_spec('picamera') is not None
        self.framerate = framerate
        if self.isPi:
            self.camera = PiCamera()
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            if self.encodings[encode] == 'bgr':
                self.rawCapture = PiRGBArray(self.camera, size=resolution)
            else:
                self.rawCapture = PiYUVArray(self.camera, size=resolution)
            self.stream = self.camera.capture_continuous(self.rawCapture,
                                                         format=self.encodings[encode],
                                                         use_video_port=True)
        else:
            self.stream = self.faker_stream_generator()
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.raw_frame = None
        self.rotation = rotation
        self.stopped = False
        self.closed = False
        self.fpsIn = FPS()
        self.fpsOut = FPS()

    def start(self):
        # start the thread to read frames from the video stream
        self.fpsIn = self.fpsIn.start()
        self.fpsOut = self.fpsOut.start()
        print('Try to start cam...')
        threading.Thread(target=self.update, args=()).start()
        return self

    def __enter__(self):
        self.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        print('Cam is running!')
        try:
            for f in self.stream:
                # grab the frame from the stream and clear the stream in
                # preparation for the next frame
                if f is not None:
                    if self.isPi:
                        self.raw_frame = f.array
                        self.rawCapture.truncate(0)
                    else:
                        self.raw_frame = f
                        time.sleep(1 / self.framerate)
                    self.fpsIn.update()
                # if the thread indicator variable is set, stop the thread
                # and resource camera resources
                if self.stopped:
                    print('Cam tries to close resources...')
                    self.stream.close()
                    self.rawCapture.close()
                    self.camera.close()
                    self.fpsIn.stop()
                    self.closed = True
                    print('All resources closed')
                    return
        except:
            if self.isPi:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
            self.fpsIn.stop()
            self.closed = True

    def read(self):
        # return the frame most recently read
        self.fpsOut.update()
        frame = self.raw_frame
        if self.rotation != 0:
            frame = cv2.rotate(frame, self.rotations[self.rotation])
        return frame

    def stop(self):
        # indicate that the thread should be stopped
        print('Cam is stopping...')
        self.stopped = True
        self.fpsOut.stop()
        while not self.closed:
            time.sleep(0.1)
        print('Cam is stopped')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def print_stats(self):
        if not self.stopped:
            print("[ERROR] thread not closed (yet)")
            return
        print("[IN] elasped time: {:.2f}".format(self.fpsIn.elapsed()))
        print("[IN] approx. FPS: {:.2f}".format(self.fpsIn.fps()))
        print("[OUT] elasped time: {:.2f}".format(self.fpsOut.elapsed()))
        print("[OUT] approx. FPS: {:.2f}".format(self.fpsOut.fps()))

    def faker_stream_generator(self):
        cap = cv2.VideoCapture('fetch/rpi2.lan/video/vid1vid.h264')
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                yield frame
            else:
                break
        cap.release()
