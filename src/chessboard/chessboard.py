import cv2
import numpy as np
import pathlib


def calibrate_chessboard(dir_path, image_format, square_size, width, height):
    """Calibrate a camera using chessboard images."""
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    objp = np.zeros((height * width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    path = pathlib.Path(dir_path)
    images = path.glob(f'*.{image_format}')
    print("Path exists? -> " + str(path.exists()))
    # Iterate through all images
    gray = []
    for fname in images:
        img = cv2.imread(str(fname))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        # print(gray.shape[::-1])
        print("Try to find chessboardcorners from " + str(fname))
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)
        print(ret)
        # If found, add object points, image points (after refining them)
        if ret:
            print("found!")
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    # Calibrate camera
    print("Calculate Camera Calibration")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return [ret, mtx, dist, rvecs, tvecs]
