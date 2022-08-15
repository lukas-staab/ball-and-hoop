from __future__ import annotations

import os
import shutil

import numpy as np
import cv2
from cv2 import FONT_HERSHEY_PLAIN

from src.chessboard import utils


class ImageComposer:
    camera_matrix = None
    dist_matrix = None
    instance_number = 0

    def __init__(self, image_raw, do_undistortion=True, do_blurring=True, debug_path: str = None):
        self.idx = ImageComposer.instance_number
        ImageComposer._static_init()
        if image_raw is None:
            raise Exception('Cannot work with empty/none image')
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
            if os.path.exists(self.debug_path):
                shutil.rmtree(self.debug_path)
            os.makedirs(debug_path, exist_ok=True)

    def newImage(self):
        self.image_history.append(self.image_history[-1].copy())

    def image(self):
        return self.image_history[-1]

    def plot_hoop(self, hoop: Hoop, color: tuple = (255, 0, 0), thickness=2):
        cv2.circle(self.image(), hoop.center, int(hoop.radius), color, thickness)

    def plot_ball(self, ball: Ball, color_outline: tuple = (0, 255, 0),
                  color_center: tuple = (0, 255, 0)):
        cv2.circle(self.image(), ball.center, ball.radius, color_outline, 2)
        cv2.circle(self.image(), ball.center, 3, color_center, -1)

    def plot_line(self, p1: tuple, p2: tuple, color: tuple = (255, 0, 0), thickness: int = 2):
        cv2.line(self.image(), p1, p2, color, thickness)

    def plot_text(self, text: str, pos: tuple, color: tuple = (255, 0, 0), fontScale=1):
        cv2.putText(self.image(), text, pos, fontFace=FONT_HERSHEY_PLAIN, color=color, fontScale=fontScale)

    def plot_angle(self, hoop: Hoop, ball: Ball):
        self.plot_line(hoop.center, ball.center)
        self.plot_line(hoop.center, ball.center)
        deg = hoop.angle_in_hoop(ball.center)
        self.plot_text(str(round(deg, 2)), (ball.center[0], ball.center[1] - int(1.5 * ball.radius)))

    def apply_undistort(self):
        self.image_history.append(cv2.undistort(self.image_history[-1], self.camera_matrix, self.dist_matrix))

    def apply_blurring(self):
        self.image_history.append(cv2.GaussianBlur(self.image_history[-1], (11, 11), 0))

    def get_hsv(self):
        return cv2.cvtColor(self.image(), cv2.COLOR_BGR2HSV)

    def plot_ball_history(self, pts, color=(0, 0, 255)):
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
        if self.debug_path is None:
            return
        print("Save image History to: " + self.debug_path + str(self.idx) + "/")
        os.makedirs(self.debug_path + str(self.idx) + "/", exist_ok=True)
        for num, img in enumerate(self.image_history, start=0):
            cv2.imwrite(self.debug_path + str(self.idx) + "/" + str(num) + ".png", img)

    @staticmethod
    def _static_init():
        if ImageComposer.instance_number == 0:
            ImageComposer.camera_matrix, ImageComposer.dist_matrix = utils.load_coefficients(
            'storage/chessboard-calibration/calibration_chessboard.yml')
        ImageComposer.instance_number = ImageComposer.instance_number + 1
