from __future__ import annotations
import math
import imutils
import numpy as np
import cv2
import circle_fit as cf
from .ball import Ball


class Hoop:

    def __init__(self,
                 center: tuple,
                 radius: int,
                 center_dots,
                 radius_dots,
                 debug_path: str
                 ):
        self.center = center,
        # i dont know why i need this. center is fine shaped, self.center is not...
        self.center = self.center[0]
        # end of confusion
        self.radius = int(radius)
        self.center_dots = center_dots
        self.radius_dots = radius_dots
        self.debug_path = debug_path

    @staticmethod
    def create_from_image(imc: ImageComposer, lower_hsv=np.array([150, 20, 20]),
                          upper_hsv=np.array([190, 255, 255]), ):
        mask_hoop = cv2.inRange(imc.get_hsv(), lower_hsv, upper_hsv)
        Hoop.save_debug_pic(imc.debug_path, mask_hoop, 'hoop-mask')
        mask_hoop = cv2.erode(mask_hoop, None, iterations=2)
        Hoop.save_debug_pic(imc.debug_path, mask_hoop, 'hoop-mask-erode')
        mask_hoop = cv2.dilate(mask_hoop, None, iterations=2)
        Hoop.save_debug_pic(imc.debug_path, mask_hoop, 'hoop-mask-dil')
        mask_hoop = mask_hoop
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
            if radius > 5:
                m = cv2.moments(c)
                center_dot = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
                dots_center.append(center_dot)
                dots_radius.append(radius)
        if len(dots_radius) < 3:
            return None
        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        center_hoop = (int(xc), int(yc))
        return Hoop(center_hoop, radius_hoop, dots_center, dots_radius)

    def angle_in_hoop(self, p: tuple):
        v1 = np.array((0, -self.radius))
        v2 = np.array(p) - np.array(self.center)
        return self.angle_of_vectors(v1, v2)

    @staticmethod
    def angle_of_vectors(v1, v2):
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball(self, imc: ImageComposer, hue_low, hue_upper, saturation_low=50, saturation_upper=255, iterations=2):
        mask_ball = cv2.inRange(imc.get_hsv(), (hue_low, saturation_low, 50), (hue_upper, saturation_upper, 255))
        self.save_debug_pic(self, mask_ball, 'ball-mask')
        mask_ball = cv2.erode(mask_ball, None, iterations=iterations)
        self.save_debug_pic(self, mask_ball, 'ball-mask-erode')
        mask_ball = cv2.dilate(mask_ball, None, iterations=iterations)
        self.save_debug_pic(self, mask_ball, 'ball-mask-erode-dil')
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
        # only proceed if the radius meets a minimum size
        return Ball(self, center_ball, int(radius))

    def save_debug_pic(self, img, name):
        Hoop._save_debug_pic(self.debug_path, img, name)

    @staticmethod
    def _save_debug_pic(path: str, img, name):
        if not name.endswith(".png"):
            name = name + ".png"
        if path is not None:
            cv2.imwrite(path + name, img)
