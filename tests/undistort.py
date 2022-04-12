import repackage
repackage.up()
from src.chessboard.utils import load_coefficients
yml = open('storage/chessboard-calibration/calibration_chessboard.yml', "r").read()
print(yml)
[camera_matrix, dist_matrix] = load_coefficients('storage/chessboard-calibration/calibration_chessboard.yml')
print(camera_matrix)
