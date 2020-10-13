#!/usr/bin/python3

# Built-in python functions
import os
import sys as sy
import readline
import time
import datetime
from pytz import timezone

# Check the python version
if sy.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sy.exit()
    pass

# Import control modules
import pmx_config as cg  # noqa: E402
import src.pmx as pm  # noqa: E402

def writelog(logfile, onoff, voltagelim, currentlim, vol, cur, timeperiod=0.) :
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    if timeperiod>0. :
      log = ('{:25s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(nowStr, onoff, voltagelim, currentlim, vol, cur, timeperiod))
    else :
      log = ('{:25s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8s}\n'.format(nowStr, onoff, voltagelim, currentlim, vol, cur, '-----'))
      pass;
    logfile.write(log)
    return log

def powerOn(voltagelim=0., currentlim=0., timeperiod=0., PMX=None) :
    if PMX==None :
        # Connect to PMX power supply
        if cg.use_moxa:
            PMX = pm.PMX(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5)
        else:
            PMX = pm.PMX(rtu_port=cg.rtu_port)
            pass
        pass

    # Open log file
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    dateStr = now.strftime('%Y-%m-%d')
    logfilename = '{}/PMX_{}.dat'.format(cg.log_dir, dateStr);
    if not os.path.isdir(cg.log_dir) : os.mkdir(cg.log_dir);
    if os.path.exists(logfilename) :
      logfile = open(logfilename, 'a+')
    else :
      logfile = open(logfilename, 'w' )
      log = '# Date Time-Timezone ON/OFF VoltageLimit[V] CurrentLimit[A] Voltage[V] Current[A] powerOn-timeperiod[sec]\n'
      logfile.write(log)
      pass
    
    # Set voltage & current 
    msg = PMX.set_voltage(voltagelim)
    msg = PMX.set_current(currentlim)

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
        now = datetime.datetime.now(timezone('UTC'))
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
        msg, vol = PMX.check_voltage()
        msg, cur = PMX.check_current()
        writelog(logfile, 'OFF', 0., 0., vol, cur)
        pass

    return PMX




if __name__ == '__main__':

  voltagelim = 0.
  currentlim = 0.
  timeperiod = 0.
  if len(sys.argv) > 1 :
    voltagelim = (float)(sys.argv[1])
    pass
  if len(sys.argv) > 2 :
    currentlim = (float)(sys.argv[2])
    pass
  if len(sys.argv) > 3 :
    timeperiod = (float)(sys.argv[3])
    pass

  powerOn(voltagelim, currentlim, timeperiod)
  
 
