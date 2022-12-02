import repackage
repackage.up()
import numpy
from src.chessboard.utils import load_coefficients
from src.ballandhoop import Image

[Image.camera_matrix, Image.dist_matrix] = load_coefficients('storage/chessboard-calibration/calibration_chessboard.yml')
im = Image.create('storage/chessboard-calibration/0.png')
im.apply_undistort(demo=True).save('storage/undistort', 'chess-0')
