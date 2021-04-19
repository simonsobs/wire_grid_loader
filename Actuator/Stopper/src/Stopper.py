# Built-in python modules
import time
import sys
import Adafruit_BBIO.GPIO as GPIO
import os

import binascii;
import struct;

from common import *;

class Stopper:
    """
    The Stopper object is for controlling the stopper ON/OFF via a beaglebone
    """

    def __init__(self, pinInfo, logdir='./log'):
        self.pinInfo    = pinInfo;
        self.pinnames   = [pin['name'] for pin in pinInfo];
        self.pinlabels  = [pin['label'] for pin in pinInfo];
        self.pinIndex   = {pin['name']:index for index, pin in enumerate(pinInfo)};
        self.pinDict    = {pin['name']:pin['pin'] for pin in pinInfo};
        self.logdir     = logdir;
        self.onoffs     = [False for pin in self.pinInfo];

        # initialize GPIO pins
        for pin in self.pinInfo :
            GPIO.setup(pin['pin'],GPIO.OUT);
            pass;
        # open log file
        self.log = Log(self.pinlabels, self.logdir);
        pass;

    def __del__(self):
        del self.log;
        return

    # Get ON/OFF of the pinname
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

    # Set ON/OFF of the pinname
    # pinname is a string of pin name or list of pin names
    # onoff = 0: OFF
    # onoff = 1: ON
    # If pinname = None, return the on/off for all the pins
    def set_onoff(self, onoff=0, pinname=None):
        setpinnames = [];
        if pinname is None :
            setpinnames = self.pinnames;
        elif isinstance(pinname, list): 
            if not all([(pinname0 in self.pinnames) for pinname0 in pinname ]) :
                print('ERROR! There is no GPIO pin names.');
                print('    Assigned pin names = {}'.format(self.pinnames));
                print('    Asked pin names    = {}'.format(pinname));
                return -1;
            setpinnames = self.pinname;
        else :
            if not (pinname in self.pinnames) :
                print('ERROR! There is no GPIO pin name of {}.'.format(pinname));
                print('    Assigned pin names = {}'.format(self.pinnames));
                return -1;
            setpinnames = [pinname];
            pass;
        print('Set {} for the pins: {}'.format('ON' if onoff else 'OFF', setpinnames));
        for name in setpinnames : 
            onoff_bool = True if onoff else False;
            GPIO.output(self.pinDict[name],onoff_bool);
            self.onoffs[self.pinIndex[name]] = onoff_bool;
            pass;
        self.log.writelog(self.onoffs);

        return 0;

    def set_allon(self) :
        print('Set ON for all of the stoppers.');
        self.set_onoff(1,None);
        return 0;

    def set_alloff(self) :
        print('Set OFF for all of the stoppers.');
        self.set_onoff(0,None);
        return 0;

    # Keep logging until stop=True
    def start_logging(self, stop=False):
        print('Start logging about stopper outputs.');
        while stop is False :
            #print('write log');
            onoffs = self.get_onoff();
            self.log.writelog(onoffs);
            pass;
        return 0;


