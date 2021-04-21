#!/usr/bin/python3

# Built-in python functions
import sys

# Check the python version
if sys.version_info.major == 2:
    print(
        "\nstart_logging.py only works with Python 3\n"
        "Usage: python3 start_logging.py")
    sys.exit()

# Import control modules
from src import LimitSwitch;
import limitswitch_config as config;


def getStatus(LS=None, pin=None) :
    if LS is None :
        LS = LimitSwitch.LimitSwitch(config.GPIOpinInfo, logdir=config.logdir);
        pass;
 
    
    msg = "Limit switch status:";
    print(msg);
    outputs = LS.get_onoff(pinname=pin);
    if pin is None:
        if len(outputs) == len(config.GPIOpinInfo):
            for i in range(len(outputs)):
                msg = "%s = %3s (%s)" % (config.GPIOpinInfo[i]['name'], 'ON' if (int(outputs[i])) else 'OFF', config.GPIOpinInfo[i]['label']);
                print(msg);
                pass;
        else:
            print('WARNING! Extra output, try again. Output = {}'.format(outputs))
            pass;
    else :
        msg = "%s = %d" % (pin, outputs);
        print(msg);
        pass;

    return LS;

### parseCmdLine() ###
def parseCmdLine(args):
    from optparse import OptionParser;
    parser = OptionParser();
    parser.add_option('-p', '--pin', dest='pin', help='Specify pin name to get status (ex. "L1R1"). Please check limitswitch_config.py. If pin is not specified, all of the pins are shown.', type = str, default=None);
    (config, args) = parser.parse_args(args);
    if len(args)!=1 :
        print('ERROR! Wrong number of arguments ({}). Shold be 1.'.format(len(args)));
        print('       You should only use options specified by - or --.');
        print('       Please see `python get_status.py --help`.');
        return 0;
    return config;


### main command when this script is directly run ###
if __name__ == '__main__':

    parseconfig = parseCmdLine(sys.argv);
    if parseconfig :
        LS = getStatus(pin=parseconfig.pin);
        del LS;
        pass;
    pass;
