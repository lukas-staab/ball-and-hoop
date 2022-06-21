# import the necessary packages
import repackage
repackage.up()
from collections import deque
from src.PiVideoStream import PiVideoStream
import argparse
import time
import cv2
from src.ballandhoop.imageComposer import ImageComposer
from src.ballandhoop.hoop import Hoop


# construct the argument parse and parse the arguments


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-res", "--resolution", type=int, default=1,
                help="Sizes from 0 to 4, default 2 (640x480)")
ap.add_argument("-e", "--encode", type=int, default=2,
                help="Encoding (yuv, bgr)")
ap.add_argument("-rot", "--rotation", type=int, default=0,
                help="Rotate multiple of 90 degree")
# ---------------------------------------------------
ap.add_argument("-d", "--display", type=int, default=0,
                help="Whether or not frames should be displayed")
ap.add_argument("-t", "--time", type=int, default=-1,
                help="Time in seconds")

args = vars(ap.parse_args())

# -----------------
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
col_lower = (100, 86, 6)
col_upper = (120, 255, 255)
buffer = 10
pts = deque(maxlen=buffer)
idx = 0
with PiVideoStream(resolution_no=args['resolution'], framerate=args['fps'], rotation=args['rotation'],
                   encode=args['encode'], awb=(1.80, 1.18)) as cam:
    # allow the camera to warmup and start the FPS counter
    time.sleep(0.25)
    # capture frames from the camera
    while idx < 5:
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        raw = cam.read()
        img = ImageComposer(raw, do_undistortion=False, do_blurring=False, debug_path='storage/tracking/')
        hoop = Hoop.create_from_image(img)
        if hoop is not None:
            ball = hoop.find_ball(100, 120)
            img.plot_hoop(hoop)
            if ball is not None:
                img.plot_ball(ball)
                pts.appendleft(ball.center)
                img.plot_ball_history(pts)
            img.save()
        idx += 1



