# make parent folder / package accessible
from importlib.util import find_spec

import repackage

repackage.up()
# import the necessary packages
import time
import argparse
import cv2
import os
from src.ballandhoop.hoop import Hoop
from src.ballandhoop.imageComposer import ImageComposer

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--rotation", type=int, default=0,
                help="Rotate multiple of 90 degree")
ap.add_argument('-l', "--lowercol", type=int, nargs=3, default=(150, 20, 20))
ap.add_argument('-u', "--uppercol", type=int, nargs=3, default=(190, 255, 255))
# ---------------------------------------------------
args = vars(ap.parse_args())

dirPath = "storage/hoop-calibration/"
os.makedirs(dirPath, exist_ok=True)

if not find_spec('picamera') is not None:
    print('Take picture from raspi cam')
    # imports only work on raspi
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 90
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # allow the camera to warmup
    time.sleep(0.1)

    # capture frames from the camera
    camera.capture(rawCapture, format="bgr", use_video_port=True)
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image_raw = rawCapture.array
    cv2.imwrite(dirPath + "raw.png", image_raw)
else:
    print('Take picture from ' + dirPath)
    image_raw = cv2.imread(dirPath + "raw.png")

imc = ImageComposer(image_raw, do_blurring=False, do_undistortion=True, debug_path=dirPath)
# convert to hsv colorspace
# search hoop
hoop = Hoop.create_from_image(imc, args['lowercol'], args['uppercol'])
if hoop is None:
    imc.save()
    print("No hoop found")
    exit(1)
imc.plot_hoop(hoop)
# prepare output picture

# search balls in colors
ball_colors = (
    # (0, 20),  # red
    # (15, 35),  # yellow
    # (90, 100),  # light blue
    (100, 120),  # dark blue
)

for (col_low, col_up) in ball_colors:
    ball = hoop.find_ball(col_low, col_up)
    # only proceed if the radius meets a minimum size
    if ball is not None and ball.radius > 10:
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        imc.plot_ball(ball)
        imc.plot_angle(hoop, ball)

imc.save()
print("dumped pic saves to dirName")

# cv2.imshow('image', image_result)
# waits for user to press any key
# (this is necessary to avoid Python kernel form crashing)
# cv2.waitKey(0)
# closing all open windows
# cv2.destroyAllWindows()
