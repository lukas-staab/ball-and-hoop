import argparse
import os
from time import sleep

from picamera import PiCamera


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-e", "--encode", type=str, default='bgr',
                help="Encoding (yuv, bgr, ...)")
ap.add_argument('-n', "--name", type=str, required=True)
# ---------------------------------------------------
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")

args = vars(ap.parse_args())


fileName = args['name']
dirName = "storage/video/"
if not os.path.exists(dirName):
    os.mkdir(dirName)

with PiCamera as camera:
    camera.resolution = (320, 240)
    camera.framerate = args['fps']
    camera.start_recording(dirName + fileName + '.raw', format=args['encode'])
    camera.wait_recording(args['time'])
    camera.stop_recording()
