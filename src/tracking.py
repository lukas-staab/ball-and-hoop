import repackage
repackage.up()
# import the necessary packages
from collections import deque
from src.PiVideoStream import PiVideoStream
import argparse
import time
import cv2

from src.hoop.ImageComposer import ImageComposer
from src.hoop.hoop import Hoop


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
ap.add_argument("-d", "--display", type=int, default=0,
                help="Whether or not frames should be displayed")
ap.add_argument("-t", "--time", type=int, default=-1,
                help="Time in seconds")

args = vars(ap.parse_args())

# -----------------
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
col_lower = (100, 86, 6)
col_upper = (120, 255, 255)
buffer = 10
pts = deque(maxlen=buffer)

try:
    cam = PiVideoStream(resolution_no=args['resolution'],
                        framerate=args['fps'], rotation=args['rotation'], encode=args['encode'])
    cam.start()
    # allow the camera to warmup and start the FPS counter
    time.sleep(1)
    print("[START] counting frames from `picamera` module...")
    start_time = time.time()
    # capture frames from the camera
    print("Searching for the hoop")
    image = cam.read()
    img_composer = ImageComposer(image)
    hoop = Hoop(img_composer.get_hsv())
    print("Loop-Search for the ball")
    while True:
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        raw = cam.read()
        img = ImageComposer(raw, do_undistortion=True, do_blurring=True, dirPath='storage/tracking/')
        center_ball, radius, hoop_deg = hoop.find_ball(img.get_hsv(), 100, 120)
        img.plot_hoop(hoop)
        img.plot_ball(center_ball, radius)
        # update the points queue
        pts.appendleft(center_ball)
        img.plot_line(pts)
        img.save()

        # loop over the set of tracked points, draw a line between last found center points

        # show the frame
        if args['display'] != 0:
            cv2.imshow("Frame", img_composer.image())
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        if args['time'] != -1 and time.time() - start_time > int(args['time']):
            break
        # clear the stream in preparation for the next frame
        # if the `q` key was pressed, break from the loop
except cv2.error as e:
    print("CV2 error: " + e.msg)
except KeyboardInterrupt:
    print('Interrupt detected!')
except Exception as e:
    print(e)
finally:
    # stop the timer and display FPS information
    cam.stop()
    cam.print_stats()
    # do a bit of cleanup
    cv2.destroyAllWindows()



