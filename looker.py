"""
Take lower and upper bounds of hue as arguments. Capture video using
PiCamera without auto white balance and exposure control. Threshold for 
required color and find center of largest contour. Rotates servo motors
towards the center.
"""

from __future__ import division
from picamera.array import PiRGBArray
from sys import stdout
import argparse
import cv2
import io
import numpy as np
import picamera
import RPi.GPIO as GPIO
import time

H_PIN = 3       # GPIO pin for horizontal motor
V_PIN = 5       # GPIO pin for vertical motor

GPIO.setmode(GPIO.BOARD)
GPIO.setup(H_PIN, GPIO.OUT)
GPIO.setup(V_PIN, GPIO.OUT)

def turn(angle, pin):
    if angle < -90 or angle > 90:
        print('Angle should be in range -90 to 90.')
        return
    pulse_width = float('%.5f' % (((angle+90)/90 + 0.5)/1000))

    for i in range(6):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(pulse_width)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.03)

#-----------------------------------------------------------------------
#   Main Code
#-----------------------------------------------------------------------

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
camera = picamera.PiCamera()
camera.resolution = (160, 120)
camera.awb_mode = 'off'
camera.awb_gains = (1.8, 1.8)
# Let digital and analog gain settle on higher values before
# turning exposure mode off
time.sleep(1)
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=(160, 120))
time.sleep(0.1)

h_angle, v_angle = 0, 45
turn(h_angle, H_PIN)
turn(-1 * v_angle, V_PIN)
time.sleep(0.5)

try:
    for capture in camera.capture_continuous(rawCapture, format="bgr",
                                             use_video_port=True):
        frame = capture.array
        rawCapture.truncate(0)
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
            if area < 100 or area < max_area:
                continue
            max_area = area
            contour = c

        # get center of contour and the quadrant in which the center lies
        h_move, v_move = 0, 0
        cx, cy = 0, 0
        if max_area != 0:
            (x, y, w, h) = cv2.boundingRect(contour)
            (cx, cy) = (x+w/2, y+h/2)
            if cx < 60:
                h_move = -1
            elif cx > 100:
                h_move = 1
            if cy < 40:
                v_move = 1
            elif cy > 80:
                v_move = -1

        if h_angle > -45 and h_move == 1: h_angle = h_angle - 10
        elif h_angle < 45 and h_move == -1: h_angle = h_angle + 10

        if v_angle < 90 and v_move == 1: v_angle = v_angle + 10
        elif v_angle > 20 and v_move == -1: v_angle = v_angle - 10

        print('center', cx , cy)
        print(h_move, v_move)
        print(h_angle, v_angle)
        if h_move != 0:
            turn(h_angle, H_PIN)
        if v_move != 0:
            turn(-1 * v_angle, V_PIN)
except KeyboardInterrupt:
    pass
GPIO.cleanup()
cv2.destroyAllWindows()
