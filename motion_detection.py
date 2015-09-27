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
import os
import time

# parse arguments
ap = argparse.ArgumentParser()
ap.add_argument('-a', '--min-area',
                type=int, default=2000, help='minimum area size')
ap.add_argument('-r', '--no-record',
                help='do not record video', action='store_true')
ap.add_argument('-d', '--no-display',
                help='do not display video', action='store_true')
args = vars(ap.parse_args())
display, record = not args['no_display'], not args['no_record']
if not display and not record:
    print('Both arguments -r(--no-record) and -d(--no-display) cannot '
          'be used at once.')
    exit(1)

# picamera configuration
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
camera.awb_mode = 'off'
camera.awb_gains = (1.8, 1.8)
# Let digital and analog gain settle on higher values before
# turning exposure mode off
camera.shutterspeed = 30000
time.sleep(1)
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=(640, 480))


# create background subtractor and video writer
subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
if record:
    try:
        os.remove('capture.avi')
    except OSError:
        pass
    video_out = cv2.VideoWriter('capture.avi',
        cv2.VideoWriter_fourcc('X','V','I','D'), 5, camera.resolution)

try:
    for capture in camera.capture_continuous(rawCapture, format='bgr',
                                             use_video_port=True):
        frame = capture.array
        text = 'Unoccupied'
        blurred = cv2.GaussianBlur(frame, (21, 21), 0)
        thresh = subtractor.apply(blurred)

        # dilate the thresholded image to fill in holes and find contours
        dilated_thresh = cv2.dilate(thresh, None, iterations=2)
        (_, contours, _) = cv2.findContours(dilated_thresh.copy(),
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # ignore if contour is smaller than minimum area
            if cv2.contourArea(c) < args['min_area']:
                continue
            # draw bounding rectangle for contour
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = 'Occupied'

        # draw text and timestamp on frame
        color = (0, 0, 255) if text == 'Occupied' else (0, 255, 0)
        cv2.putText(frame, 'Room Status: {}'.format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(frame, datetime.datetime.now().strftime('%A %d %B %Y %I:%M:%S%p'),
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # show frame and quit when 'q' key is pressed
        if record:
            video_out.write(frame)
        if display:
            cv2.imshow('Security Feed', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                if record:
                    video_out.release()
                break
        rawCapture.truncate(0)

except KeyboardInterrupt:
    if record:
        video_out.release()
    exit(0)
