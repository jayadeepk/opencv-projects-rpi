"""
Captures image using Raspberry Pi camera and outputs images with mean
and gaussian threshold filters applied.
"""

import cv2 as cv
import numpy as np
import picamera
import time

cam = picamera.PiCamera()
time.sleep(5)
cam.capture('test.jpg')


img = cv.imread('test.jpg', cv.IMREAD_GRAYSCALE)
img = cv.medianBlur(img, 5)

mean = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C,
                            cv.THRESH_BINARY, 11, 2)
gauss = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                             cv.THRESH_BINARY, 11, 2)

cv.imwrite('mean.jpg', mean)
cv.imwrite('gauss.jpg', gauss)

