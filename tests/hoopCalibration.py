# make parent folder / package accessible
import os

import repackage

repackage.up()
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from src.chessboard.utils import load_coefficients
import time
import cv2
import numpy as np
import imutils as imutils

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

# convert to hsv colorspace
hsv = cv2.cvtColor(image_undis, cv2.COLOR_BGR2HSV)
dirName = input("Base dir name: ")
os.makedirs("storage/hoop-calibration/" + dirName + "/", exist_ok=True)

# lower bound and upper bound for Orange color
lower_bound = np.array([170, 20, 20])
upper_bound = np.array([190, 255, 255])
# find the colors within the boundaries
mask = cv2.inRange(hsv, lower_bound, upper_bound)
mask = cv2.erode(mask, None, iterations=2)
mask = cv2.dilate(mask, None, iterations=2)

cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

centers = []
image_result = image_undis.copy()
for c in cnts:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    centers.append(center)
    # only proceed if the radius meets a minimum size
    if radius > 5:
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        cv2.circle(image_result, (int(x), int(y)), int(radius),
                   (0, 255, 255), 2)
        cv2.circle(image_result, center, 5, (0, 0, 255), -1)

dirPath = "storage/hoop-calibration/" + dirName + "/"
cv2.imwrite(dirPath + "raw.png", image_raw)
cv2.imwrite(dirPath + "undistorted.png", image_undis)
cv2.imwrite(dirPath + "masked.png", mask)
cv2.imwrite(dirPath + "foundPoints.png", image_result)
print("Saved")
print("Found Circles:")
print(centers)
