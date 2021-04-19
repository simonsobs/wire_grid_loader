#!/usr/bin/python3

# Built-in python functions
import sys

# Check the python version
'''
if sy.version_info.major == 2:
    print(
        "\nstart_logging.py only works with Python 3\n"
        "Usage: python3 start_logging.py")
    sy.exit()
'''

# Import control modules
from src import LimitSwitch;
import limitswitch_config as config;


LS = LimistSwitch.LimitSwitch(config.GPIOpinInfo, logdir='./log', interval=1.);
LS.start_logging();
