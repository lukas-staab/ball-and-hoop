# import the necessary packages
from __future__ import print_function


from imutils.video import FPS
from picamera.array import PiYUVArray
from picamera.array import PiRGBArray
from picamera import PiCamera
from PiVideoStream import PiVideoStream
import argparse
import time
import cv2

frameSize = (640, 480)
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--num-frames", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-r", "--resolution", type=int, default=1,
                help="Sizes from 0 to 4, default 1 (320x240)")
ap.add_argument("-e", "--encode", type=int, default=1,
                help="Encoding (yuv, bgr)")
ap.add_argument("-r", "--rotation", type=int, default=0,
                help="Rotate multiple of 90 degree")
# ---------------------------------------------------
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")

args = vars(ap.parse_args())

cam = PiVideoStream(resolution_no=args['resolution'],
                    framerate=args['num_frames'], rotation=args['rotation'], encode=args['encode'])

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
start_time = time.time()
fps = FPS().start()
# capture frames from the camera
while time.time() - start_time > int(args['time']):
    # and occupied/unoccupied text

    image = cam.read()
    if args['display'] != -1:
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
    # show the frame

# stop the timer and display FPS information
fps = cam.fpsIn
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# do a bit of cleanup
cam.stop()
cv2.destroyAllWindows()
