
import utils
import cv2

[camera_matrix, dist_matrix] = utils.load_coefficients('./calibration_chessboard.yml')

img = cv2.imread("./storage/chessboard-calibration/" + input("Chessboard Number: ") + ".png")

corrected_img = cv2.undistort(img, camera_matrix, dist_matrix, None, None)

cv2.imwrite("undistort.png", corrected_img)

