from __future__ import annotations
import math
import imutils
import numpy as np
import cv2
import circle_fit as cf

from src.ballandhoop import helper, Ball, Image


class Hoop:
    """
    Class which represents the data holding of the hoop
    This constructor is usually populated by the config file entries

    :param center: the center of the hoop
    :param radius: the radius of the hoop
    :param center_dots: a list of the center of the hoop markers for finding the hoop
    :param radius_dots: a list of the radius' of the hoop markers for finding the hoop
    :param angle_offset: a custom offset of angle, which will be added to each result of :py:meth:`.angle_in_hoop()`
    :param fov: a 2-tuple of angles which will be used as starting and ending angles to cut off the picture mask outside this circle sector
    :param kwargs: just a placeholder so if additional keys are given in config file, there will be no errors, because some config file attributes will be used in the methods
    """

    def __init__(self, center: list, radius: int, center_dots: list, radius_dots: list, angle_offset=0, fov=(90, 270),
                 **kwargs):
        self.center = center,
        # i do not know why i need this line, input is ok, self. ist not
        self.center = list(self.center[0])
        # end of confusion
        self.radius = int(radius)
        self.center_dots = list(center_dots)
        self.radius_dots = list(radius_dots)
        self.angle_offset = int(angle_offset)
        self.fov = fov

    @staticmethod
    def create_from_image(hsv, image: Image, morph_iterations=0, debug_output_path=None, min_dots_radius=2, **kwargs):
        """
        This method should be populated with the entries of the config file.
        It searches in range of the hsv colors for three or more hoop markers and builds a binary mask out of it.
        Depending on the `morph_iterations` amount the found mask will be eroded and dilated multiple times for noice reduction.
        If the radius of the markers is too small, it will not be used for the hoop calculation.
        The center of the remaining markers will be calculated and fitted to a circle.
        This circle radius and center are the center and radius of the returned hoop.
        If there are to less (remaining) markers, None will be returned instead.

        :param hsv: the colors to search for. has a `upper` and `lower` key which each hold a (H,S,V) color
        :param image: the Image to search the hoop markers in
        :type image: :py:class:`~.image.Image`
        :param morph_iterations: amount of times the mask will be eroded and dilated. The higher the value, the more noice is removed
        :param debug_output_path: the directory path where the debug pictures will be saved
        :param min_dots_radius: the minimal radius of the markers
        :param kwargs: a catch-all parameter, so if too many arguments are given, python will not throw an error
        :return: The hoop if any was found
        :rtype: :py:class:`.Hoop` | None
        """
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
        """
        Calculates the angle between a given point (e.g. the ball center) inside the hoop.
        The :py:attr:`angle_offset` is added to the angle.

        :param p: the point which angle should be calculated
        :type p: tuple
        :return: The angle between (p - :py:attr:`self.center`)  and (0, :py:attr:`self.radius`)
        """

        v1 = np.array((0, self.radius))
        v2 = np.array(p) - np.array(self.center)
        return self.angle_of_vectors(v1, v2) + self.angle_offset

    @staticmethod
    def angle_of_vectors(v1, v2):
        """
        Calculates the angle between two vectors
        :return: the angle between two vectors in degree
        :rtype: float
        """
        x = np.cross(v1, v2)
        y = np.dot(v1, v2)
        return math.atan2(x, y) / math.pi * 180

    def find_ball_async(self, frame_number, frame, ball_config, dir_path=None):
        """
        A wrapper function for the async call from the :py:class:`Application` for :py:meth:`find_ball()`.

        :param frame_number: the number of the frame, not used for calculation but important for the :py:meth:`application callback <.application.Application.ball_found_async_callback()>`
        :param frame: the frame array in hsv color space
        :param ball_config: the ball config, see :py:meth:`find_ball()` for more info
        :param dir_path: the directory where debugging pictures will be saved
        :return: A tuple of the given frame number and the found ball, if any
        :rtype: (int, Ball|None)
        """
        ball = self.find_ball(frame, **ball_config, dir_path=dir_path)
        return frame_number, ball

    def find_ball(self, frame, hsv, morph_iterations=1, min_radius=5, max_radius=20, dir_path=None, **kwargs):
        """
        Tries to find the ball in the given picture. Therefore, the image is filtered with the given HSV colors to a mask.
        This mask is morphed, depending on the given iterations. There will be a dilatation and an erode afterwards (closure),
        to close holes in the found ball mask which will be there because of the physical hoop.
        All found mask points which are outside the given hoop :py:attr:`Field of View<fov>` are removed.
        It will then loop through the biggest connected areas in the mask (the biggest first). If their radius is inside min_radius and
        max_radius the found ball will be returned or none if none of the connected areas are fitting the limits.

        :param frame: the array of the frame in HSV color space
        :param hsv: a dictionary with `upper` and `lower` and (H,S,V) values, which the frame will be filtered to
        :param morph_iterations: the amount of iterations to morph, defaults to 1
        :param min_radius: the minimal radius a ball is allowed to have, defaults to 5
        :param max_radius: the maximal radius a ball is allowed to have, defaults to 20
        :param dir_path: the directory where debugging pictures will be saved, defaults to None
        :param kwargs: just a catch-all for additional parameters from the config file, will be ignored
        :return: the found ball, if any
        :rtype: Ball | None
        """
        Image(image_hsv=frame).save(dir_path, 'raw')
        mask_ball = cv2.inRange(frame, np.array(hsv['lower']), np.array(hsv['upper']))
        Image(image_bw=mask_ball).save(dir_path, 'ball-mask')
        if morph_iterations > 0:
            mask_ball = cv2.dilate(mask_ball, None, iterations=morph_iterations)
            Image(image_bw=mask_ball).save(dir_path, 'ball-mask-dil')
            mask_ball = cv2.erode(mask_ball, None, iterations=morph_iterations)
            Image(image_bw=mask_ball).save(dir_path, 'ball-mask-dil-erode')

        mask_hoop = np.zeros_like(mask_ball)
        mask_hoop = cv2.ellipse(mask_hoop, self.center, (self.radius, self.radius), 0, self.fov[0] - 90,
                                self.fov[1] - 90, (255, 255, 255), -1)
        Image(image_bw=mask_hoop).save(dir_path, 'segment-mask')
        mask = cv2.bitwise_and(mask_hoop, mask_ball)
        Image(image_bw=mask).save(dir_path, 'final-mask')

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        # this function only wraps the different opencv signatures, it does nothing else
        cnts = list(imutils.grab_contours(cnts))
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

        # this if is technically not necessary but saves a bit performance
        if dir_path is not None:
            # save a result picture if debug dir path is set
            Image(image_hsv=frame) \
                .plot_hoop(self) \
                .plot_ball(ball) \
                .plot_angle(ball) \
                .save(dir_path, 'result')
        # returns None if there was no valid ball contour in the list, the first found ball otherwise
        return ball
