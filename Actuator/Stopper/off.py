#!/usr/bin/python3

# Built-in python functions
import sys

# Check the python version
if sys.version_info.major == 2:
    print(
        "\noff.py only works with Python 3\n"
        "Usage: python3 off.py")
    sys.exit()

# Import control modules
from src import Stopper;
import stopper_config as config;

def off(stopper=None) :
    # Initialize Stopper reader
    if stopper is None : stopper = Stopper.Stopper(config.GPIOpinInfo, logdir='./log');
    stopper.set_alloff();
    return stopper;

if __name__=='__main__' :
    stopper = off();
    del stopper;
    pass;   
