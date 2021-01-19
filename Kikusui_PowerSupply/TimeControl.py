#!/usr/bin/python3

# Built-in python functions
import sys
import time
import numpy as np
from powerOn import powerOn, parseCmdLine

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

file_path = '/home/kyoto/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

feedback_time = [0.181, 0.221, 0.251, 0.281, 0.301]
wanted_angle = 22.5
uncertaity_cancel = 3
absolute_position = np.arange(0,360,wanted_angle)
feedback_loop = 8
Deg = 360/52000

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
            start_time = time.time()
            cycle = 0
            for j in range(1):
                operation_current = currentlim
                num_execution = 3
                time.sleep(1.5)
                if operation_current > 3.0:
                    print("operation current is over a range from 0. to 3.0")
                    sys.exit(1)
                for k in range(num_execution):
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
                    print(f'cycle num_{cycle} start_{round(start_position,2)} goal_{round(goal_position,2)}')
                    operation_time = timeperiod
                    powerOn(voltagelim, operation_current, operation_time, notmakesure=True, position=start_position)
                    time.sleep(0.6)
                    for l in range(feedback_loop):
                        mid_position = getPosition(file_path)*Deg
                        if goal_position + wanted_angle < mid_position:
                            operation_time = feedbackfunction(goal_position - (mid_position - 360))
                            pass
                        else:
                            operation_time = feedbackfunction(goal_position - mid_position)
                            pass
                        powerOn(voltagelim, operation_current, operation_time, notmakesure=True)
                        time.sleep(0.6)
                        pass
                    time.sleep(1.5)
                    cycle += 1
                    pass
                pass
            stop_time = time.time()
            print(stop_time - start_time)
            pass
        else:
            print("This is a script to measure the relation between operation time of power supply and proceeded angle.")

def getPosition(filepath):
    for i in range(10):
        try:
            f = open(filepath,'r')
            data = f.readlines()
            f.close()
            position = data[0]
        except IndexError:
            time.sleep(0.1)
            continue
        break
    return float(position)

def feedbackfunction(position_difference):
    if position_difference >= 6.0:
        return feedback_time[4]
        pass
    if (6.0 > position_difference) & (position_difference >= 4.5):
        return feedback_time[3]
        pass
    if (4.5 > position_difference) & (position_difference >= 3.5):
        return feedback_time[2]
        pass
    if (3.5 > position_difference) & (position_difference >= 2.5):
        return feedback_time[1]
        pass
    if (2.5 > position_difference) & (position_difference >= 0.5):
        return feedback_time[0]
        pass
    if 0.5 > position_difference:
        return 0.04
        pass

### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)
    voltagelim = config.voltagelim
    currentlim = config.currentlim
    timeperiod = config.timeperiod
    notmakesure = config.notmakesure

    TimeControl(voltagelim, currentlim, timeperiod, notmakesure)
    pass
