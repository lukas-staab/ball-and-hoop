import os
import numpy as np
import cv2
from src.chessboard import utils


class ImageComposer:
    camera_matrix, dist_matrix = utils.load_coefficients(
        'storage/chessboard-calibration/calibration_chessboard.yml')

    def __init__(self, image_raw, do_undistortion=True, do_blurring=True, dirPath=None):
        if image_raw is None or image_raw.empty():
            raise Exception('Cannot work with empty/none image')
        self.idx = 0
        self.image_raw = image_raw
        self.image_history = [image_raw]
        if do_undistortion:
            self.apply_undistort()
        if do_blurring:
            self.apply_blurring()
        # append copy of last instance to paint on
        self.image_history.append(self.image_history[-1].copy())
        self.dirPath = dirPath
        if self.dirPath is not None:
            os.makedirs(dirPath, exist_ok=True)

    def image(self):
        return self.image_history[-1]

    def plot_hoop(self, hoop, color=(255, 0, 0), thickness=2):
        cv2.circle(self.image(), hoop.center, hoop.radius, color, thickness)

    def plot_ball(self, ball_center, ball_radius, color_outline=(0, 255, 0), color_center=(0, 255, 0)):
        cv2.circle(self.image(), ball_center, ball_radius, color_outline, 2)
        cv2.circle(self.image(), ball_center, 3, color_center, -1)

    def apply_undistort(self):
        self.image_history.append(cv2.undistort(self.image_history[-1], self.camera_matrix, self.dist_matrix))

    def apply_blurring(self):
        self.image_history.append(cv2.GaussianBlur(self.image_history[-1], (11, 11), 0))

    def get_hsv(self):
        return cv2.cvtColor(self.image(), cv2.COLOR_BGR2HSV)

    def plot_line(self, pts, color=(0, 0, 255)):
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(pts.maxlen / float(i + 1)) * 2.5)
            cv2.line(self.image(), pts[i - 1], pts[i], color, thickness)

    def save(self):
        if self.dirPath is None:
            return
        for num, img in enumerate(self.image_history, start=0):
            cv2.imwrite(self.dirPath + "/" + str(self.idx) + "/" + str(num) + ".png", img)
        self.idx = self.idx + 1
