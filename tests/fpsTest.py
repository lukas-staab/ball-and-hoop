# import the necessary packages
from __future__ import print_function
import repackage
repackage.up()
from src.PiVideoStream import PiVideoStream
import argparse
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-res", "--resolution", type=int, default=1,
                help="Sizes from 0 to 4, default 1 (320x240)")
ap.add_argument("-e", "--encode", type=int, default=1,
                help="Encoding (yuv, bgr)")
ap.add_argument("-rot", "--rotation", type=int, default=0,
                help="Rotate multiple of 90 degree")
# ---------------------------------------------------
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")

args = vars(ap.parse_args())

cam = PiVideoStream(resolution_no=args['resolution'],
                    framerate=args['fps'], rotation=args['rotation'], encode=args['encode'])
cam.start()
time.sleep(0.25)
# allow the camera to warmup and start the FPS counter
print("[START] counting frames from `picamera` module...")
start_time = time.time()
# capture frames from the camera
while time.time() - start_time <= int(args['time']):
    # and occupied/unoccupied text
    image = cam.read()
    time.sleep(1/(args['fps']))
    if args['display'] != -1:
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
    # show the frame

# stop the timer and display FPS information
cam.stop()
cam.print_stats()
# do a bit of cleanup
cv2.destroyAllWindows()
