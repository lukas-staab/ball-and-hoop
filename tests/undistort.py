import repackage
repackage.up()
from src.chessboard.utils import load_coefficients

coef = load_coefficients('../storage/chessboard-calibration/calibration_chessboard.yml')
print(coef)