from src.chessboard import utils
import cv2


def main():
    [camera_matrix, dist_matrix] = utils.load_coefficients(
        '../../storage/chessboard-calibration/calibration_chessboard.yml')

    img = cv2.imread("./storage/chessboard-calibration/" + input("Chessboard Number: ") + ".png")

    height, width = img.shape[:2]

    newcameramatrix, _ = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_matrix, (width, height), 0.5, (width, height)
    )

    print(img.shape[:2])

    corrected_img = cv2.undistort(img, camera_matrix, dist_matrix, None, newcameramatrix)

    cv2.imwrite("undistort.png", corrected_img)


if __name__ == '__main__':
    main()
