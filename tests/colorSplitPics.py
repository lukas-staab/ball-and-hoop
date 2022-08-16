# make parent folder / package accessible
import argparse

import repackage
repackage.up()
# import the necessary packages
from src.ballandhoop import ImageComposer

import cv2
import os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filepath", type=str, required=False)
ap.add_argument("-l", "--lowerBound", type=int, required=False, default=20)
ap.add_argument("-u", "--upperBound", type=int, required=False, default=255)
# ---------------------------------------------------
args = vars(ap.parse_args())

image = None
storagePath = "storage/col-split/"

if 'filepath' in args and len(args['filepath']) > 0:
    print('Take pic from file')
    image = cv2.imread(args['filepath'])
else:
    # has to be on rpi
    print('Take pic from cam')
    from src.ballandhoop.videostream import PiVideoStream
    from src.ballandhoop.whiteBalancing import WhiteBalancing
    gains = WhiteBalancing(verboseOutput=True).calculate()
    with PiVideoStream(framerate=60, awb=gains) as vid:
        image = vid.read()

dirName = input("Base dirName name: ")
os.makedirs(storagePath + dirName + "/", exist_ok=True)
# due to the user input lag, this is kind of random which picture is picked
im = ImageComposer(image, do_undistortion=False, do_blurring=False,
                   debug_path=storagePath + dirName)
hsv = im.get_hsv()

for x in range(0, 255, 5):
    # lower bound and upper bound for Orange color
    lower_bound = np.array([x, args['lowerBound'], args['lowerBound']])
    upper_bound = np.array([(x+20) % 255, args['upperBound'], args['upperBound']])
    # find the colors within the boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    segmented_img = cv2.bitwise_and(im.image(), im.image(), mask=mask)

    path = storagePath + dirName + "/" + str(x) + "-" + str((x+20) % 255) + ".png"
    cv2.imwrite(path, segmented_img)
im.save()
print("Saved")
