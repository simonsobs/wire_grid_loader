#!/usr/bin/python3

# Built-in python functions
import sys
import time
import numpy as np
import datetime
from src.common import *
from Ether_basic import *

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

logfile = openlog('log_ether')
#file_path = '/home/wire-grid-pc/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

Deg = 360/52000

### main function ###
def Checks(voltagelim=12.,
            currentlim=3.,
            notmakesure=False,
            initializing_option=0):
    if voltagelim != 12.:
        print("the rated Voltage of this motor DMN37KA is 12V.\n")
        sys.exit(1)
        pass

    default_control(voltagelim, 3., 5.01)
    time.sleep(10)
    start_position = getPosition(file_path)*Deg
    start_time = time.time()
    startStr = datetime.datetime.fromtimestamp(start_time).strftime('%Y/%m/%d %H:%M:%S')

    if initializing_option == 0: # matrix
        print('check the minimal control-angle under these condition:\n\
            voltage_lim=12V, current_lim={}, time_period;0.10sec ~ 0.30sec(delta 0.02sec)\n\
            positon={}, start at {}\n'.format(currentlim, round(start_position,3), startStr))

        curlim = currentlim
        for i in range(11):
            tperiod = 0.10 + 0.02(i+1)
            for k in range(2):
                turn_on(notmakesure=notmakesure)
                writelog(logfile, 'ON', voltagelim=12., currentlim=curlim, timeperiod=tperiod, position=position, notmakesure=notmakesure)
                time.sleep(tperiod)
                turn_off(notmakesure=notmakesure)
                writelog(logfile, 'OFF', voltagelim=12., currentlime=curlim, notmakesure=notmakesure)

                time.sleep(2)

                default_control(voltagelim, 3., 0.5)
                time.sleep(3)
                pass
            default_control(voltagelim, 3., 1)
            time.sleep(3)

        pass

    elif initializing_option == 1: # check the minimal control andgle
        print('check the minimal control-angle under these condition:\n\
            matrix Ampere;1.5A ~ 3.0A(delta 0.3A), time;0.4sec ~ 2.4sec(delta 0.4sec)\n\
            positon={}, start at {}\n'.format(round(start_position,3), startStr))

        for i in range(6):
            curlim = 1.5 + 0.3*i
            for j in range(6):
                tperiod = 0.4 + 0.4*j
                for k in range(2):
                    turn_on(notmakesure=notmakesure)
                    writelog(logfile, 'ON', voltagelim=12., currentlim=curlim, timeperiod=tperiod, position=position, notmakesure=notmakesure)
                    time.sleep(tperiod)
                    turn_off(notmakesure=notmakesure)
                    writelog(logfile, 'OFF', voltagelim=12., currentlim=curlim, notmakesure=notmakesure)

                    time.sleep(2)

                    default_control(voltagelim, 3., 0.5)
                    time.sleep(3)
                    pass
                time.sleep(3)
                pass
            default_control(voltagelim, 3., 1)
            time.sleep(3)
        pass

    stop_time = time.time()
    print(f'measurement time is {stop_time - start_time} sec')
    pass

def default_control(voltagelim, currentlim, timeperiod, position=0., notmakesure=False):
    msg_vollim, vollim = set_voltage(voltagelim)
    msg_curlim, curlim = set_current(currentlim)
    print(msg_vollim + '\n' + msg_curlim)
    msg_output = turn_on(notmakesure=notmakesure)
    print(msg_output)
    msg_vol, vol = check_voltage()
    msg_cur, cur = check_current()
    writelog(logfile, 'ON', vollim, curlim, vol, cur, position=position, timeperiod=timeperiod)
    time.sleep(timeperiod)
    msg_output = turn_off(notmakesure=notmakesure)
    print(msg_output)
    pass

### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)

    curlim = config.currentlim
    init_op = config.initializing_option

    Checks(vollim=12., curlim, notmakesure=True, init_op)
    pass