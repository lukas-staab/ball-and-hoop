import math
import imutils
import numpy as np
import cv2
import circle_fit as cf
import src.hoop.ImageComposer as ic


class Hoop:

    def __init__(self,
                 image_composer: ic.ImageComposer,
                 lower_hsv=np.array([150, 20, 20]),
                 upper_hsv=np.array([190, 255, 255]),
                 ):
        self.image_composer = image_composer
        self.lower_hsv = lower_hsv
        self.upper_hsv = upper_hsv
        self.debug_path = image_composer.get_debug_path()
        self.center, self.radius, self.center_dots, self.radius_dots, self.mask_hoop = (None, None, None, None, None)

    def find_hoop(self):
        mask_hoop = cv2.inRange(self.image_composer.get_hsv(), self.lower_hsv, self.upper_hsv)
        self.save_debug_pic(mask_hoop, 'hoop-mask')
        mask_hoop = cv2.erode(mask_hoop, None, iterations=2)
        self.save_debug_pic(mask_hoop, 'hoop-mask-erode')
        mask_hoop = cv2.dilate(mask_hoop, None, iterations=2)
        self.save_debug_pic(mask_hoop, 'hoop-mask-dil')
        self.mask_hoop = mask_hoop
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
            raise RuntimeError('Not enough calibration points in the picture')
        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        center_hoop = (int(xc), int(yc))
        ret = (center_hoop, int(radius_hoop), dots_center, dots_radius, mask_hoop)
        self.center, self.radius, self.center_dots, self.radius_dots, self.mask_hoop = ret
        return ret

    def angle_in_hoop(self, center_ball):
        v1 = np.array((0, -self.radius))
        v2 = center_ball - self.center
        return self.angle_of_vectors(v1, v2)

    @staticmethod
    def angle_of_vectors(v1, v2):
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball(self, col_low, col_up):
        mask_ball = cv2.inRange(self.image_composer.get_hsv(), (col_low, 20, 20), (col_up, 255, 255))
        self.save_debug_pic(mask_ball, 'ball-mask')
        mask_ball = cv2.erode(mask_ball, None, iterations=2)
        self.save_debug_pic(mask_ball, 'ball-mask-erode')
        mask_ball = cv2.dilate(mask_ball, None, iterations=2)
        self.save_debug_pic(mask_ball, 'ball-mask-erode-dil')
        cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) == 0:
            # cv2.imshow('debug', hsv)
            # time.sleep(5)
            raise RuntimeError('No ball found')
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        m = cv2.moments(c)
        center_ball = np.array((int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])))
        # only proceed if the radius meets a minimum size
        hoop_deg = self.angle_in_hoop(center_ball)
        return center_ball, radius, hoop_deg

    def save_debug_pic(self, img, name):
        if not name.endswith(".png"):
            name = name + ".png"
        if self.debug_path != "":
            cv2.imwrite(self.debug_path + name, img)
