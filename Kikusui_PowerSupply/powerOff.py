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
def powerOff(PMX=None) :

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
    
    # Turn OFF
    PMX.turn_off()
    vol   , cur    = PMX.check_voltage_current()
    vollim, curlim = PMX.check_voltage_current_limit()
    writelog(logfile, 'OFF', notmakesure=False, vollim, curlim, vol, cur)

    return PMX




### parseCmdLine() ###
def parseCmdLine(args):
  from optparse import OptionParser;
  parser = OptionParser();
  #parser.add_option('-v', '--verbose', dest='verbose', help='verbosity (0:Normal, -1:output all)', type = int, default=0);
  (config, args) = parser.parse_args(args);
  return config;




### main command when this script is directly run ###
if __name__ == '__main__':

  config = parseCmdLine(sys.argv)

  powerOff()
  pass
  
 
