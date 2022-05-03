import math
import imutils
import numpy
import numpy as np
import cv2
import circle_fit as cf


class Hoop:

    def __init__(self,
                 hsv_image,
                 lower_hsv=np.array([150, 20, 20]),
                 upper_hsv=np.array([190, 255, 255]),
                 ):
        self.hsv_image = hsv_image
        self.lower_hsv = lower_hsv
        self.upper_hsv = upper_hsv
        self.center, self.radius, self.center_dots, self.radius_dots = self.find_hoop()

    def find_hoop(self):
        mask_hoop = cv2.inRange(self.hsv_image, self.lower_hsv, self.upper_hsv)
        mask_hoop = cv2.erode(mask_hoop, None, iterations=2)
        mask_hoop = cv2.dilate(mask_hoop, None, iterations=2)
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

        xc, yc, radius_hoop, _ = cf.least_squares_circle(dots_center)
        center_hoop = (int(xc), int(yc))

        return numpy.array(center_hoop), radius_hoop, dots_center, dots_radius

    def angle_in_hoop(self, center_ball):
        v1 = np.array((0, -self.radius))
        v2 = center_ball - self.center
        return self.angle_of_vectors(v1, v2)

    @staticmethod
    def angle_of_vectors(v1, v2):
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball(self, hsv, col_low, col_up):
        mask_ball = cv2.inRange(hsv, (col_low, 20, 20), (col_up, 255, 255))
        mask_ball = cv2.erode(mask_ball, None, iterations=2)
        mask_ball = cv2.dilate(mask_ball, None, iterations=2)
        cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) == 0:
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

