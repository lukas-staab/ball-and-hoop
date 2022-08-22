from src.ballandhoop.videostream import VideoStream
import time
import os
import cv2

def saveVideo(file_name, fps=60, length=1, resolution_no=2, wb_gains=None):
    dirName = "storage/faker/"
    file_path = dirName + file_name + '.avi'

    if not os.path.exists(dirName):
        os.mkdir(dirName)

    video_writer = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc('I', '4', '2', '0'),
                                   fps, VideoStream.resolutions[resolution_no])
    vid = VideoStream(resolution_no=resolution_no, framerate=fps, wb_gains=wb_gains, as_hsv=False)
    sec = time.time()
    for frame in vid:
        if video_writer.isOpened() and time.time() - sec <= length:
            break
        video_writer.write(frame)
    video_writer.release()
    vid.close()


def savePicture(file_name, resolution_no=2, wb_gains=None):
    fps = 60
    dirName = "storage/faker/"
    file_base = dirName + file_name
    if not os.path.exists(dirName):
        os.mkdir(dirName)

    vid = VideoStream(resolution_no=resolution_no, framerate=fps, wb_gains=wb_gains)
    idx = 1
    for frame in vid:
        cv2.imwrite(file_base + "-" + idx + '.png', frame)
        idx = idx + 1
        if idx > 5:
            break
    vid.close()
