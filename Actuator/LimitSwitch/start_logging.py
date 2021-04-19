#!/usr/bin/python3

# Built-in python functions
import sys
# To kill this script by Ctrl+C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

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
from src import LimitSwitch;
import limitswitch_config as config;


LS = LimitSwitch.LimitSwitch(config.GPIOpinInfo, logdir='./log', interval=1.);
LS.start_logging();
