"""
Takes angles of horizontal motor and vertical motor as inputs
and rotates servo motors using pulses.
"""

from __future__ import division
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
        time.sleep(0.05)
    print('Pulse width in pin %d is %f' % (pin, pulse_width))

try:
    while True:
        print('Enter horizontal and vertical angles:  '),
        h, v = raw_input().split()
        h_angle, v_angle = int(h), int(v)

        turn(h_angle, H_PIN)
        turn(v_angle, V_PIN)
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
