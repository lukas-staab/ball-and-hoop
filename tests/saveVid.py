import repackage
repackage.up()
import argparse
import os
import time
import cv2

from src.PiVideoStream import PiVideoStream

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


dirName = "storage/video/"
fileName = dirName + args['name']
size = (320, 240)

if not os.path.exists(dirName):
    os.mkdir(dirName)

with cv2.VideoWriter(fileName + '.avi', cv2.VideoWriter_fourcc('I', '4', '2', '0'), args['fps'], size) as videoWriter:
    with PiVideoStream(resolution_no=1, framerate=args['fps']) as vid:
        sec = time.time()
        while videoWriter.isOpened() and time.time() - sec > int(args['time']) :
            frame = vid.read()
            videoWriter.write(frame)