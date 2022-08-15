from __future__ import annotations
import math
import os
import shutil

import imutils
import numpy as np
import cv2
import circle_fit as cf
from .ball import Ball



class Hoop:

    def __init__(self,
                 center: list,
                 radius: int,
                 center_dots:list,
                 radius_dots:list,
                 ):
        self.center = center,
        # i do not know why i need this line, input is ok, self. ist not
        self.center = self.center[0]
        # end of confusion
        self.radius = int(radius)
        self.center_dots = center_dots
        self.radius_dots = radius_dots

    @staticmethod
    def create_from_image(lower_hsv, upper_hsv, pic=None):
        shutil.rmtree('storage/hoop/')
        os.makedirs('storage/hoop/')
        lower_hsv = np.array(lower_hsv)
        upper_hsv = np.array(upper_hsv)
        if pic is None:
            import picamera.array
            camera = picamera.PiCamera(sensor_mode=7)
            camera.resolution = (640, 480)
            output = picamera.array.PiRGBArray(camera)
            camera.capture(output, format='rgb', use_video_port=True)
            pic = output.array
        from . import ImageComposer
        imc = ImageComposer(pic, do_undistortion=False, do_blurring=False)
        imc.color_split('storage/hoop/details/', lower_hsv, upper_hsv)
        hsv = imc.get_hsv()
        Hoop._save_debug_pic(pic, 'raw')
        Hoop._save_debug_pic(hsv, 'hsv')
        mask_hoop = cv2.inRange(hsv, lower_hsv, upper_hsv)
        Hoop._save_debug_pic(mask_hoop, 'hoop-mask')
        mask_hoop = cv2.erode(mask_hoop, None, iterations=2)
        Hoop._save_debug_pic(mask_hoop, 'hoop-mask-erode')
        mask_hoop = cv2.dilate(mask_hoop, None, iterations=2)
        Hoop._save_debug_pic(mask_hoop, 'hoop-mask-dil')
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
                center_dot = [int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])]
                dots_center.append(center_dot)
                dots_radius.append(radius)
        if len(dots_radius) < 3:
            return None # Exception('Less then 3 edge dots found for hoop. See in storage/hoop/ for debugging pictures')
        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        hoop = Hoop([int(xc), int(yc)], int(radius_hoop), dots_center, dots_radius)
        imc.start_new_image()
        imc.plot_hoop(hoop)
        Hoop._save_debug_pic(imc.image(), 'hoop')
        return hoop

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
        self.save_debug_pic(mask_ball, 'ball-mask')
        mask_ball = cv2.erode(mask_ball, None, iterations=iterations)
        self.save_debug_pic(mask_ball, 'ball-mask-erode')
        mask_ball = cv2.dilate(mask_ball, None, iterations=iterations)
        self.save_debug_pic(mask_ball, 'ball-mask-erode-dil')
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
        Hoop._save_debug_pic(img, name)

    @staticmethod
    def _save_debug_pic(img, name):
        if not name.endswith(".png"):
            name = name + ".png"
        os.makedirs('storage/hoop/', exist_ok=True)
        cv2.imwrite('storage/hoop/' + name, img)
