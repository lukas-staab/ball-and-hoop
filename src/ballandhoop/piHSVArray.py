from picamera.array import PiRGBArray

import cv2


class PiHSVArray(PiRGBArray):
    """
    A wraper class which extends :py:class:`picamera.array.PiRGBArray` and converts the pixels to HSV color

    :param camera: the camera object, see parent constructor
    :type camera: picamera.PiCamera
    :param size: the size of the frame, see parent constructor

    :ivar array: the frame data, inherited
    """

    def __init__(self, camera, size=None):
        super(PiHSVArray, self).__init__(camera, size)

    def flush(self):
        """
        This method is called after the data is fully written. It converts to HSV.
        Note: the picamera has to use bgr, not rgb otherwise this will produce weird results
        """

        # method is called after data is written
        super(PiHSVArray, self).flush()
        # super().flush() wrote RGB Data to self.array, now convert it
        self.array = cv2.cvtColor(self.array, cv2.COLOR_BGR2HSV)
