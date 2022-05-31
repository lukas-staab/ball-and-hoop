import os
from time import sleep

from picamera import PiCamera

fileName = input("File name: ")
dir = "storage/video/"
if not os.path.exists(dir):
    os.mkdir(dir)

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 60

camera.start_recording(dir + fileName + '.bgr', format='bgr')
sleep(10)
camera.stop_recording()