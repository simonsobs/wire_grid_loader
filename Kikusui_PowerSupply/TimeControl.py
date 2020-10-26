#!/usr/bin/python3

# Built-in python functions
import sys
import time
from powerOn import parseCmdLine, powerOn

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

### main function ###
def TimeControl(voltagelim=0., currentlim=0., timeperiod=0., continuous=False):
    if continuous==True:
        powerOn(voltagelim, currentlim)
        pass
    else:
        for i in range(1):
            powerOn(voltagelim, currentlim, timeperiod, checkvalues=False)

### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)
    voltagelim = config.voltagelim
    currentlim = config.currentlim
    timeperiod = config.timeperiod
    checkvalues = config.checkvalues

    TimeControl(voltagelim, currentlim, timeperiod, continuous=False)
    pass
