import shutil

from src.ballandhoop.videostream import VideoStream
import time
import os
import cv2


def savePictures(dir_name, amount: int = 10, fps=60, resolution_no: int = 0, wb_gains=None):
    dir_base = "storage/faker/"
    dir_name = dir_base + dir_name + "/"
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)

    vid = VideoStream(resolution_no=int(resolution_no), framerate=fps, wb_gains=wb_gains, as_hsv=False)
    idx = 0
    buffer = []
    for frame in vid:
        buffer.append(frame)
        idx = idx + 1
        if idx > int(amount):
            break
    vid.close()
    print('Got ' + str(int(vid.fps.fps())) + " fps in " + str(vid.fps.elapsed()) + "s")
    for i, f in enumerate(buffer):
        # this function can be too slow for doing it inside the top loop (?)
        cv2.imwrite(dir_name + str(i) + '.png', f)
