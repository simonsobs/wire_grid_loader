import os
import datetime
from pytz import timezone

### parseCmdLine() ###
def parseCmdLine(args):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-v', '--voltage', dest='voltagelim', help='Voltage limit [V]', type = float, default=12.)
    parser.add_option('-c', '--current', dest='currentlim', help='Current limit [A]', type = float, default=3.)
    parser.add_option('-t', '--time'   , dest='timeperiod', help='Powering-on time [sec]: If the period=<0, KIKUSUI power supply continues to power on until you run the powerOff script.', type = float, default=0.)
    parser.add_option('-l', '--laps', dest='num_laps', help='the number of laps for discrete angle measurement. default is 10', type=int, default=10)
    parser.add_option('-f', '--feedback', dest='num_feedback', help='the number of feedbacks for one action. default is 5', type=int, default=5)
    parser.add_option('-s', '--stopped', dest='stopped_time', help='stopped time between the actions. defalut 30 sec', type=float, default=30.)
    parser.add_option('-d', '--discrete', action="store_true", dest='control_type', help='False:continuous rotation, True:discrete rotation, default is False', default=False)
    parser.add_option('-n', '--notmakesure', action="store_true", dest='notmakesure', help='Whether to check Voltage and Current. default is False', default=False)
    parser.add_option('-i', '--initialize', dest='initializing_option', help='to initialize the calibrator. 0:check minimal control-angle(default), 1:matrix 1.5/1.8/2.1/2.4/2.7/3.0 A and 0.4/0.8/1.2/1.6/2.0/2.4 sec', type=int, default=0)
    #parser.add_option('-v', '--verbose', dest='verbose', help='verbosity (0:Normal, -1:output all)', type = int, default=0)
    (config, args) = parser.parse_args(args)
    return config

### Log format ###
def writelog(logfile, onoff, voltagelim, currentlim, vol=0., cur=0., timeperiod=0., position=0., notmakesure=False) :
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    if notmakesure==False:
      if timeperiod > 0. :
        log = ('{:25s} {:3s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8s}\n'.format(nowStr, onoff, 'YES', voltagelim, currentlim, vol, cur, timeperiod, '--------'))
      else :
        log = ('{:25s} {:3s} {:3s} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8s} {:8s}\n'.format(nowStr, onoff, 'YES', voltagelim, currentlim, vol, cur, '--------', '--------'))
        pass;
    else:
      if timeperiod > 0. :
        log = ('{:25s} {:3s} {:3s} {:8.3f} {:8.3f} {:8s} {:8s} {:8.3f} {:8.3f}\n'.format(nowStr, onoff, 'NO', voltagelim, currentlim, '--------', '--------', timeperiod, position))
      else :
        log = ('{:25s} {:3s} {:3s} {:8.3f} {:8.3f} {:8s} {:8s} {:8s} {:8s}\n'.format(nowStr, onoff, 'NO', voltagelim, currentlim, '--------', '--------', '--------', '--------'))
        pass;
    logfile.write(log)
    return nowStr

def writeitem(logfile, date_str, item, state):
    log = ('{:25s} {:12s} {:5s}'.format(date_str, item, state))
    logfile.write(log)
    pass

def openlog(log_dir, verbose=0) :
    # Open log file
    now = datetime.datetime.now(timezone('UTC'))
    nowStr  = now.strftime('%Y-%m-%d %H:%M:%S-%Z')
    dateStr = now.strftime('%Y-%m-%d')
    if verbose == 0:
      logfilename = '{}/PMX_{}.dat'.format(log_dir, dateStr)
      if not os.path.isdir(log_dir) : os.mkdir(log_dir)
      if os.path.exists(logfilename) :
        logfile = open(logfilename, 'a+')
      else :
        logfile = open(logfilename, 'w' )
        log = '# Date Time-Timezone ON/OFF CheckValues[Y/N] VoltageLimit[V] CurrentLimit[A] Voltage[V] Current[A] powerOn-timeperiod[sec]\n'
        logfile.write(log)
        pass
      pass
    else:
      logfilename = '{}/items_{}.dat'.format(log_dir, dateStr)
      if not os.path.isdir(log_dir) : os.mkdir(log_dir)
      if os.path.exists(logfilename) :
        logfile = open(logfilename, 'a+')
      else :
        logfile = open(logfilename, 'w' )
        log = '# Date Time-Timezone Item Start/Stop\n'
        logfile.write(log)
        pass
      pass
    return logfile;

