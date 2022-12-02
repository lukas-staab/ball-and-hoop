"""
.. warning::
    Do not use this class too much in mission critical calculations.
    It is not optimized to work fast. Its just a convinient wrapper, which transform every bgr to hsv and vice versa.
    This happens afer every image processing step. You have been warned.
"""

from __future__ import annotations

import os

import numpy as np
import cv2
from cv2 import FONT_HERSHEY_PLAIN

from src.ballandhoop import helper
from src.chessboard import utils


class Image:
    """
    If this class is created with a bgr oder hsv array, the other one will be automatically generated

    :param image_bgr: the bgr frame array 
    :param image_hsv: the hsv frame array 
    :param image_bw:  a monochrome frame array 
    """

    camera_matrix = None
    """ 
    The camera matrix, loaded from the chessboard calibration
    """

    dist_matrix = None
    """
    The dist matrix, loaded from the chessboard calibration
    """

    def __init__(self, image_bgr=None, image_hsv=None, image_bw=None):

        self.image_bgr = None
        self.image_hsv = None
        self.image_bw = image_bw
        if image_bgr is None and image_hsv is None and image_bw is None:
            raise Exception('Cannot work with empty/none image')
        if image_bw is None:
            if image_bgr is not None:
                self.image_bgr = image_bgr
            else:
                self.image_bgr = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

            if image_hsv is not None:
                self.image_hsv = image_hsv
            else:
                self.image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    def plot_hoop(self, hoop: Hoop, color: tuple = (255, 0, 0), thickness=2, with_dots=False) -> Image:
        """
        Plots a hoop as a circle in the image
        
        :param hoop: the hoop to plot
        :type hoop: Hoop
        :param color: the color the circle will be plotted in, defaults to (255, 0, 0)
        :param thickness: the thickness the circle will be plotted in, -1 for full fill, defaults to 2
        :param with_dots: flag if the dots should be plotted as well
        :type with_dots: bool
        :return: The new image instance
        :rtype: Image 
        """
        if hoop is None:
            return self
        pic = cv2.circle(self.image_bgr, hoop.center, int(hoop.radius), color, thickness)
        if with_dots:
            for i, center in enumerate(hoop.center_dots):
                pic = cv2.circle(pic, center, hoop.radius_dots[i] + 1, color, -1)
        return Image(image_bgr=pic)

    def plot_ball(self, ball: Ball, color_outline: tuple = (0, 255, 0),
                  color_center: tuple = (0, 255, 0)) -> Image:
        """
        Plots the outline and the center of a ball in the image
        
        :param ball: The ball to plot
        :param color_outline: the color of the outline, defaults to (0, 255, 0)
        :param color_center:  the color of the center, defaults to (0, 255, 0)
        :return: The new image instance
        :rtype: Image 
        """
        
        if ball is None:
            return self
        pic = self.image_bgr
        pic = cv2.circle(pic, ball.center, ball.radius, color_outline, 2)
        pic = cv2.circle(pic, ball.center, 3, color_center, -1)
        return Image(image_bgr=pic)

    def plot_line(self, p1: tuple, p2: tuple, color: tuple = (255, 0, 0), thickness: int = 2) -> Image:
        """
        Plots a line in the image
        
        :param p1: the first point 
        :param p2: the second point 
        :param color: the color, defaults to (255, 0, 0)
        :param thickness: the thickness, defaults to 2
        :return: The new image instance
        :rtype: Image 
        """
        pic = cv2.line(self.image_bgr, p1, p2, color, thickness)
        return Image(image_bgr=pic)

    def plot_rectangle(self, x, y, w, h, color=(255, 0, 0), thickness=3) -> Image:
        """
        Plots a rectangle in the image
        
        :param x: the x coordinate
        :param y: the y coordinate
        :param w: the width
        :param h: the height 
        :param color: the color, defaults to (255, 0, 0)
        :param thickness: the thickness, defaults to 3
        :return: 
        """
        pic = cv2.rectangle(self.image_bgr, (x, y), (x + w, y + h), color=color, thickness=thickness)
        return Image(image_bgr=pic)

    def plot_text(self, text: str, pos: tuple, color: tuple = (255, 0, 0), fontScale=1) -> Image:
        """
        Plots text to the image
        
        :param text: the text, 
        :param pos: the position
        :param color: the color, defaults to (255, 0, 0)
        :param fontScale: the fontscale, defaults to 1
        :return: The new image instance
        :rtype: Image 
        """
        
        pic = cv2.putText(self.image_bgr, text, pos, fontFace=FONT_HERSHEY_PLAIN, color=color, fontScale=fontScale)
        return Image(image_bgr=pic)

    def plot_angle(self, ball: Ball) -> Image:
        """
        Plots the angle to the image
        
        :param ball: the ball
        :return: The new image instance
        :rtype: Image
        """
        
        hoop = ball.hoop
        if ball is None or hoop is None:
            return self
        deg = hoop.angle_in_hoop(ball.center)

        img = self.plot_line(hoop.center, ball.center)
        img = img.plot_line(hoop.center, ball.center)
        img = img.plot_text(str(round(deg, 2)), (ball.center[0], ball.center[1] - int(1.5 * ball.radius)))
        return img

    def apply_undistort(self, demo=False) -> Image:
        """
        Undistort the image with the lens calibration from the chessboard 
        
        :param demo: flag if the image should be cutted or transformed with black border
        :return: The new image instance
        :rtype: Image
        """
        if Image.camera_matrix is None or Image.dist_matrix is None:
            Image.camera_matrix, Image.dist_matrix = utils.load_coefficients(
                'storage/chessboard-calibration/calibration_chessboard.yml')
        h, w = self.image_bgr.shape[:2]
        new_cam_mat, roi = cv2.getOptimalNewCameraMatrix(Image.camera_matrix, Image.dist_matrix, (w, h), int(demo),
                                                         (w, h))
        pic = cv2.undistort(self.image_bgr, self.camera_matrix, self.dist_matrix, newCameraMatrix=new_cam_mat)
        if demo:
            x, y, w, h = roi
            im = Image(image_bgr=pic)
            return im.plot_rectangle(x, y, w, h)
        return Image(image_bgr=pic)

    def apply_blurring(self, blur_radius=11) -> Image:
        """
        Blurs the image
        
        :param blur_radius: the blur radius, defaults to 11
        :return: The new image instance
        :rtype: Image
        """
        pic = cv2.GaussianBlur(self.image_bgr, (blur_radius, blur_radius), 0)
        return Image(image_bgr=pic)

    def apply_hoop_cutting(self, hoop: Hoop) -> Image:
        """
        WIP - blacks out everything outside the hoop
        
        :param hoop: 
        :return: The new image instance
        :rtype: Image
        """
        mask = np.zeros(self.image_bgr.shape, dtype='uint8')
        mask = cv2.circle(mask, hoop.center, hoop.radius, (255, 255, 255), -1)
        pic = cv2.bitwise_and(self.image_bgr, self.image_bgr, mask=mask)
        return Image(image_bgr=pic)

    def plot_ball_history(self, pts, color=(0, 0, 255)) -> Image:
        """
        Plots the ball history. The tail is getting less thick
        
        :param pts: the list of the points 
        :param color: the color 
        :return: The new image instance
        :rtype: Image
        """
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
        """
        Save the image to the given dir with the filename in rgb and hsv
        
        :param dir_path: the dir_path, if none, then nothing is saved
        :param filename: the filename, will be suffixed with `-hsv.png` and `-rgb.png`
        """
        if dir_path is None:
            return
        if dir_path[-1] != "/":
            dir_path = dir_path + "/"
        os.makedirs(dir_path, exist_ok=True)
        # hsv has to be BGR2RGB converted, so the RGB result in png will be in correct order, open cv expects BGR
        if self.image_bgr is not None and self.image_hsv is not None:
            cv2.imwrite(dir_path + filename + "-hsv.png", cv2.cvtColor(self.image_hsv, cv2.COLOR_RGB2BGR))
            cv2.imwrite(dir_path + filename + "-rgb.png", self.image_bgr)
        else:
            cv2.imwrite(dir_path + filename + ".png", self.image_bw)

    def color_split(self, dir_path, hsv_lower_bound, hsv_upper_bound, return_hsv=False):
        """
        This method generates multiple pictures to separate different colored parts of the image.
        Rotates through the H value with fixed S and V values
        
        :param dir_path: the dir path, can have a tailored `/`, but does not need to
        :param hsv_lower_bound: lower hsv value, H will be rotated
        :param hsv_upper_bound: upper hsv value, H will be rotated
        :param return_hsv: flag if a hsv color space should be saved, or rgb, defaults to False (rgb)
        """
        if dir_path[-1] != "/":
            dir_path = dir_path + "/"
        os.makedirs(dir_path, exist_ok=True)
        source_pic = self.image_bgr
        if return_hsv:
            # hsv has to be BGR2RGB converted, so the RGB result in png will be in correct order, open cv expects BGR
            source_pic = cv2.cvtColor(self.image_hsv, cv2.COLOR_RGB2BGR)

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
    def create(path: str = None, wb_gains=None) -> Image:
        """
        Creates an Image instance, either from file or cam
        
        :param path: the path, if not given take pic from cam
        :param wb_gains: the wb_gains the cam will use if needed
        :return: A new image instance
        :rtype: Image
        """
        pic = helper.get_bgr_picture(path, wb_gains)
        return Image(image_bgr=pic)
