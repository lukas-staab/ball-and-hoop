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

    def __init__(self,center: list, radius: int, center_dots: list, radius_dots: list, angle_offset=0, **kwargs):
        self.center = center,
        # i do not know why i need this line, input is ok, self. ist not
        self.center = list(self.center[0])
        # end of confusion
        self.radius = int(radius)
        self.center_dots = list(center_dots)
        self.radius_dots = list(radius_dots)
        self.angle_offset = int(angle_offset)
        print("Offset: " + str(self.angle_offset))

    @staticmethod
    def create_from_image(hsv, image:Image, morph_iterations=0, debug_output_path=None, min_dots_radius=2, **kwargs):
        lower_hsv = np.array(hsv['lower'])
        upper_hsv = np.array(hsv['upper'])

        if debug_output_path is not None and debug_output_path[-1] != '/':
            debug_output_path = debug_output_path + "/"

        mask_hoop = cv2.inRange(image.image_hsv, lower_hsv, upper_hsv)
        Image(image_bw=mask_hoop).save(debug_output_path, 'hoop-mask')
        if morph_iterations > 0:
            mask_hoop = cv2.erode(mask_hoop, None, iterations=morph_iterations)
            Image(image_bw=mask_hoop).save(debug_output_path, 'hoop-mask-erode')
            mask_hoop = cv2.dilate(mask_hoop, None, iterations=morph_iterations)
            Image(image_bw=mask_hoop).save(debug_output_path, 'hoop-mask-erode-dil')
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
            if radius >= min_dots_radius:
                m = cv2.moments(c)
                center_dot = [int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])]
                dots_center.append(center_dot)
                dots_radius.append(int(radius))
        if len(dots_radius) < 3:
            return None  # Exception('Less then 3 edge dots found for hoop. See in storage/hoop/ for debugging pictures')
        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        hoop = Hoop([int(xc), int(yc)], int(radius_hoop), dots_center, dots_radius)
        return hoop

    def angle_in_hoop(self, p: tuple):
        v1 = np.array((0, self.radius))
        v2 = np.array(p) - np.array(self.center)
        return self.angle_of_vectors(v1, v2) + self.angle_offset

    @staticmethod
    def angle_of_vectors(v1, v2):
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball_async(self, frame_number, frame, ball_config, dir_path=None):
        ball = self.find_ball(frame, **ball_config, dir_path=dir_path)
        return frame_number, ball

    def find_ball(self, frame, hsv, morph_iterations=1, min_radius=5, max_radius=20, dir_path=None, **kwargs):
        Image(image_hsv=frame).save(dir_path, 'raw')
        mask_ball = cv2.inRange(frame, np.array(hsv['lower']), np.array(hsv['upper']))
        Image(image_bw=mask_ball).save(dir_path, 'ball-mask')
        if morph_iterations > 0:
            mask_ball = cv2.dilate(mask_ball, None, iterations=morph_iterations)
            Image(image_bw=mask_ball).save(dir_path, 'ball-mask-dil')
            mask_ball = cv2.erode(mask_ball, None, iterations=morph_iterations)
            Image(image_bw=mask_ball).save(dir_path, 'ball-mask-dil-erode')
        cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        # this function only wraps the different opencv signatures, it does nothing else
        cnts = list(imutils.grab_contours(cnts))
        # if there are no contours in the picture, return no ball found
        if len(cnts) == 0:
            # cv2.imshow('debug', hsv)
            # time.sleep(5)
            return None
        # sort contours in the mask by area, then try if the
        #  minimum enclosing circle is fitting in the ball radius range
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        ball = None
        for c in cnts:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius < min_radius or radius > max_radius:
                # skip this entry if to big or too small
                continue
            # otherwise continue with the calculation
            m = cv2.moments(c)
            if float(m['m00']) == 0.0:
                # div 0
                continue
            center_ball = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
            ball = Ball(self, center_ball, int(radius))
            # keep the first fitting ball and do not loop further
            break

        if dir_path is not None:
            # save a result picture if debug dir path is set
            Image(image_hsv=frame)\
                .plot_hoop(self)\
                .plot_ball(ball)\
                .plot_angle(self, ball)\
                .save(dir_path, 'result')
        # returns None if there was no valid contour in the list, the first found ball otherwise
        return ball
