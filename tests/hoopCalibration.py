# make parent folder / package accessible 
import repackage
repackage.up()
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from src.chessboard.utils import load_coefficients
import time
import cv2
import numpy as np

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
# lower bound and upper bound for Orange color
lower_bound = np.array([10, 20, 20])
upper_bound = np.array([30, 255, 255])
# find the colors within the boundaries
mask = cv2.inRange(hsv, lower_bound, upper_bound)

kernel = np.ones((7, 7), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
segmented_img = cv2.bitwise_and(image_undis, image_undis, mask=mask)
filename = input("File name without .png: ")
pathRaw =  "storage/hoop-calibration/" + filename + "-raw.png"
pathUndis =  "storage/hoop-calibration/" + filename + "-undistorted.png"
path = "storage/hoop-calibration/" + filename + ".png"
# save the frame
cv2.imwrite(pathRaw, image_raw)
cv2.imwrite(pathUndis, image_undis)
cv2.imwrite(path, segmented_img)
print("Saved")
