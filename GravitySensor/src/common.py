import os
import datetime
from pytz import timezone

### Log format ###
def writelog(logfile, onoff, voltagelim, currentlim, vol, cur, timeperiod=0.) :
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    if timeperiod>0. :
      log = ('{:25s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(nowStr, onoff, voltagelim, currentlim, vol, cur, timeperiod))
    else :
      log = ('{:25s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8s}\n'.format(nowStr, onoff, voltagelim, currentlim, vol, cur, '--------'))
      pass;
    logfile.write(log)
    return log


def openlog(log_dir) :
    # Open log file
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    dateStr = now.strftime('%Y-%m-%d')
    logfilename = '{}/PMX_{}.dat'.format(log_dir, dateStr);
    if not os.path.isdir(log_dir) : os.mkdir(log_dir);
    if os.path.exists(logfilename) :
      logfile = open(logfilename, 'a+')
    else :
      logfile = open(logfilename, 'w' )
      log = '# Date Time-Timezone ON/OFF VoltageLimit[V] CurrentLimit[A] Voltage[V] Current[A] powerOn-timeperiod[sec]\n'
      logfile.write(log)
      pass
    return logfile;

