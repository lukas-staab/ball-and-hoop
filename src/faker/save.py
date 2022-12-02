from src.ballandhoop.videostream import VideoStream
import shutil
import os
import cv2


def savePictures(dir_name, amount: int = 10, fps: int = 60, resolution_no: int = 1, wb_gains=None):
    """
    Saves multiple video like images with ascending file names in a given folder, starting with 0.png
    :param str dir_name: name of the (new) directory inside `storage/faker/`, directory will be cleared out at the start
    :param amount: amount of pictures taken
    :param fps: the framerate in which the video frames will be fetched
    :param resolution_no: the resolution number which will be used, see :py:property`VideoStream.resolutions`
    :param wb_gains: the gains for white balancing, see :py:class`VideoStream`
    :return:
    """
    dir_base = "storage/faker/"
    dir_name = dir_base + dir_name + "/"
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)

    vid = VideoStream(resolution_no=int(resolution_no), framerate=int(fps), wb_gains=wb_gains, as_hsv=False)
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
