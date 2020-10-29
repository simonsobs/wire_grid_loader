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
def TimeControl(voltagelim=0., currentlim=0., timeperiod=0., notmakesure=False):
    if notmakesure==False:
        print("Sorry, this script still cannot meet the request. please add '-n' option")
        pass
    else:
        if voltagelim != 12.:
            print("the rated Voltage of this motor DMN37KA is 12V")
            sys.exit(1)
        if timeperiod > 0.:
            for i in range(1):
                for j in range(6):
                    operation_current = currentlim * (i+1)
                    operation_time = timeperiod * (j+1)
                    num_execution = 10
                    if operation_current > 3.0:
                        print("operation current is over a range from 0. to 3.0")
                        sys.exit(1)
                    for k in range(int(num_execution)):
                        powerOn(voltagelim, operation_current, operation_time, notmakesure=True)
                        time.sleep(1.5)
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
