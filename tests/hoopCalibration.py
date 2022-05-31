# make parent folder / package accessible
import repackage
repackage.up()
# import the necessary packages
from src.chessboard.utils import load_coefficients
from cv2 import FONT_HERSHEY_PLAIN
import numpy as np
import time
import cv2
import os
from src.hoop.Hoop import Hoop
from src.hoop.ImageComposer import ImageComposer


dirName = input("Base dir name [00]:") or "00"
dirPath = "storage/hoop-calibration/" + dirName + "/"
if not os.path.exists(dirPath):
    os.makedirs("storage/hoop-calibration/" + dirName + "/", exist_ok=True)
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
imc.save()
# convert to hsv colorspace
# search hoop
hoop = Hoop(imc)
hoop.find_hoop()
imc.plot_hoop(hoop)
imc.save()
# prepare output picture

# search balls in colors
ball_colors = (
    #(0, 20),  # red
    #(15, 35),  # yellow
    #(90, 100),  # light blue
    (100, 120),  # dark blue
)

for (col_low, col_up) in ball_colors:
    ball_center, ball_radius, ball_deg = hoop.find_ball(col_low, col_up)
    # only proceed if the radius meets a minimum size
    if ball_radius > 10:
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        imc.plot_ball(ball_center, ball_radius)
        print(np.array(ball_center) - hoop.center)
        imc.plot_line((hoop.center, ball_center))
        deg = hoop.angle_in_hoop(ball_center)


imc.save()
print("dumped pic saves to dir")

# cv2.imshow('image', image_result)
# waits for user to press any key
# (this is necessary to avoid Python kernel form crashing)
# cv2.waitKey(0)
# closing all open windows
# cv2.destroyAllWindows()
