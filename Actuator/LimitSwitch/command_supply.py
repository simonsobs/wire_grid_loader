#!/usr/bin/python3

# Built-in python functions
import sys
import readline

# Check the python version
# NOTE: Please change if after python3 installation
'''
if sys.version_info.major == 2:
    print(
        "\ncommand_supply.py only works with Python 3\n"
        "Usage: python3 command_supply.py")
    sys.exit()
'''

# Import control modules
from src import LimitSwitch;
import limitswitch_config as config;

# Initialize LimitSwitch reader
LS = LimitSwitch.LimitSwitch(config.GPIOpinInfo, logdir='./log', interval=1.);

# Check the arguments
if len(sys.argv) > 1:
    pinnames = [];
    for s in sys.argv[1:] :
        pinnames += s.split(',');
        pass;
    print(LS.get_onoff(pinnames));
else:
    while True:
        # Python2
        val = raw_input("Enter pinnames ('H' for help): ");
        # Python3
        # NOTE: Please change if after python3 installation
        #val = input("Enter pinnames ('H' for help): ");
        #print("input = {:s}".format(val));
        if val=="H" :
            print('There are the following pin names. Please enter pin names to check. (e.g. "LSR1", "LSR1,LSR2")');
            print(LS.pinnames);
            print('If you want to quit, please put Q(quit,exit).');
            continue;
        elif val in ['Q', 'quit', 'exit']:
            break;
        print(LS.get_onoff(val.split(',')));
        pass;
    pass;

