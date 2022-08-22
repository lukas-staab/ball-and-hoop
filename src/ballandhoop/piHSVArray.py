from picamera.array.PiRGBArray import PiRGBArray


class PiHSVArray(PiRGBArray):

    def __init__(self, camera, size=None):
        super(PiHSVArray, self).__init__(camera, size)

    def flush(self):
        # method is called after data is written
        super(PiHSVArray, self).flush()
        # super().flush() wrote RGB Data to self.array, now convert it
        self.array = cv2.cvtColor(self.array, cv2.COLOR_RGB2HSV)
