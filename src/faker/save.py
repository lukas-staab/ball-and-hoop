import shutil

from src.ballandhoop.videostream import VideoStream
import time
import os
import cv2


def savePictures(dir_name, resolution_no=2, wb_gains=None, amount=5, fps=60):
    dir_base = "storage/faker/"
    dir_name = dir_base + dir_name
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)

    vid = VideoStream(resolution_no=resolution_no, framerate=fps, wb_gains=wb_gains, as_hsv=False)
    idx = 0
    for frame in vid:
        # first pic is sometimes off color
        if idx == 0:
            continue
        cv2.imwrite(dir_name + "/" + str(idx) + '.png', frame)
        idx = idx + 1
        if idx > amount:
            break
    vid.close()
