import os
import numpy as np
import cv2
from src.chessboard import utils


class ImageComposer:
    camera_matrix, dist_matrix = utils.load_coefficients(
        'storage/chessboard-calibration/calibration_chessboard.yml')

    def __init__(self, image_raw, do_undistortion=True, do_blurring=True, debug_path: str=None):
        if image_raw is None:
            raise Exception('Cannot work with empty/none image')
        self.idx = 0
        self.image_raw = image_raw
        self.image_history = [image_raw]
        if do_undistortion:
            self.apply_undistort()
        if do_blurring:
            self.apply_blurring()
        # append copy of last instance to paint on
        self.newImage()
        if debug_path is not None and not debug_path.endswith('/'):
            debug_path += "/"
        self.debug_path = debug_path
        if self.debug_path is not None:
            os.makedirs(debug_path, exist_ok=True)

    def newImage(self):
        self.image_history.append(self.image_history[-1].copy())

    def image(self):
        return self.image_history[-1]

    def plot_hoop(self, hoop, color=(255, 0, 0), thickness=2):
        cv2.circle(self.image(), hoop.center, int(hoop.radius), color, thickness)

    def plot_ball(self, ball_center, ball_radius, color_outline=(0, 255, 0), color_center=(0, 255, 0)):
        cv2.circle(self.image(), ball_center, int(ball_radius), color_outline, 2)
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

    def get_debug_path(self):
        return self.debug_path + str(self.idx) + "/"

    def save(self):
        if self.debug_path is None:
            return
        for num, img in enumerate(self.image_history, start=0):
            cv2.imwrite(self.debug_path + str(self.idx) + "/" + str(num) + ".png", img)
        self.idx = self.idx + 1
