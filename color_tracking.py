"""
Take lower and upper bounds of hue as arguments. Capture video using
PiCamera without auto white balance and exposure control. Threshold for 
required color and find center of largest contour. Print center and the
quadrant (up/down, left/right) in which the center lies. Display video
with rectangle around contour.
"""

from picamera import PiCamera
from picamera.array import PiRGBArray
import argparse
import cv2
import numpy as np
import time
from sys import stdout

# parse arguments
ap = argparse.ArgumentParser()
ap.add_argument('-l', '--lower-hue',
                type=int, default=30, help='lower bound for hue')
ap.add_argument('-u', '--upper-hue',
                type=int, default=110, help='upper bound for hue')
args = vars(ap.parse_args())
if (args['lower_hue'] < 0 or args['lower_hue'] > 239 or
    args['upper_hue'] < 0 or args['upper_hue'] > 239):
    print('Hue should be a number between 0 and 239.')
    exit(1)
if not args['lower_hue'] < args['upper_hue']:
    print('Lower bound for hue should be less than upper bound.')
    exit(1)

# picamera configuration
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
camera.awb_mode = 'off'
camera.awb_gains = (1.8, 1.8)
# Let digital and analog gain settle on higher values before
# turning exposure mode off
time.sleep(1)
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)
 
for capture in camera.capture_continuous(rawCapture, format="bgr",
                                       use_video_port=True):
    frame = capture.array
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([args['lower_hue'], 50, 50], dtype=np.uint8)
    upper_bound = np.array([args['upper_hue'],255,255], dtype=np.uint8)

    # Threshold the HSV image for required hue
    thresh = cv2.inRange(hsv, lower_bound, upper_bound)
    dilated_thresh = cv2.dilate(thresh, None, iterations=2)

    (_, contours, _) = cv2.findContours(dilated_thresh.copy(),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find largest contour
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area < 1000 or area < max_area:
            continue
        max_area = area
        contour = c

    # get center of contour and the quadrant in which center lies
    h_move, v_move = '      ', '      '
    cx, cy = 0, 0
    if max_area != 0:
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        (cx, cy) = (x+w/2, y+h/2)
        if cx < 300:
            h_move = 'Left  '
        elif cx > 340:
            h_move = 'Right '
        if cy < 220:
            v_move = 'Up    '
        elif cx > 260:
            v_move = 'Down  '
    stdout.flush()
    stdout.write('%s %s      Center:  %d %d      \r' % (h_move, v_move, cx, cy))

    cv2.imshow('frame', frame)
    cv2.imshow('thresh', thresh)
    k = cv2.waitKey(5) & 0xFF
    rawCapture.truncate(0)
    if k == 27:
        break
cv2.destroyAllWindows()
