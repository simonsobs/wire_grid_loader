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
position_file_path = '/home/wire-grid-pc/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

Deg = 360/52000
wanted_angle = 22.5
with open('feedback_amount.txt','r') as f:
    feedback_amount = (f.readlines())[-1].replace('\n', '').split(' ')
    feedback_time = [float(feedback_amount[1]), float(feedback_amount[2]), float(feedback_amount[3]), float(feedback_amount[4]), float(feedback_amount[5])]
    pass
print(feedback_time)
feedback_cut = [1.0, 3.0, 4.0, 5.0, 6.0]

### main function ###
def Controls(voltagelim=12.,
            currentlim=3.,
            control_type=False,
            timeperiod=10.,
            num_laps=10,
            num_feedback=8,
            stopped_time=10.,
            notmakesure=False):
    if voltagelim != 12.:
        print("the rated Voltage of this motor DMN37KA is 12V.\n")
        sys.exit(1)
        pass
    start_str, stop_str = default_control(12., 3., 5.01)
    writeitem(itemfile, start_str, 'measurement', 'start')
    time.sleep(30)
    start_position = getPosition(position_file_path)*Deg
    start_time = time.time()
    startStr = datetime.datetime.fromtimestamp(start_time).strftime('%Y/%m/%d %H:%M:%S')
    if control_type == True: # stepwise rotation
        print('start stepwise rotation under these condition:\n\
number of laps = {}, number of feedbacks = {}\n\
positon={}, start at {}\n'.format(num_laps, num_feedback, round(start_position,3), startStr))
        cycle = 1
        for i in range(num_laps*int(360/wanted_angle)):
            stop_str = feedbackfunction(3.0, 0.401, num_feedback, notmakesure=True)
            time.sleep(stopped_time)
            cycle += 1
            pass
        pass
    else: # continuous rotation
        if(currentlim > 3.):
            print("Please set the current to 3.0 A or less")
            sys.exit(1)
            pass
        else:
            print('start continuous rotation under these condition:\n\
voltagelim={}, currentlim={}, timeperiod={}, makesure_voltage_and_current={}\n\
positon={}, start_time={}\n'.format(voltagelim, currentlim, timeperiod, not notmakesure, round(start_position,3), startStr))
            start_str, stop_str = default_control(voltagelim, currentlim, timeperiod, position=start_position, notmakesure=notmakesure)
            writeitem(itemfile, start_str, 'measurement', 'start')
            pass
        pass
    writeitem(itemfile, stop_str, 'measurement', 'stop')
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
    date_str0 = writelog(logfile, 'ON', vollim, curlim, vol, cur, position=position, timeperiod=timeperiod)
    time.sleep(timeperiod)
    msg_output = turn_off(notmakesure=notmakesure)
    date_str1 = writelog(logfile, 'OFF', voltagelim, currentlim)
    print(msg_output)
    return date_str0, date_str1

def feedback_control(voltagelim, currentlim, timeperiod, position, notmakesure=True):
    turn_on(notmakesure=notmakesure)
    writelog(logfile, 'ON', voltagelim, currentlim, timeperiod=timeperiod, position=position, notmakesure=notmakesure)
    time.sleep(timeperiod)
    turn_off(notmakesure=notmakesure)
    date_str1 = writelog(logfile, 'OFF', voltagelim, currentlim, notmakesure=notmakesure)
    return date_str1

def feedbackfunction(operation_current, operation_time, feedback_loop, notmakesure):
    uncertaity_cancel = 3
    absolute_position = np.arange(0,360,wanted_angle)

    start_position = getPosition(position_file_path)*Deg
    if (360 < start_position + uncertaity_cancel):
        goal_position = wanted_angle
        pass
    elif absolute_position[-1] < start_position + uncertaity_cancel:
        goal_position = 0
        pass
    else:
        goal_position = min(absolute_position[np.where(start_position + uncertaity_cancel < absolute_position)[0]])
        pass
    print('start: {}, goal: {}'.format(round(start_position,3), round(goal_position,3)))
    feedback_control(voltagelim, operation_current, operation_time, position=start_position, notmakesure=notmakesure)
    time.sleep(0.4)
    for l in range(feedback_loop):
        mid_position = getPosition(position_file_path)*Deg
        if goal_position + wanted_angle < mid_position:
            operation_time = howlong(goal_position - (mid_position - 360))
            pass
        else:
            operation_time = howlong(goal_position - mid_position)
            pass
        date_str1 = feedback_control(voltagelim, operation_current, operation_time, position=mid_position, notmakesure=notmakesure)
        time.sleep(0.4)
        pass
    return date_str1

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

def howlong(position_difference):
    if position_difference >= feedback_cut[4]:
        operation_time = feedback_time[4]
        pass
    if (feedback_cut[4] > position_difference) & (position_difference >= feedback_cut[3]):
        operation_time = feedback_time[3]
        pass
    if (feedback_cut[3] > position_difference) & (position_difference >= feedback_cut[2]):
        operation_time = feedback_time[2]
        pass
    if (feedback_cut[2] > position_difference) & (position_difference >= feedback_cut[1]):
        operation_time = feedback_time[1]
        pass
    if (feedback_cut[1] > position_difference) & (position_difference >= feedback_cut[0]):
        operation_time = feedback_time[0]
        pass
    if feedback_cut[0] > position_difference:
        operation_time = 0.001
        pass
    return operation_time


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

    if timeperiod <= 0.:
        timeperiod = 10.
        pass

    Controls(voltagelim, currentlim, control_type, timeperiod, num_laps, num_feedback, stopped_time, notmakesure)
    pass