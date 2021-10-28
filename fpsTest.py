# import the necessary packages
from __future__ import print_function


from imutils.video import FPS
from picamera.array import PiYUVArray
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import time
import cv2

frameSize = (640, 480)
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")
ap.add_argument("-s", "--size", type=int, default=1,
                help="Sizes from 0 to 4, default 1 (320x240)")
ap.add_argument("-e", "--encode", type=ascii, default="rgb",
                help="Encoding (rgb, yuv, bgr")
sizes = {
    0: (160, 120),
    1: (320, 240),
    2: (640, 480),
    3: (1280, 920),
    4: (1600, 1200),
}
args = vars(ap.parse_args())
# initialize the camera and stream
camera = PiCamera()
camera.resolution = sizes.get(args['size'])
camera.framerate = args['num_frames']
# rawCapture = PiRGBArray(camera, size=frameSize)
if args['encode'] == 'yuv':
    rawCapture = PiYUVArray(camera)
else:
    rawCapture = PiRGBArray(camera)

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
start_time = time.time()
fps = FPS().start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format=args['encode'], use_video_port=True):
    # and occupied/unoccupied text
    image = frame.array
    fps.update()
    # show the frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if time.time() - start_time > int(args['time']):
        break

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# do a bit of cleanup
cv2.destroyAllWindows()
rawCapture.close()
camera.close()
