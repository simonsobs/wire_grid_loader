#!/usr/bin/python3

# Built-in python functions
import sys
import readline

# Check the python version
if sys.version_info.major == 2:
    print(
        "\ncommand_supply.py only works with Python 3\n"
        "Usage: python3 command_supply.py")
    sys.exit()

# Import control modules
from src import Stopper;
import stopper_config as config;

# Initialize Stopper reader
stopper = Stopper.Stopper(config.GPIOpinInfo, logdir='./log');

# Interactive mode
while True:
    # Python2
    #val = raw_input("Enter pinnames ('H' for help): ");
    # Python3
    val = input("Enter pinnames ('H' for help): ");

    #print("input = {:s}".format(val));
    if val=='H' :
        print('Commands: ON(=True=1), OFF(=False=0), Q(=quit=exit)');
    elif val in ['ON', True, '1']:
        stopper.set_allon();
    elif val in ['OFF', False, '0']:
        stopper.set_alloff();
    elif val in ['Q', 'quit', 'exit']:
        break;
    else :
        print('ERROR! Unknown command: {}'.format(val));
        pass;
    pass;

