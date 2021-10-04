# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 90
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)

name = input("Filename: ")

# capture frames from the camera
camera.capture(rawCapture, format="bgr", use_video_port=True)
# grab the raw NumPy array representing the image, then initialize the timestamp
# and occupied/unoccupied text
image = rawCapture.array
filename = "storage/chessboard-calibration/" + name + ".png"
# save the frame
cv2.imwrite(filename, image)
print("Saved")

