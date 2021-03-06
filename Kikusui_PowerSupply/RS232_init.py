#!/usr/bin/python3

# Built-in python functions
import os
import sys
import time
import readline
import numpy as np
from datetime import datetime
from powerOn import powerOn

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

# Import control modules
import pmx_config as cg  # noqa: E402
import src.pmx as pm  # noqa: E402

from src.common import * # writelog(), openlog(), parseCmdLine()

logfile = openlog(cg.log_dir)
file_path = '/home/wire-grid-pc/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

Deg = 360/52000

### main function ###
def RS232_init(voltagelim=12.,
            currentlim=3.,
            notmakesure=False,
            initializing_option=0):
    if voltagelim != 12.:
        print("the rated Voltage of this motor DMN37KA is 12V.\n")
        sys.exit(1)
        pass

    PMX = connection_func()
    control_func(PMX, voltagelim, 3., 5.01)

    print('working fine, stay a few second!')
    time.sleep(10)
    start_position = getPosition(file_path)*Deg
    start_time = time.time()
    startStr = datetime.datetime.fromtimestamp(start_time).strftime('%Y/%m/%d %H:%M:%S')

    if initializing_option == 0: # confirm the minimal control angle
        print('\ncheck the minimal control-angle under these condition:\n\
voltage_lim=12V, current_lim={}A, time_period;0.10sec ~ 0.30sec(delta 0.02sec)\n\
positon={}, start at {}\n'.format(currentlim, round(start_position,3), startStr))

        cycle = 1
        curlim = currentlim
        for i in range(11):
            tperiod = 0.10 + 0.02*i
            for k in range(2):
                print(f'\nnum_cycle {cycle}')

                control_func(PMX, voltagelim, curlim, tperiod, notmakesure=True)

                time.sleep(2)

                control_func(PMX, voltagelim, 3., 0.5)
                time.sleep(2)
                cycle += 1
                pass
            time.sleep(1)

        pass

    elif initializing_option == 1: # check the matrix
        print('\ncheck the minimal control-angle under these condition:\n\
matrix Ampere;1.5A ~ 3.0A(delta 0.3A), time;0.4sec ~ 2.4sec(delta 0.4sec)\n\
positon={}, start at {}\n'.format(round(start_position,3), startStr))

        cycle = 1
        for i in range(6):
            curlim = 1.5 + 0.3*i
            for j in range(6):
                tperiod = 0.4 + 0.4*j
                for k in range(2):
                    print(f'\nnum_cycle {cycle}')

                    control_func(PMX, voltagelim, curlim, tperiod, notmakesure=True)

                    time.sleep(2.5)

                    control_func(PMX, voltagelim, 3., 0.5)
                    time.sleep(2)
                    cycle += 1
                    pass
                time.sleep(2)
                pass
            control_func(PMX, voltagelim, 3., 1)
            time.sleep(2)
        pass

    stop_time = time.time()
    print(f'measurement time is {stop_time - start_time} sec')
    pass

def connection_func(PMX=None):
    # Connect to PMX power supply
    if PMX==None :
        if cg.use_moxa:
            PMX = pm.PMX(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5)
        else:
            PMX = pm.PMX(rtu_port=cg.rtu_port)
            pass
        pass
    PMX.clean_serial()
    return PMX

def control_func(PMX, voltagelim, currentlim, timeperiod=0.1, position=0., notmakesure=False):

    # Set voltage & current
    msg_vollim = PMX.set_voltage(voltagelim)
    msg_curlim = PMX.set_current(currentlim)

    if notmakesure==False:
        # Turn On
        msg_output = PMX.turn_on(notmakesure)
        msg_vol, vol = PMX.check_voltage()
        msg_cur, cur = PMX.check_current()
        writelog(logfile, 'ON', voltagelim, currentlim, vol, cur, timeperiod)

        time.sleep(timeperiod)

        msg_output = PMX.turn_off(notmakesure)
        vollim, curlim = PMX.check_voltage_current_limit()
        vol   , cur    = PMX.check_voltage_current()
        writelog(logfile, 'OFF', vollim, curlim, vol, cur)
        pass
    else:
        PMX.turn_on(notmakesure)
        writelog(logfile, 'ON', voltagelim, currentlim, timeperiod=timeperiod, position=position, notmakesure=notmakesure)

        time.sleep(timeperiod)

        PMX.turn_off(notmakesure)
        writelog(logfile, 'OFF', voltagelim, currentlim, notmakesure=notmakesure)
        pass
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

    RS232_init(voltagelim, currentlim, notmakesure=True, initializing_option=init_op)
    pass