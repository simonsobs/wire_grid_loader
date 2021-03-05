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
itemfile = openlog('item', verbose=1)
file_path = '/home/wire-grid-pc/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

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

    print('working fine, stay a few second!')

    if initializing_option == 0:
        item_value = 'calibration'
        pass
    elif initializing_option == 1:
        item_value = 'matrix'

    start_str, stop_str = default_control(voltagelim, 3., 5.01)
    writeitem(itemfile, start_str, item_value, 'start')
    time.sleep(10)
    start_position = getPosition(file_path)*Deg
    start_time = time.time()
    startStr = datetime.datetime.fromtimestamp(start_time).strftime('%Y/%m/%d %H:%M:%S')

    if initializing_option == 0: # confirm the minimal control angle
        print('check the minimal control-angle under these condition:\n\
voltage_lim=12V, current_lim={}A, time_period;0.10sec ~ 0.30sec(delta 0.02sec)\n\
positon={}, start at {}\n'.format(currentlim, round(start_position,3), startStr))

        cycle = 1
        curlim = currentlim
        for i in range(11):
            tperiod = 0.10 + 0.02*i
            for k in range(100):
                print(f'num_cycle {cycle}')

                check_control(voltagelim, curlim, tperiod, notmakesure=True)

                time.sleep(2)

                start_str, stop_str = default_control(voltagelim, 3., 0.5)
                time.sleep(2)
                cycle += 1
                pass
            time.sleep(1)

        pass

    elif initializing_option == 1: # check the matrix
        print('check the minimal control-angle under these condition:\n\
matrix Ampere;1.5A ~ 3.0A(delta 0.3A), time;0.4sec ~ 2.4sec(delta 0.4sec)\n\
positon={}, start at {}\n'.format(round(start_position,3), startStr))

        cycle = 1
        for i in range(6):
            curlim = 1.5 + 0.3*i
            for j in range(6):
                tperiod = 0.4 + 0.4*j
                for k in range(100):
                    print(f'num_cycle {cycle}')

                    check_control(voltagelim, curlim, tperiod, notmakesure=True)

                    time.sleep(2)

                    default_control(voltagelim, 3., 0.5)
                    time.sleep(2)
                    cycle += 1
                    pass
                time.sleep(2)
                pass
            start_str, stop_str = default_control(voltagelim, 3., 1)
            time.sleep(2)
        pass

    writeitem(itemfile, stop_str, item_value, 'stop')
    stop_time = time.time()
    print(f'measurement time is {stop_time - start_time} sec')
    pass

def default_control(voltagelim, currentlim, timeperiod, position=0., notmakesure=False):
    msg_vollim, vollim = set_voltage(voltagelim)
    msg_curlim, curlim = set_current(currentlim)
    msg_output = turn_on(notmakesure=notmakesure)
    #print(msg_output)
    msg_vol, vol = check_voltage()
    msg_cur, cur = check_current()
    date_str0 = writelog(logfile, 'ON', voltagelim, curlim, vol, cur, position=position, timeperiod=timeperiod)
    time.sleep(timeperiod)
    msg_output = turn_off(notmakesure=notmakesure)
    date_str1 = writelog(logfile, 'OFF', voltagelim, currentlim)
    #print(msg_output)
    return date_str0, date_str1

def check_control(voltagelim, currentlim, timeperiod, notmakesure=True):
    msg_curlim, curlim = set_current(currentlim)
    print('    ' + msg_curlim)
    print(f'    Time set = {round(timeperiod,3)}')
    turn_on(notmakesure=notmakesure)
    writelog(logfile, 'ON', voltagelim, currentlim, timeperiod=timeperiod, notmakesure=notmakesure)
    time.sleep(timeperiod)
    turn_off(notmakesure=notmakesure)
    writelog(logfile, 'OFF', voltagelim, currentlim, notmakesure=notmakesure)
    pass

def getPosition(filepath):
    for i in range(10):
        try:
            f = open(filepath, 'r')
            data = f.readlines()
            f.close()
            position = data[0]
        except IndexError:
            time.sleep(0.1)
            continue
        break
    return float(position)

### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)

    voltagelim = config.voltagelim
    currentlim = config.currentlim
    control_type = config.control_type
    timeperiod = config.timeperiod
    num_laps = config.num_laps
    num_feedback = config.num_feedback
    stopped_time = config.stopped_time
    notmakesure = config.notmakesure
    init_op = config.initializing_option

    Checks(voltagelim, currentlim, notmakesure=True, initializing_option=init_op)
    pass