""" Use this Image painting abstraction only in none Time-relevant settings. It is not optimized on efficiency"""

from __future__ import annotations

import os

import numpy as np
import cv2
from cv2 import FONT_HERSHEY_PLAIN

from src.ballandhoop import helper
from src.chessboard import utils


class Image:
    camera_matrix = None
    dist_matrix = None
    instance_number = 0

    def __init__(self, image_bgr=None, image_hsv=None, debug_path: str = None):
        self.image_bgr = None
        self.image_hsv = None
        if image_bgr is None and image_hsv is None:
            raise Exception('Cannot work with empty/none image')

        if image_bgr is not None:
            self.image_bgr = image_bgr
        else:
            self.image_bgr = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

        if image_hsv is not None:
            self.image_hsv = image_hsv
        else:
            self.image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    def plot_hoop(self, hoop: Hoop, color: tuple = (255, 0, 0), thickness=2):
        pic = cv2.circle(self.image_bgr, hoop.center, int(hoop.radius), color, thickness)
        for i, center in enumerate(hoop.center_dots):
            pic = cv2.circle(pic, center, hoop.radius_dots[i])
        return Image(image_bgr=pic)

    def plot_ball(self, ball: Ball, color_outline: tuple = (0, 255, 0),
                  color_center: tuple = (0, 255, 0)):
        pic = self.image_bgr
        pic = cv2.circle(pic, ball.center, ball.radius, color_outline, 2)
        pic = cv2.circle(pic, ball.center, 3, color_center, -1)
        return Image(image_bgr=pic)

    def plot_line(self, p1: tuple, p2: tuple, color: tuple = (255, 0, 0), thickness: int = 2):
        pic = cv2.line(self.image_bgr, p1, p2, color, thickness)
        return Image(image_bgr=pic)

    def plot_text(self, text: str, pos: tuple, color: tuple = (255, 0, 0), fontScale=1):
        pic = cv2.putText(self.image_bgr, text, pos, fontFace=FONT_HERSHEY_PLAIN, color=color, fontScale=fontScale)
        return Image(image_bgr=pic)

    def plot_angle(self, hoop: Hoop, ball: Ball):
        deg = hoop.angle_in_hoop(ball.center)

        img = self.plot_line(hoop.center, ball.center)
        img = img.plot_line(hoop.center, ball.center)
        img = img.plot_text(str(round(deg, 2)), (ball.center[0], ball.center[1] - int(1.5 * ball.radius)))
        return img

    def apply_undistort(self):
        if Image.camera_matrix is None or Image.dist_matrix is None:
            Image.camera_matrix, Image.dist_matrix = utils.load_coefficients(
                'storage/chessboard-calibration/calibration_chessboard.yml')
        pic = cv2.undistort(self.image_bgr, self.camera_matrix, self.dist_matrix)
        return Image(image_bgr=pic)

    def apply_blurring(self):
        pic = cv2.GaussianBlur(self.image_bgr, (11, 11), 0)
        return Image(image_bgr=pic)

    def apply_hoop_cutting(self, hoop: Hoop):
        mask = np.zeros(self.image_bgr.shape, dtype='uint8')
        pic = cv2.circle(mask, hoop.center, hoop.radius, (255, 255, 255), -1)
        pic = cv2.bitwise_and(self.image_bgr, self.image_bgr, mask=mask)
        return Image(image_bgr=pic)

    def plot_ball_history(self, pts, color=(0, 0, 255)):
        pic = self.image_bgr
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(pts.maxlen / float(i + 1)) * 2.5)
            pic = cv2.line(pic, pts[i - 1], pts[i], color, thickness)
        return Image(image_bgr=pic)

    def save(self, dir_path, filename="image"):
        if dir_path[-1] != "/":
            dir_path = dir_path + "/"
        os.makedirs(dir_path, exist_ok=True)
        cv2.imwrite(dir_path + filename + "-hsv.png", self.image_hsv)
        cv2.imwrite(dir_path + filename + "-rgb.png", self.image_bgr)

    def color_split(self, dir_path, hsv_lower_bound, hsv_upper_bound, return_hsv=False):
        """ This method generates multiple pictures to separate different colored parts of the """
        if dir_path[-1] != "/":
            dir_path = dir_path + "/"
        os.makedirs(dir_path, exist_ok=True)
        source_pic = self.image_bgr
        if return_hsv:
            source_pic = self.image_hsv

        hsv_lower_bound = np.array(hsv_lower_bound)
        hsv_upper_bound = np.array(hsv_upper_bound)
        for x in range(0, 180, 5):
            # lower bound and upper bound for Orange color
            hsv_lower_bound[0] = x % 180
            hsv_upper_bound[0] = (x + 10) % 180
            # find the colors within the boundaries
            mask = cv2.inRange(self.image_hsv, hsv_lower_bound, hsv_upper_bound)
            # kernel = np.ones((3, 3), np.uint8)
            # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            segmented_img = cv2.bitwise_and(source_pic, source_pic, mask=mask)

            file_name = dir_path + str(x) + "-" + str((x + 10) % 180) + ".png"
            cv2.imwrite(file_name, segmented_img)

    @staticmethod
    def create(path: str = None, wb_gains=None):
        pic = helper.get_bgr_picture(path, wb_gains)
        return Image(image_bgr=pic)
