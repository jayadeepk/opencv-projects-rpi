import time
import RPi.GPIO as GPIO

def measure():
  """Measure distance using Ultrasonic sensor"""
  GPIO.output(GPIO_TRIGGER, GPIO.HIGH)
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, GPIO.LOW)
  start = time.time()

  while GPIO.input(GPIO_ECHO)==GPIO.LOW:
    start = time.time()

  while GPIO.input(GPIO_ECHO)==GPIO.HIGH:
    stop = time.time()

  elapsed = stop-start
  distance = (elapsed * 34300)/2

  return distance

# -----------------------
# Main Script
# -----------------------

GPIO.setmode(GPIO.BOARD)

# Define GPIO to use on Pi
GPIO_TRIGGER = 3
GPIO_ECHO    = 5

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

try:
  while True:
    distance = measure()
    print "Distance : %.1f" % distance
    time.sleep(0.5)
except KeyboardInterrupt:
  # User pressed CTRL-C
  # Reset GPIO settings
  GPIO.cleanup()
