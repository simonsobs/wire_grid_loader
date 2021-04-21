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
from src import NP05B;
import NP05B_config as config;


def getStatus(np05b=None) :
    if np05b is None :
        if config.use_tcp:
            np05b = NP05B.NP05B(tcp_ip=config.tcp_ip, user=config.user, password=config.password, log_dir=config.log_dir, port_info=config.port_info)
        else:
            np05b = NP05B.NP05B(rtu_port=config.ttyUSBPort, log_dir=config.log_dir, port_info=config.port_info)
        pass;
 
    
    outputs = np05b.getstatus();
    msg = "Port power status:";
    print(msg);
    if outputs == True:
        print('WARNING! Jumbled...try again')
    elif len(outputs) == 5:
        for i in range(len(outputs)):
            msg = "Port %d = %3s (%s)" % (i + 1, 'ON' if (int(outputs[i])) else 'OFF', config.port_info[i]['label']);
            print(msg)
            pass
    else:
        print('WARNING! Extra bytes, try again')
        pass;

    return np05b;

### parseCmdLine() ###
def parseCmdLine(args):
    from optparse import OptionParser;
    parser = OptionParser();
    #parser.add_option('-p', '--ports', dest='ports', help='port list to be powered on (1-5). It can be specify multiple ports by combinding ports with "," (ex. "1,2").', type = str, default=None);
    (config, args) = parser.parse_args(args);
    return config;


### main command when this script is directly run ###
if __name__ == '__main__':

    parseconfig = parseCmdLine(sys.argv);

    np05b = getStatus();
    del np05b;

    pass
