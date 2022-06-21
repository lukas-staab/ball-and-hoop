import os

import picamera.array
import numpy
import cv2


class WhiteBalancing:

    def __init__(self, dirPath='./storage/awb/', deleteOldPics=True):
        self.dirPath = dirPath
        os.makedirs(self.dirPath, exist_ok=True)
        filelist = [f for f in os.listdir(self.dirPath) if f.endswith(".png") and deleteOldPics]
        for f in filelist:
            os.remove(os.path.join(self.dirPath, f))

    def calculate(self):
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
                    camera.capture(output, format='rgb', use_video_port=True)
                    cv2.imwrite(self.dirPath + '{0:2d}.png'.format(i), output.array)
                    r, g, b = (numpy.mean(output.array[..., i]) for i in range(3))
                    print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (rg, bg, r, g, b))
                    # Adjust R and B relative to G, but only if they're significantly
                    # different (delta +/- 2)
                    if abs(r - g) > 2:
                        rg -= 0.01 * (r - g)
                        changed = True
                    if abs(b - g) > 2:
                        bg -= 0.01 * (b - g)
                        changed = True
                    (rg, bg) = numpy.maximum((0, 0), (rg, bg))
                    (rg, bg) = numpy.minimum((8, 8), (rg, bg))
                    output.seek(0)
                    output.truncate()
                    if changed is False:
                        return rg, bg


