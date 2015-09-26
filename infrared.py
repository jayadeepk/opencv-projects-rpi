import time
import RPi.GPIO as GPIO
from sys import stdout

def detect(GPIO_IR):
    """Detect obstacle using Infrared sensor"""
    if GPIO.input(GPIO_IR):
        stdout.flush()
        stdout.write('Obstacle:  Yes\r')
    else:
        stdout.flush()
        stdout.write('Obstacle:  No \r')

GPIO_IR = 5
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_IR,GPIO.IN)

try:
    while(True):
        detect(GPIO_IR)
        time.sleep(0.1)
except KeyboardInterrupt:
  # User pressed CTRL-C
  # Reset GPIO settings
  GPIO.cleanup()

