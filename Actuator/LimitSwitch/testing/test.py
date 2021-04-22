import time
import sys
import Adafruit_BBIO.GPIO as GPIO

tsleep = 0.1;
GPIO.setup("P8_7",GPIO.IN,pull_up_down=GPIO.PUD_UP);
GPIO.setup("P8_11",GPIO.IN,pull_up_down=GPIO.PUD_UP);
time.sleep(0.1);

while True :
    val1 =  'OFF' if GPIO.input("P8_7" ) else 'ON';
    val2 =  'OFF' if GPIO.input("P8_11") else 'ON';
    print('input1 = {} / input2 =  {}'.format(val1,val2));
    time.sleep(tsleep);
    pass;

print('End');
