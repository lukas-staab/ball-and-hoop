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
from src.hoop.hoop import Hoop


dirName = input("Base dir name: ")
dirPath = "storage/hoop-calibration/" + dirName + "/"
if not os.path.exists(dirPath):
    os.mkdir("storage/hoop-calibration/" + dirName + "/")
    print('Take picture from raspi cam')
    # imports only work on raspi
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 90
    rawCapture = PiRGBArray(camera, size=(640, 480))
    [camera_matrix, dist_matrix] = load_coefficients('storage/chessboard-calibration/calibration_chessboard.yml')

    # allow the camera to warmup
    time.sleep(0.1)

    # capture frames from the camera
    camera.capture(rawCapture, format="bgr", use_video_port=True)
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image_raw = rawCapture.array
    image_undis = cv2.undistort(image_raw, camera_matrix, dist_matrix)
    cv2.imwrite(dirPath + "raw.png", image_raw)
    cv2.imwrite(dirPath + "undistorted.png", image_undis)
else:
    print('Take picture from ' + dirPath)
    image_raw = cv2.imread(dirPath + "raw.png")
    image_undis = cv2.imread(dirPath + "undistorted.png")

# convert to hsv colorspace
hsv = cv2.cvtColor(image_undis, cv2.COLOR_BGR2HSV)
# search hoop
hoop = Hoop(hsv)
# prepare output picture
image_result = image_undis.copy()
cv2.circle(image_result, hoop.center, int(hoop.radius), (0, 255, 0), 2)
cv2.line(image_result, hoop.center, np.array(hoop.center - np.array((0, hoop.radius)), int), (255, 53, 184), 2)

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
        cv2.circle(image_result, ball_center, int(ball_radius), (0, 255, 255), 2)
        cv2.circle(image_result, ball_center, 5, (0, 0, 255), -1)
        print(np.array(ball_center) - hoop.center)
        cv2.line(image_result, hoop.center, ball_center, (255, 0, 0), 2)
        deg = hoop.angle_in_hoop(ball_center)
        cv2.putText(image_result, str(round(deg, 2)), (ball_center[0], ball_center[1] - int(1.5 * ball_radius)),
                    fontFace=FONT_HERSHEY_PLAIN, color=(255, 0, 0),
                    fontScale=1)

cv2.imwrite(dirPath + "result.png", image_result)
print("dumped pic saves to dir")

# cv2.imshow('image', image_result)
# waits for user to press any key
# (this is necessary to avoid Python kernel form crashing)
# cv2.waitKey(0)
# closing all open windows
# cv2.destroyAllWindows()
