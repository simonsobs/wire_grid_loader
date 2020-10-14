#!/usr/bin/python3

# Built-in python functions
import os
import sys as sy
import readline
import time

# Check the python version
if sy.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sy.exit()
    pass

# Import control modules
import pmx_config as cg  # noqa: E402
import src.pmx as pm  # noqa: E402

from src.common import * # writelog(), openlog()

### main function ###
def powerOff(PMX=None) :

    # Connect to PMX power supply
    if PMX==None :
        if cg.use_moxa:
            PMX = pm.PMX(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5)
        else:
            PMX = pm.PMX(rtu_port=cg.rtu_port)
            pass
        pass

    # Open log file
    logfile = openlogfile(cg.log_dir)
    
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
        msg, vol = PMX.check_voltage()
        msg, cur = PMX.check_current()
        writelog(logfile, 'OFF', 0., 0., vol, cur)
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
  Out("",True,config);
  return config;




### main command when this script is directly run ###
if __name__ == '__main__':

  config = parseCmdLine(sys.argv)
  voltagelim = config.voltagelim
  currentlim = config.currentlim
  timeperiod = config.timeperiod

  powerOn(voltagelim, currentlim, timeperiod)
  pass
  
 
