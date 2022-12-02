import time

import cv2

#img = cv2.imread('storage/cheat1.png')
# img = cv2.blur(img, (10, 10))
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# _, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
# img = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, None)



raw_image = cv2.imread('../fetch/rpi2.lan/calibration/raw-rgb.png')
cv2.imshow('Original Image', raw_image)
cv2.waitKey(0)

bilateral_filtered_image = cv2.bilateralFilter(raw_image, 5, 175, 175)
cv2.imshow('Bilateral', bilateral_filtered_image)
cv2.waitKey(0)

edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)
cv2.imshow('Edge', edge_detected_image)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

contour_list = []
for contour in contours:
    approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
    area = cv2.contourArea(contour)
    if ((len(approx) > 8) & (len(approx) < 23) & (area > 30) ):
        contour_list.append(contour)

cv2.drawContours(raw_image, contour_list,  -1, (255,0,0), 2)
cv2.imshow('Objects Detected',raw_image)
cv2.imwrite('../edges.png', edge_detected_image)
cv2.imwrite('../edge-detect.png', raw_image)
cv2.waitKey(0)

