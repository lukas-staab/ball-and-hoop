import numpy as np
import repackage
repackage.up()
from src.ballandhoop.imageComposer import ImageComposer
from src.ballandhoop.videostream import VideoStream
from src.ballandhoop.hoop import Hoop
import time
import cv2


cam = VideoStream()
cam.start()
time.sleep(1)
while True:
    f = cam.read()
    img = ImageComposer(f, do_blurring=False, do_undistortion=True)
    try:
        hoop = Hoop(img.get_hsv(), lower_hsv=np.array([170, 20, 20]),)
        print('Found points')
        img.plot_hoop(hoop)
        cv2.imshow('mask', hoop.mask_hoop)
    except RuntimeError:
        pass
    cv2.imshow('F', img.image())
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows()
