from __future__ import annotations
import math
import os
import shutil
import imutils
import numpy as np
import cv2
import circle_fit as cf

from src.ballandhoop import helper, Ball, Image


class Hoop:

    def __init__(self,center: list, radius: int, center_dots: list, radius_dots: list, **arg):
        self.center = center,
        # i do not know why i need this line, input is ok, self. ist not
        self.center = self.center[0]
        # end of confusion
        self.radius = int(radius)
        self.center_dots = center_dots
        self.radius_dots = radius_dots

    @staticmethod
    def create_from_image(lower, upper, pic=None, iterations=2, debug_output_path=None):
        lower_hsv = np.array(lower)
        upper_hsv = np.array(upper)

        if debug_output_path is not None and debug_output_path[-1] != '/':
            debug_output_path = debug_output_path + "/"

        if type(pic) is str or pic is None:
            im = Image.create(pic)
        else:
            im = Image(image_bgr=pic)

        im.color_split(debug_output_path + 'hoop-colsplit/', lower_hsv, upper_hsv)
        hsv = im.image_hsv
        Hoop._save_debug_pic(pic, 'raw', debug_output_path)
        Hoop._save_debug_pic(hsv, 'hsv', debug_output_path)
        mask_hoop = cv2.inRange(hsv, lower_hsv, upper_hsv)
        Hoop._save_debug_pic(mask_hoop, 'hoop-mask', debug_output_path)
        if iterations > 0:
            mask_hoop = cv2.erode(mask_hoop, None, iterations=iterations)
            Hoop._save_debug_pic(mask_hoop, 'hoop-mask-erode', debug_output_path)
            mask_hoop = cv2.dilate(mask_hoop, None, iterations=iterations)
            Hoop._save_debug_pic(mask_hoop, 'hoop-mask-erode-dil', debug_output_path)
        cnts = cv2.findContours(mask_hoop.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        dots_center = []
        dots_radius = []

        for c in cnts:
            # iterate over all contours in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 3:
                m = cv2.moments(c)
                center_dot = [int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])]
                dots_center.append(center_dot)
                dots_radius.append(int(radius))
        if len(dots_radius) < 3:
            return None, im  # Exception('Less then 3 edge dots found for hoop. See in storage/hoop/ for debugging pictures')
        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        hoop = Hoop([int(xc), int(yc)], int(radius_hoop), dots_center, dots_radius)
        im = im.plot_hoop(hoop)
        Hoop._save_debug_pic(im.image_bgr, 'hoop', debug_output_path)
        return hoop, im

    def angle_in_hoop(self, p: tuple):
        v1 = np.array((0, -self.radius))
        v2 = np.array(p) - np.array(self.center)
        return self.angle_of_vectors(v1, v2)

    @staticmethod
    def angle_of_vectors(v1, v2):
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball(self, frame, cols: dict, iterations=2, dir_path=None):
        mask_ball = cv2.inRange(frame, np.array(cols['lower']), np.array(cols['upper']))
        self.save_debug_pic(mask_ball, 'ball-mask', dir_path)
        if iterations > 0:
            mask_ball = cv2.dilate(mask_ball, None, iterations=iterations)
            self.save_debug_pic(mask_ball, 'ball-mask-dil', dir_path)
            mask_ball = cv2.erode(mask_ball, None, iterations=iterations)
            self.save_debug_pic(mask_ball, 'ball-mask-dil-erode', dir_path)
        cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) == 0:
            # cv2.imshow('debug', hsv)
            # time.sleep(5)
            return None
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        m = cv2.moments(c)
        center_ball = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
        ball = Ball(self, center_ball, int(radius))
        if ball.radius < 8:
            # if found ball is too small, it is probably not a real ball but noise
            return None
        if dir_path is not None:
            Image(image_hsv=frame).plot_hoop(self).plot_ball(ball).save(dir_path, 'result')
        return ball

    def save_debug_pic(self, img, name, dir_path):
        Hoop._save_debug_pic(img, name, dir_path)

    @staticmethod
    def _save_debug_pic(img, name, dir_path):
        if dir_path is None:
            return
        if not name.endswith(".png"):
            name = name + ".png"
        if not dir_path.endswith('/'):
            dir_path = dir_path + "/"
        os.makedirs(dir_path, exist_ok=True)
        cv2.imwrite(dir_path + name, img)
