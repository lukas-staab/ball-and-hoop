import argparse
import repackage
import cv2
repackage.up()
from src.ballandhoop.imageComposer import ImageComposer


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filepath", type=str, required=True)
# ---------------------------------------------------
args = vars(ap.parse_args())

pic = cv2.imread(args['filepath'])
imc = ImageComposer(pic)

cv2.imshow('HSV', imc.get_hsv())
key = cv2.waitKey(0)

