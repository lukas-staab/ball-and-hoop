# make parent folder / package accessible
import repackage
repackage.up()
# import the necessary packages
from src.ballandhoop import ImageComposer
from src.PiVideoStream import PiVideoStream
import cv2
import os
import numpy as np


with PiVideoStream(framerate=60) as vid:
    dirName = input("Base dirName name: ")
    os.makedirs("storage/hoop-calibration/" + dirName + "/", exist_ok=True)
    # due to the user input lag, this is kind of random which picture is picked
    im = ImageComposer(vid.read(), do_undistortion=False, do_blurring=False,
                       debug_path="storage/hoop-calibration/" + dirName)
    hsv = im.get_hsv()

    for x in range(0, 255, 5):
        # lower bound and upper bound for Orange color
        lower_bound = np.array([x, 20, 20])
        upper_bound = np.array([(x+20) % 255, 255, 255])
        # find the colors within the boundaries
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        segmented_img = cv2.bitwise_and(im.image(), im.image(), mask=mask)

        path = "storage/hoop-calibration/" + dirName + "/" + str(x) + "-" + str((x+20) % 255) + ".png"
        cv2.imwrite(path, segmented_img)
    im.save()
    print("Saved")
