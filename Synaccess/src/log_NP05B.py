import os
import datetime
from pytz import timezone

### Log class ###
class Log :

    def __init__(self, labels, logdir='./log'):
        self.labels = labels;
        self.logdir = logdir;

        self.opendatetime = None;
        self.logfile      = None;
        self.openlog();
        pass;
    
    def __del__(self):
        if not self.logfile is None :
            self.logfile.close();
            del self.logfile;
            pass;
        return


    def openlog(self) :
        if not self.logfile is None :
            self.logfile.close();
            pass;
        # Open log file
        now = datetime.datetime.now(timezone('UTC'))
        self.opendatetime = now;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        dateStr = now.strftime('%Y-%m-%d');
        logfilename = '{}/synaccess_{}.log'.format(self.logdir, dateStr);
        if not os.path.isdir(self.logdir) : os.mkdir(self.logdir);
        print('Open log file: {}.'.format(logfilename));
        if os.path.exists(logfilename) :
            self.logfile = open(logfilename, 'a+');
        else :
            self.logfile = open(logfilename, 'w' );
            log = '# Date Time-Timezone {}\n'.format(' '.join(self.labels));
            self.logfile.write(log);
            pass
        return True;
    
    def writestatus(self,onoffs) :
        # ON/OFF csv-like data
        if isinstance(onoffs, list) : onoffStr = ' '.join(['{:3s}'.format('1' if onoff==1 else '0') for onoff in onoffs]);
        else                        : onoffStr = '{:3s}'.format('1' if onoffs==1 else '0');
        self.write(onoffStr);
        return True;
    
    def writelog(self, msg) :
        self.write(msg, header='# ');
        return True;
 
    def write(self,msg,header='') :
        now = datetime.datetime.now(timezone('UTC'));
        if self.opendatetime.day != now.day : 
            self.openlog();
            pass;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        log = ('{}{:25s} {:s}\n'.format(header, nowStr, msg));
        self.logfile.write(log);
        self.logfile.flush();
        return True;
 
    pass;
    


