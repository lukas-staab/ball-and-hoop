

import os

import picamera.array
import numpy as np
import cv2

dirPath = './storage/awb/'
os.makedirs(dirPath, exist_ok=True)
# https://raspberrypi.stackexchange.com/questions/22975/custom-white-balancing-with-picamera
with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.awb_mode = 'off'
    # Start off with ridiculously low gains
    rg, bg = (0.5, 0.5)
    with picamera.array.PiRGBArray(camera) as output:
        # Allow 30 attempts to fix AWB
        for i in range(10):
            # Capture a tiny resized image in RGB format, and extract the
            # average R, G, and B values
            camera.awb_gains = (rg, bg)
            camera.capture(output, format='rgb', use_video_port=True, sensor_mode=7)
            cv2.imwrite(dirPath + '{0:2d}.png'.format(i), output.array)
            r, g, b = (np.mean(output.array[..., i]) for i in range(3))
            print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (
                rg, bg, r, g, b))
            # Adjust R and B relative to G, but only if they're significantly
            # different (delta +/- 2)
            if abs(r - g) > 2:
                rg -= 0.01 * (r - g)
            if abs(b - g) > 1:
                bg -= 0.01 * (b - g)
            (rg, bg) = max((0, 0), (rg, bg))
            (rg, bg) = min((8, 8), (rg, bg))
            output.seek(0)
            output.truncate()