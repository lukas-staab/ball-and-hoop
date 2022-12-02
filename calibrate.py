import argparse
import os
import sys

# setting paths for custom package and current working directory

directory = os.path.abspath(os.path.dirname(__file__))
os.chdir(directory)
sys.path.append(directory)

# definition of parameters which can be used
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--white-calibration", default=False, action='store_true',
                help="Flag if white calibration should run")
ap.add_argument('-o', "--hoop-calibration", action='store_true', default=False,
                help="Flag if hoop calibration should run")
ap.add_argument('-l', "--lowercol", type=int, nargs=3, default=None,
                help="Only used with hoop: Lower bound of hoop border dots color in HSV color format (H: 0-180, S and V: 0-255 range)")
ap.add_argument('-u', "--uppercol", type=int, nargs=3, default=None,
                help="Only used with hoop: Upper bound of hoop border dots color in HSV color format (H: 0-180, S and V: 0-255 range)")
ap.add_argument('-b', "--ball-calibration", action='store_true', default=False,
                help="Flag if ball calibration should run")
ap.add_argument('-v', "--verbose", default=False, action='store_true',
                help='Give more output to console')
ap.add_argument('--host', type=str, default=None,
                help='Forces a different hostname. Helpful for testing outside the real host')
args = vars(ap.parse_args())

from src.ballandhoop.application import Application

app = Application(verbose_output=args['verbose'], force_hostname=args['host'])
app.run_calibration(calc_wb_gains=args['white_calibration'],
                    search_hoop=args['hoop_calibration'],
                    hoop_hsv={'upper' : args['uppercol'], 'lower': args['lowercol']},
                    search_ball=args['ball_calibration'],
                    ball_hsv={'upper': None, 'lower': None})
