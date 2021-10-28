# import the necessary packages
from collections import deque
import imutils as imutils
import utils
import numpy as np
from PiVideoStream import PiVideoStream
import argparse
import time
import cv2


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fps", type=int, default=60,
                help="# of frames to loop over for FPS test")
ap.add_argument("-res", "--resolution", type=int, default=1,
                help="Sizes from 0 to 4, default 1 (320x240)")
ap.add_argument("-e", "--encode", type=int, default=1,
                help="Encoding (yuv, bgr)")
ap.add_argument("-rot", "--rotation", type=int, default=0,
                help="Rotate multiple of 90 degree")
# ---------------------------------------------------
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")
ap.add_argument("-t", "--time", type=int, default=5,
                help="Time in seconds")

args = vars(ap.parse_args())

# -----------------
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
buffer = 10
pts = deque(maxlen=buffer)

[camera_matrix, dist_matrix] = utils.load_coefficients('./calibration_chessboard.yml')


cam = PiVideoStream(resolution_no=args['resolution'],
                    framerate=args['fps'], rotation=args['rotation'], encode=args['encode'])
cam.start()
# allow the camera to warmup and start the FPS counter
time.sleep(0.5)
print("[START] counting frames from `picamera` module...")
start_time = time.time()
# capture frames from the camera
# capture frames from the camera
while True:
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = cam.read()
    undistort = cv2.undistort(image, camera_matrix, dist_matrix)
    blurred = cv2.GaussianBlur(undistort, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # only proceed if at least one contour was found
    center = None
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(undistort, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(undistort, center, 5, (0, 0, 255), -1)
    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(undistort, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame
    if args['display']:
        cv2.imshow("Frame", undistort)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    if time.time() - start_time > int(args['time']):
        break
    # clear the stream in preparation for the next frame
    # if the `q` key was pressed, break from the loop

# stop the timer and display FPS information
cam.stop()
cam.print_stats()
# do a bit of cleanup
cv2.destroyAllWindows()



