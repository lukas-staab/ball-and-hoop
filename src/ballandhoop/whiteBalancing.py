import os
import numpy
import cv2
import numpy as np

from src.ballandhoop import helper


class WhiteBalancing:
    """
    This class organizes the white balancing and manual calculation of the wb_gains.
    It takes a picture with arbitrary gains, takes (optional) a region of interest [210:430, 150:320]
    in the middle of the image (cropping it) and averaging all red, blue and green values.
    The goal is to change the red and blue gain that way, that all means are equal.
    Works best with a well illuminated and white only background.

    :param dirPath: the path where the debugging pictures are saved to, defaults to `storage/awb`
    :param delta: the accepted difference delta between the mean color values r,g,b, defaults to 2
    :param verboseOutput: flag if more output should be given, defaults to False
    """

    def __init__(self, dirPath='storage/awb/', delta=2, verboseOutput=False):
        self.verboseOutput = verboseOutput
        self.dirPath = dirPath
        self.delta = delta
        helper.reset_content_of_dir(dirPath)

    def calculate(self, cropping=False):
        """
        Does the calculation

        :param cropping: flag if roi [210:430, 150:320] should be cropped before the mean calculation
        :return: (r_gain,b_gain)
        :rtype: (float, float) each between 0 and 8
        """
        import picamera.array
        # https://raspberrypi.stackexchange.com/questions/22975/custom-white-balancing-with-picamera
        with picamera.PiCamera(sensor_mode=7) as camera:
            camera.resolution = (640, 480)
            camera.awb_mode = 'off'
            # Start off with ridiculously low gains
            rg, bg = (0.5, 0.5)
            with picamera.array.PiRGBArray(camera) as output:
                # Allow 30 attempts to fix AWB
                for i in range(10):
                    # Capture a tiny resized image in RGB format, and extract the
                    # average R, G, and B values
                    changed = False
                    camera.awb_gains = (rg, bg)
                    camera.capture(output, format='bgr', use_video_port=True)
                    pic = output.array
                    if cropping:
                        pic = pic[210:430, 150:320]
                    cv2.imwrite(self.dirPath + '{0:2d}.png'.format(i), pic)
                    b, g, r = (numpy.mean(pic[..., i]) for i in range(3))
                    if self.verboseOutput:
                        print('R:%5.2f, B:%5.2f => (%5.2f, %5.2f, %5.2f)' % (rg, bg, r, g, b))
                    # Adjust R and B relative to G, but only if they're significantly
                    if abs(r - g) > self.delta:
                        rg -= 0.01 * (r - g)
                        changed = True
                    if abs(b - g) > self.delta:
                        bg -= 0.01 * (b - g)
                        changed = True
                    # make sure they are in the valid bounds between 0 and 8
                    (rg, bg) = numpy.maximum((0, 0), (rg, bg))
                    (rg, bg) = numpy.minimum((8, 8), (rg, bg))
                    output.seek(0)
                    output.truncate()
                    if changed is False:
                        output.close()
                        camera.close()
                        return [float(rg), float(bg)]


