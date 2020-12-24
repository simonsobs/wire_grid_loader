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

file_path = '/home/kyoto/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt'

feedback_time = [0.18, 0.22, 0.25, 0.28, 0.30]
wanted_angle = 22.5
feedback_loop = 3
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
            for i in range(1):
                for j in range(2):
                    operation_current = currentlim
                    num_execution = 20
                    time.sleep(2)
                    if operation_current > 3.0:
                        print("operation current is over a range from 0. to 3.0")
                        sys.exit(1)
                    for k in range(num_execution):
                        start_position = getPosition(file_path)*Deg
                        if start_position + wanted_angle > 360:
                            goal_position = start_position + wanted_angle - 360
                            pass
                        else:
                            goal_position = start_position + wanted_angle
                            pass
                        operation_time = timeperiod
                        powerOn(voltagelim, operation_current, operation_time, notmakesure=True)
                        time.sleep(2)
                        for l in range(feedback_loop):
                            mid_position = getPosition(file_path)*Deg
                            if goal_position < mid_position:
                                operation_time = feedbackfunction(goal_position - (mid_position - 360))
                                pass
                            else:
                                operation_time = feedbackfunction(goal_position - mid_position)
                            time.sleep(2)
                            pass
                        time.sleep(3)
                        pass
                    powerOn(12, 3.0, 1, notmakesure=True)
                    time.sleep(3)
                    pass
                pass
            stop_time = time.time()
            print(stop_time - start_time)
            pass
        else:
            print("This is a script to measure the relation between operation time of power supply and proceeded angle.")

def getPosition(filepath):
    f = open(filepath, 'r')
    data = f.readlines()
    f.close()
    return float(data[0])

def feedbackfunction(position_difference):
    if position_difference >= 4.5:
        return feedback_time[4]
        pass
    if 4.5 > position_difference & position_difference >= 3.5:
        return feedback_time[3]
        pass
    if 3.5 > position_difference & position_difference >= 2.5:
        return feedback_time[2]
        pass
    if 2.5 > position_difference & position_difference >= 1.5:
        return feedback_time[1]
        pass
    if 1.5 > position_difference & position_difference >= 0.5:
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
