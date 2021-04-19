import os
import datetime
from pytz import timezone

### Log format ###
def openlog(log_dir, labels) :
    # Open log file
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    dateStr = now.strftime('%Y-%m-%d')
    logfilename = '{}/limitswitch_{}.log'.format(log_dir, dateStr);
    if not os.path.isdir(log_dir) : os.mkdir(log_dir);
    if os.path.exists(logfilename) :
      logfile = open(logfilename, 'a+')
    else :
      logfile = open(logfilename, 'w' )
      log = '# Date Time-Timezone {}\n'.format(' '.join(labels));
      logfile.write(log)
      pass
    return logfile;

def writelog(logfile, onoffs) :
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    onoffsStr = ' '.join(['{:3s}'.format('1' if onoff==1 else '0') for onoff in onoffs]);
    log = ('{:25s} {:s}\n'.format(nowStr, onoffsStr)
    logfile.write(log)
    return log;



