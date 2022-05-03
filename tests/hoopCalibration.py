# make parent folder / package accessible
import math
import os

import repackage
from cv2 import FONT_HERSHEY_PLAIN

repackage.up()
# import the necessary packages
from src.chessboard.utils import load_coefficients
import time
import cv2
import numpy as np
import imutils as imutils
import circle_fit as cf
from math import atan2


def angle_of_vector(v1, v2):
    x = v1[0] * v2[1] - v1[1] * v2[0]
    y = v1[0] * v2[0] + v1[1] * v2[1]
    return atan2(x, y) / math.pi * 180


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

# lower bound and upper bound for pink color
lower_bound = np.array([150, 20, 20])
upper_bound = np.array([190, 255, 255])
# find the colors within the boundaries
mask_hoop = cv2.inRange(hsv, lower_bound, upper_bound)
mask_hoop = cv2.erode(mask_hoop, None, iterations=2)
mask_hoop = cv2.dilate(mask_hoop, None, iterations=2)
cv2.imwrite(dirPath + "masked-hoop.png", mask_hoop)

cnts = cv2.findContours(mask_hoop.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

centers = []
image_result = image_undis.copy()
for c in cnts:
    # iterate over all contours in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center_ball = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    centers.append(center_ball)
    # only proceed if the radius meets a minimum size
    if radius > 5:
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        cv2.circle(image_result, (int(x), int(y)), int(radius),
                   (0, 255, 255), 2)
        cv2.circle(image_result, center_ball, 3, (0, 0, 255), -1)

xc, yc, r, _ = cf.least_squares_circle(centers)
center_hoop = (int(xc), int(yc))
cv2.circle(image_result, center_hoop, int(r), (0, 255, 0), 2)
cv2.line(image_result, center_hoop, (int(xc), int(yc) - int(r)), (255, 53, 184), 2)
ball_colors = (
    #(0, 20),  # red
    #(15, 35),  # yellow
    #(90, 100),  # light blue
    (100, 120),  # dark blue
)

for (col_low, col_up) in ball_colors:
    mask_ball = cv2.inRange(hsv, (col_low, 20, 20), (col_up, 255, 255))
    mask_ball = cv2.erode(mask_ball, None, iterations=2)
    mask_ball = cv2.dilate(mask_ball, None, iterations=2)
    cv2.imwrite(dirPath + "col-" + str(col_low) + ".png", mask_ball)
    cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center_ball = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        print(center_ball)
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(image_result, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(image_result, center_ball, 5, (0, 0, 255), -1)
            cv2.line(image_result, center_hoop, center_ball, (255, 0, 0), 2)
            print((center_ball[0] - center_hoop[0], center_ball[1] - center_hoop[1]))
            deg = angle_of_vector((0, -r), (center_ball[0] - center_hoop[0], center_ball[1] - center_hoop[1]))
            cv2.putText(image_result, str(round(deg, 2)), (center_ball[0], center_ball[1] - int(1.5 * radius)),
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
