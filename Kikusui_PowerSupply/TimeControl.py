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

from src.common import * # writelog(), openlog()

### main function ###
def TimeControl(voltagelim=0., currentlim=0., timeperiod=0., PMX=None) :

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

    wait_turn_on = PMX.waittime * 4.

    if timeperiod > wait_turn_on:
        # Run and Sleep for the specified time period
        print(time.time())
        for i in range(5):
            for j in range(2):
                PMX.turn_on() # include wait() x 4 (200 msec)
                time1 = time.time()
                msg, vol = PMX.check_voltage()
                msg, cur = PMX.check_current()
                writelog(logfile, 'ON', voltagelim, currentlim, vol, cur, timeperiod)

                time.sleep(timeperiod*(i+1))

                PMX.turn_off()
                time2 = time.time()
                vol   , cur    = PMX.check_voltage_current()
                vollim, curlim = PMX.check_voltage_current_limit()
                writelog(logfile, 'OFF', vollim, curlim, vol, cur)

                with open('interval_temp.dat','a+') as itemp:
                    print(time2-time1,file=itemp)
                    pass

                time.sleep(0.5)
                pass
            print(time.time())
            time.sleep(2)
            pass
        print(time.time())
        pass
    else :
        msg = ("WARNING! The wait-time period is too short.\n\
                The period should be larger than wait-time for turning on({:.3f} sec)."
                .format(wait_turn_on))
        print(msg)
        pass

    return PMX


### parseCmdLine() ###
def parseCmdLine(args):
  from optparse import OptionParser;
  parser = OptionParser();
  parser.add_option('-v', '--voltage', dest='voltagelim', help='Voltage limit [V]', type = float, default=0.);
  parser.add_option('-c', '--current', dest='currentlim', help='Current limit [A]', type = float, default=0.);
  parser.add_option('-t', '--time'   , dest='timeperiod', help='Powering-on time [sec]: If the time=<0, KIKUSUI power supply continues to power on until you run the powerOff script.', type = float, default=0.);
  #parser.add_option('-v', '--verbose', dest='verbose', help='verbosity (0:Normal, -1:output all)', type = int, default=0);
  (config, args) = parser.parse_args(args);
  return config;

### main command when this script is directly run ###
if __name__ == '__main__':

  config = parseCmdLine(sys.argv)
  voltagelim = config.voltagelim
  currentlim = config.currentlim
  timeperiod = config.timeperiod

  TimeControl(voltagelim, currentlim, timeperiod)
  pass
