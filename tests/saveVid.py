import repackage
repackage.up()
import argparse
import os
import time
import cv2

from src.ballandhoop.videostream import VideoStream

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument('-n', "--name", type=str, required=True)
ap.add_argument('-w', "--awb", type=str, default='auto')
# ---------------------------------------------------
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")

args = vars(ap.parse_args())


dirName = "storage/faker/"
fileName = dirName + args['name']
size = (640, 420)

if not os.path.exists(dirName):
    os.mkdir(dirName)

videoWriter = cv2.VideoWriter(fileName + '.avi', cv2.VideoWriter_fourcc('I', '4', '2', '0'), args['fps'], size)
with VideoStream(resolution_no=2, framerate=args['fps']) as vid:
    sec = time.time()
    for frame in vid:
        if videoWriter.isOpened() and time.time() - sec <= int(args['time']):
            break
        videoWriter.write(frame)
    videoWriter.release()