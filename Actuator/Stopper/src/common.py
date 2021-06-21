import os
import datetime
# NOTE: Please change if after python3 installation
#from pytz import timezone

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
        # NOTE: Please change if after python3 installation
        #now = datetime.datetime.now(timezone('UTC'))
        now = datetime.datetime.now();
        self.opendatetime = now;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        dateStr = now.strftime('%Y-%m-%d');
        logfilename = '{}/stopper_{}.log'.format(self.logdir, dateStr);
        if not os.path.isdir(self.logdir) : os.mkdir(self.logdir);
        print('Open log file: {}.'.format(logfilename));
        if os.path.exists(logfilename) :
            self.logfile = open(logfilename, 'a+');
        else :
            self.logfile = open(logfilename, 'w' );
            log = '# Date Time-Timezone {}\n'.format(' '.join(self.labels));
            self.logfile.write(log);
            pass
        return 0;
    
    def writelog(self,onoffs) :
        # NOTE: Please change if after python3 installation
        #now = datetime.datetime.now(timezone('UTC'));
        now = datetime.datetime.now();
        if self.opendatetime.day != now.day : 
            self.openlog();
            pass;
        nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z');
        if isinstance(onoffs, list) : onoffsStr = ' '.join(['{:3s}'.format('1' if onoff==1 else '0') for onoff in onoffs]);
        else                        : onoffsStr = '{:3s}'.format('1' if onoffs==1 else '0');
        log = ('{:25s} {:s}\n'.format(nowStr, onoffsStr));
        self.logfile.write(log);
        self.logfile.flush();
        return 0;
    
    

