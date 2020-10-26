#!/usr/bin/python3

# Built-in python functions
import sys
import time
from powerOn import powerOn, parseCmdLine

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

### main function ###
def TimeControl(voltagelim=0., currentlim=0., timeperiod=0., notmakesure=True):
    if timeperiod > 0.:
        for i in range(1):
            powerOn(voltagelim, currentlim, timeperiod, notmakesure=True)
            pass
        pass
    else:
        print("This is a script to measure the relation between operation time of power supply and proceeded angle.")

### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)
    voltagelim = config.voltagelim
    currentlim = config.currentlim
    timeperiod = config.timeperiod
    notmakesure = config.notmakesure

    TimeControl(voltagelim, currentlim, timeperiod, notmakesure)
    pass
