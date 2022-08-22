import argparse
import os
import sys

# setting paths for custom package and current working directory

directory = os.path.abspath(os.path.dirname(__file__))
os.chdir(directory)
sys.path.append(directory)

# definition of parameters which can be used
ap = argparse.ArgumentParser(description='This cmd line interface was build to help generate faker content')
ap.add_argument("-w", "--white-calibration", default=None, nargs=2,
                help="Enter custom wb_gains, if empty it will measure them")
ap.add_argument("--video", action='store_true', default=False,
                help="Flag if video should be taken")
ap.add_argument('-p', "--picture", action='store_true', default=False,
                help="Flag if picture should be taken")
ap.add_argument('-v', "--verbose", default=False, action='store_true',
                help='Give more output to console')
ap.add_argument('-n', '--name', type=str, required=True)
ap.add_argument('--host', type=str, default=None,
                help='Forces a different hostname. Helpful for writing outside the real host')
args = vars(ap.parse_args())

from src.ballandhoop.application import Application

app = Application(verbose_output=args['verbose'], force_hostname=args['host'])
app.generate_fakes(video=args['video'], picture=args['picture'], file_name=args['name'], )

