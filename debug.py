import argparse
import os
import sys

# setting paths for custom package and current working directory

directory = os.path.abspath(os.path.dirname(__file__))
os.chdir(directory)
sys.path.append(directory)

# definition of parameters which can be used
ap = argparse.ArgumentParser(description='This cmd line interface was build to help generate faker content')
ap.add_argument("-w", "--wb-gains", default=None, type=float, nargs=2,
                help="Enter custom wb_gains, if empty it will measure them")
ap.add_argument('-v', "--verbose", default=False, action='store_true',
                help='Give more output to console')
ap.add_argument('--vid', nargs='+', metavar=('name', 'amount', 'fps'))
ap.add_argument('--host', type=str, default=None,
                help='Forces a different hostname. Helpful for writing outside the real host')
args = vars(ap.parse_args())

from src.ballandhoop.application import Application

app = Application(verbose_output=args['verbose'], force_hostname=args['host'])
app.debug(save_vid=args['vid'], wb_gains=args['wb-gains'])

