from src.chessboard import calibrate_chessboard
from utils import save_coefficients

# Parameters
IMAGES_DIR = '/home/pi/ball-hoop-picam/storage/chessboard-calibration'
IMAGES_FORMAT = 'png'
SQUARE_SIZE = 1.5
WIDTH = 9
HEIGHT = 6

# Calibrate
ret, mtx, dist, rvecs, tvecs = calibrate_chessboard(
    IMAGES_DIR,
    IMAGES_FORMAT,
    SQUARE_SIZE,
    WIDTH,
    HEIGHT
)
# Save coefficients into a file
save_coefficients(mtx, dist, "calibration_chessboard.yml")
