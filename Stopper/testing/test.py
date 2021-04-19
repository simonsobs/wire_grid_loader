import time
import sys
import Adafruit_BBIO.GPIO as GPIO

on = (int)(sys.argv[1]);

GPIO.setup("P8_15",GPIO.OUT);
time.sleep(0.1);

if on :
    print('True');
    GPIO.output("P8_15",True);
else :
    print('False');
    GPIO.output("P8_15",False);
    pass;

print('End');
