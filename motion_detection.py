"""
Capture image using PiCamera without auto white balance and exposure
control. Use BackgroundSubtractorMOG2 of openCV to detect motion,
draw rectangles around each contour and display occupancy status along
with current time.
"""

from picamera import PiCamera
from picamera.array import PiRGBArray
import argparse
import cv2
import datetime
import imutils
import time

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

# parse argument for minimum area
ap = argparse.ArgumentParser()
ap.add_argument('-a', '--min-area',
                type=int, default=2000, help='minimum area size')
args = vars(ap.parse_args())

# detect motion using background subractor
subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

for capture in camera.capture_continuous(rawCapture, format='bgr',
                                         use_video_port=True):
    frame = capture.array
    text = 'Unoccupied'
    blurred = cv2.GaussianBlur(frame, (21, 21), 0)
    thresh = subtractor.apply(blurred)

    # dilate the thresholded image to fill in holes, then find contours
    dilated_thresh = cv2.dilate(thresh, None, iterations=2)
    (_, contours, _) = cv2.findContours(dilated_thresh.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # ignore if contour is smaller than minimum area
        if cv2.contourArea(c) < args['min_area']:
            continue
        # compute bounding rectangle for the contour and display it on frame
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = 'Occupied'

    # draw the text and timestamp on the frame
    color = (0, 0, 255) if text == 'Occupied' else (0, 255, 0)
    cv2.putText(frame, 'Room Status: {}'.format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(frame, datetime.datetime.now().strftime('%A %d %B %Y %I:%M:%S%p'),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show frame and quit when 'q' key is pressed
    cv2.imshow('Security Feed', frame)
    cv2.imshow('Thresh', thresh)
    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows()

