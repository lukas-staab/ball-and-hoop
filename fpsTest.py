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
ap.add_argument("-e", "--encode", type=int, default=0,
                help="Encoding (yuv, bgr)")
ap.add_argument("-r", "--rotate", type=int, default=0,
                help="Rotate multiple of 90 degree")
sizes = {
    0: (160, 120),
    1: (320, 240),
    2: (640, 480),
    3: (1280, 920),
    4: (1600, 1200),
}
encodings = {
   0: 'yuv',
   1: 'bgr'
}
rotates = {
    1: cv2.cv2.ROTATE_90_CLOCKWISE,
    2: cv2.cv2.ROTATE_180,
    3: cv2.cv2.ROTATE_90_COUNTERCLOCKWISE,
}

args = vars(ap.parse_args())
# initialize the camera and stream
camera = PiCamera()
camera.resolution = sizes.get(args['size'])
camera.framerate = args['num_frames']
# rawCapture = PiRGBArray(camera, size=frameSize)
encoding = encodings[args['encode']]
if encoding == 'yuv':
    rawCapture = PiYUVArray(camera)
else:
    rawCapture = PiRGBArray(camera)

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
start_time = time.time()
fps = FPS().start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format=encoding, use_video_port=True):
    # and occupied/unoccupied text
    image = frame.array
    if args['rotate'] != 0:
        image = cv2.rotate(image, rotates[args['rotate']])
    fps.update()
    if args['display'] != -1:
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
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
