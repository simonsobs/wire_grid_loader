#!/usr/bin/python3

# Built-in python functions
import sys as sy
import readline
import time
import datetime

# Check the python version
if sy.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sy.exit()
    pass

# Import control modules
import pmx_config as cg  # noqa: E402
import src.pmx as pm  # noqa: E402

def writelog(logfile, onoff, voltagelim, currentlim, vol, cur) :
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    log = ('{:25s} {:3s} {:10.3f} {:10.3f} {:10.3f} {:10.3f}\n'.format(nowStr, onoff, voltagelim, currentlim, vol, cur))
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
    logfilename = '{}/PMX_{}.dat'.format(log_dir, dateStr);
    if os.path.exists(logfilename) :
      logfile = open(outfile, 'a+')
    else :
      logfile = open(outfile, 'w' )
      log = '# Date Time-Timezone ON/OFF VoltageLimit[V] CurrentLimit[A] Voltage[V] Current[A]\n'
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
    writelog(logfile, nowStr, 'ON', voltagelim, currentlim, vol, cur))

    # Turn OFF after timeperiod
    # If timeperiod <= 0., the power is ON permanently.
    if timeperiod > 0. :
        # Sleep for the specified time period
        if timeperiod > wait_turn_on :
            time.sleep(timeperiod-wait_turn_on)
        else :
            msg = ("WARNING! The wait-time period is too short.\n
            The period should be larger than wait-time for turning on({:.3f} sec)."
            .format(wait_turn_on))
            print(msg)
            pass
       
        PMX.turn_off()
        now = datetime.datetime.now(timezone('UTC'))
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
        msg, vol = PMX.check_voltage()
        msg, cur = PMX.check_current()
        writelog(logfile, nowStr, 'OFF', voltagelim, currentlim, vol, cur))
        pass

    return PMX

