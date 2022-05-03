import os
from time import sleep

from picamera import PiCamera

dirName = input("Base dir name: ")
dirPath = "storage/hoop-calibration/" + dirName + "/"
if not os.path.exists(dirPath):
    os.mkdir("storage/hoop-calibration/" + dirName + "/")

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 60

camera.start_recording(dirPath + 'vid.h264')
sleep(10)
camera.stop_recording()