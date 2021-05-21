# Built-in python modules
import time
import sys
import Adafruit_BBIO.GPIO as GPIO
import os

import binascii;
import struct;

from .log_limitswitch import Log;

class LimitSwitch:
    """
    The LimitSwitch object is for detecting the limit switch ONOFF via a beaglebone
    """

    def __init__(self, pinInfo, logdir='./log'):
        self.pinInfo    = pinInfo;
        self.pinnames   = [pin['name'] for pin in pinInfo];
        self.pinlabels  = [pin['label'] for pin in pinInfo];
        self.pinIndex   = {pin['name']:index for index, pin in enumerate(pinInfo)};
        self.pinDict    = {pin['name']:pin['pin'] for pin in pinInfo};
        self.logdir     = logdir;

        # initialize GPIO pins
        for pin in self.pinInfo :
            GPIO.setup(pin['pin'],GPIO.IN,pull_up_down=GPIO.PUD_UP);
            pass;
        # open log file
        self.log = Log(self.pinlabels, self.logdir);
        pass;

    def __del__(self):
        del self.log;
        return

    # pinname is a string of pin name or list of pin names
    # return single int or list of int
    #   0 : OFF
    #   1 : ON 
    # If pinname = None, return the on/off for all the pins
    def get_onoff(self, pinname=None):
        if pinname is None :
            ret =  [ 0 if GPIO.input(self.pinDict[pinname0]) else 1 for pinname0 in self.pinnames ];
        elif isinstance(pinname, list): 
            if not all([(pinname0 in self.pinnames) for pinname0 in pinname ]) :
                print('ERROR! There is no GPIO pin names.');
                print('    Assigned pin names = {}'.format(self.pinnames));
                print('    Asked pin names    = {}'.format(pinname));
                return -1;
            ret =  [ 0 if GPIO.input(self.pinDict[pinname0]) else 1 for pinname0 in pinname ];
        else :
            if not (pinname in self.pinnames) :
                print('ERROR! There is no GPIO pin name of {}.'.format(pinname));
                print('    Assigned pin names = {}'.format(self.pinnames));
                return -1;
            ret =  0 if GPIO.input(self.pinDict[pinname]) else 1;
            pass;
        return ret;


    # Keep logging until stop=True
    # interval : time interval to write log [sec]
    # The defaut interval is 1sec
    def start_logging(self, stop=False, interval=1.):
        print('Start logging about limit switch outputs. (interval={} sec)'.format(interval));
        while stop is False :
            #print('write log');
            onoffs = self.get_onoff();
            self.log.writelog(onoffs);
            time.sleep(interval);
            pass;
        return 0;


