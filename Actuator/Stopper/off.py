#!/usr/bin/python3

# Built-in python functions
import sys

# Check the python version
# NOTE: Please change if after python3 installation
''' 
if sys.version_info.major == 2:
    print(
        "\nstart_logging.py only works with Python 3\n"
        "Usage: python3 start_logging.py")
    sys.exit()
'''

# Import control modules
from src import Stopper;
import stopper_config as config;

# Initialize Stopper reader
stopper = Stopper.Stopper(config.GPIOpinInfo, logdir='./log');
stopper.set_alloff();
del stopper;
