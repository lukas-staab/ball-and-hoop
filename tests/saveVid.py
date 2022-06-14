import repackage
repackage.up()
import argparse
import os
import time

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


fileName = args['name']
dirName = "storage/video/"
size = (320, 240)

if not os.path.exists(dirName):
    os.mkdir(dirName)

videoWriter = cv2.VideoWriter(dirName + 'outputvid.avi', cv2.VideoWriter_fourcc('I', '4', '2', '0'), args['fps'], size)

with PiVideoStream(resolution_no=1, framerate=args['fps']) as vid:
    vid.start()
    sec = time.time()
    while videoWriter.isOpened() and time.time() - sec > int(args['time']) :
        frame = vid.read()
        videoWriter.write(frame)
    videoWriter.release()