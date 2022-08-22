import argparse
import os
import sys

# setting paths for custom package and current working directory

directory = os.path.abspath(os.path.dirname(__file__))
os.chdir(directory)
sys.path.append(directory)

# definition of parameters which can be used
ap = argparse.ArgumentParser()
ap.add_argument('-l', "--lowercol", type=int, nargs=3, default=None,
                help="Lower bound of ball color in HSV color format")
ap.add_argument('-u', "--uppercol", type=int, nargs=3, default=None,
                help="Lower bound of ball color in HSV color format")
ap.add_argument('-v', "--verbose", default=False, action='store_true',
                help='Give more output to console')
ap.add_argument('--host', type=str, default=None,
                help='Forces a different hostname. Helpful for testing outside a raspberry pi')
args = vars(ap.parse_args())

from src.ballandhoop.application import Application

app = Application(verbose_output=args['verbose'], force_hostname=args['host'])
app.run(ball_search_col={'lower': args['lowercol'], 'upper': args['uppercol']})
