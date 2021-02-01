#!/usr/bin/python3

# Built-in python functions
import sys
import time
from datetime import datetime
import numpy as np
from powerOn import powerOn
from src.common import parseCmdLine

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

file_path = '/home/kyoto/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

Deg = 360/52000
feedback_time = [0.181, 0.221, 0.251, 0.281, 0.301]
feedback_cut = [0.5, 2.5, 4.5, 6.0, 7.0]

### main function ###
def Controls(voltagelim=12.,
            currentlim=3.,
            control_type=False,
            timeperiod=10.,
            num_laps=10,
            num_feedback=8,
            stopped_time=30.,
            notmakesure=False):
    if voltagelim != 12.:
        print("the rated Voltage of this motor DMN37KA is 12V.\n")
        sys.exit(1)
        pass
    powerOn(12., 3., 5.01, notmakesure=True)
    time.sleep(3)
    start_position = getPosition(file_path)*Deg
    start_time = time.time()
    startStr = datetime.fromtimestamp(start_time).strftime('%Y/%m/%d %H:%M:%S')
    if control_type == True: # discrete rotation
        print('start discrete rotation under these condition:\n\
                number of laps = {}, number of feedbacks = {}\n\
                positon={}, start at {}\n'.format(num_laps, num_feedback, round(start_position,3), startStr))
        cycle = 1
        for i in range(num_laps):
            feedbackfunction(3.0, 0.401, num_feedback, notmakesure=True)
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
            powerOn(voltagelim, currentlim, timeperiod, position=start_position, notmakesure=notmakesure)
            pass
        pass
    stop_time = time.time()
    print(f'measurement time is {stop_time - start_time} sec')
    pass


def feedbackfunction(operation_current, operation_time, feedback_loop, notmakesure):
    wanted_angle = 22.5
    uncertaity_cancel = 3
    absolute_position = np.arange(0,360,wanted_angle)

    start_position = getPosition(file_path)*Deg
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
    powerOn(voltagelim, operation_current, operation_time, position=start_position, notmakesure=notmakesure)
    time.sleep(0.4)
    for l in range(feedback_loop):
        mid_position = getPosition(file_path)*Deg
        if goal_position + wanted_angle < mid_position:
            operation_time = howlong(goal_position - (mid_position - 360))
            pass
        else:
            operation_time = howlong(goal_position - mid_position)
            pass
        powerOn(voltagelim, operation_current, operation_time, position=mid_position, notmakesure=notmakesure)
        time.sleep(0.4)
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
        operation_time = 0.04
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
