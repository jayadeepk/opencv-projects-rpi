"""
Captures video using Raspberry Pi camera and displays video stream
with mean threshold filter applied.
"""

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
 
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
time.sleep(0.1)
 
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = cv2.cvtColor(frame.array, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(img, 3)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    cv2.imshow("Frame", img)
    key = cv2.waitKey(1) & 0xFF
 
    rawCapture.truncate(0)
    if key == ord("q"):
        break
