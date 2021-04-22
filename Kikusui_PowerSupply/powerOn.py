#!/usr/bin/python3

# Built-in python functions
import os
import sys
import readline
import time

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

### main function ###
def powerOn(voltagelim=0., currentlim=0., timeperiod=0., position=0., notmakesure=False, PMX=None) :

    # Connect to PMX power supply
    if PMX==None :
        if cg.use_moxa:
            PMX = pm.PMX(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5)
        else:
            PMX = pm.PMX(rtu_port=cg.rtu_port)
            pass
        pass
    PMX.clean_serial()

    # Open log file
    logfile = openlog(cg.log_dir)

    # Set voltage & current
    msg = PMX.set_voltage(voltagelim)
    msg = PMX.set_current(currentlim)

    if notmakesure==False:
        # Turn On
        PMX.turn_on() # include wait() x 4 (200 msec)
        msg, vol = PMX.check_voltage()
        msg, cur = PMX.check_current()
        wait_turn_on = PMX.waittime * 4.
        writelog(logfile, 'ON', voltagelim, currentlim, vol, cur, timeperiod)

        # Turn OFF after timeperiod
        # If timeperiod <= 0., the power is ON permanently.
        if timeperiod > 0. :
            # Sleep for the specified time period
            if timeperiod > wait_turn_on :
                time.sleep(timeperiod-wait_turn_on)
            else :
                msg = ("WARNING! The wait-time period is too short.\n\
                The period should be larger than wait-time for turning on({:.3f} sec)."
                .format(wait_turn_on))
                print(msg)
                pass

            PMX.turn_off()
            vol   , cur    = PMX.check_voltage_current()
            vollim, curlim = PMX.check_voltage_current_limit()
            writelog(logfile, 'OFF', vollim, curlim, vol, cur)
            pass
        pass
    else:
        # Turn On
        PMX.turn_on(notmakesure)
        writelog(logfile, 'ON', voltagelim, currentlim, timeperiod=timeperiod, position=position, notmakesure=notmakesure)

        if timeperiod > 0. :
            # Sleep for the specified time period
            time.sleep(timeperiod)

            PMX.turn_off(notmakesure)
            writelog(logfile, 'OFF', voltagelim, currentlim, notmakesure=notmakesure)
            pass
        pass
    return PMX


### main command when this script is directly run ###
if __name__ == '__main__':

    config = parseCmdLine(sys.argv)
    voltagelim = config.voltagelim
    currentlim = config.currentlim
    timeperiod = config.timeperiod
    notmakesure = config.notmakesure

    powerOn(voltagelim, currentlim, timeperiod, notmakesure)
    pass
