import argparse
import os
import sys
import time

# setting paths for custom package and current working directory
directory = os.path.abspath(os.path.dirname(__file__))
os.chdir(directory)
sys.path.append(directory)

# definition of parameters which can be used
ap = argparse.ArgumentParser()
ap.add_argument('-l', "--lowercol", type=int, nargs=3, default=None,
                help="Lower bound of ball color in HSV color format (H: 0-180, S and V: 0-255 range)")
ap.add_argument('-u', "--uppercol", type=int, nargs=3, default=None,
                help="Lower bound of ball color in HSV color format (H: 0-180, S and V: 0-255 range)")
ap.add_argument('-v', "--verbose", default=False, action='store_true',
                help='Give more output to console')
ap.add_argument('-t', "--time", default=False, action='store_true',
                help='Output how long this app had run')
ap.add_argument('--host', type=str, default=None,
                help='Forces a different hostname. Helpful for testing outside a raspberry pi')
args = vars(ap.parse_args())

from src.ballandhoop.application import Application

start_time = time.time()
app = Application(verbose_output=args['verbose'], force_hostname=args['host'])
app.run(ball_hsv={'lower': args['lowercol'], 'upper': args['uppercol']})

if args['time']:
    end_time = time.time()
    diff_time = end_time - start_time
    print(diff_time)