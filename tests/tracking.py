# import the necessary packages
import repackage
repackage.up()
from collections import deque
from src.ballandhoop.videostream import VideoStream
import argparse
import time
from src.ballandhoop.imageComposer import ImageComposer
from src.ballandhoop.hoop import Hoop
from src.ballandhoop.whiteBalancing import WhiteBalancing


# construct the argument parse and parse the arguments


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-res", "--resolution", type=int, default=2,
                help="Sizes from 0 to 4, default 2 (640x480)")
ap.add_argument("-e", "--encode", type=int, default=1,
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
# define the lower and upper boundaries of the
# ball in the HSV color space, then initialize the
# list of tracked points
buffer = 10
pts = deque(maxlen=buffer)
idx = 0

gains = WhiteBalancing(verboseOutput=True).calculate()

with VideoStream(resolution_no=args['resolution'], framerate=args['fps'], rotation=args['rotation'],
                 encode=args['encode'], awb=gains) as cam:
    # allow the camera to warmup and start the FPS counter
    time.sleep(0.25)
    # capture frames from the camera

    hoop = None
    while idx < 5:
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        raw = cam.read()
        img = ImageComposer(raw, do_undistortion=False, do_blurring=False, debug_path='storage/tracking/')
        if hoop is None:
            hoop = Hoop.create_from_image(img)
            if hoop is None:
                img.save()
                raise Exception('Ring kann nicht erzeugt werden - kann im Bild nicht gefunden werden')
        ball = hoop.find_ball(100, 120)
        # plot after ball search
        img.plot_hoop(hoop)
        if ball is not None:
            img.plot_ball(ball)
            pts.appendleft(ball.center)
            img.plot_ball_history(pts)
        img.save()
        idx += 1



