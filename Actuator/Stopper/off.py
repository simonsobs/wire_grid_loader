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

# Initialize Stopper reader
stopper = Stopper.Stopper(config.GPIOpinInfo, logdir='./log');
stopper.set_alloff();
del stopper;
