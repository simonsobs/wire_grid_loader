import os
import datetime
from pytz import timezone

### Log class ###
class Log :

    def __init__(self, logdir='./log'):
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
        now = datetime.datetime.now();
        self.opendatetime = now;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        dateStr = now.strftime('%Y-%m-%d');
        logfilename = '{}/actuator_{}.log'.format(self.logdir, dateStr);
        if not os.path.isdir(self.logdir) : os.mkdir(self.logdir);
        print('Open log file: {}.'.format(logfilename));
        if os.path.exists(logfilename) :
            self.logfile = open(logfilename, 'a+');
        else :
            self.logfile = open(logfilename, 'w' );
            log = '# Date Time-Timezone\n';
            self.logfile.write(log);
            pass
        return 0;
    
    def writelog(self,msg) :
        now = datetime.datetime.now(timezone('UTC'));
        now = datetime.datetime.now();
        if self.opendatetime.day != now.day : 
            self.openlog();
            pass;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        log = ('{:25s} {:s}\n'.format(nowStr, msg));
        self.logfile.write(log);
        self.logfile.flush();
        return 0;
    
    

