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


def powerOn(np05b=None,ports=None) :
    if np05b is None :
        if config.use_tcp:
            np05b = NP05B.NP05B(tcp_ip=config.tcp_ip, user=config.user, password=config.password, log_dir=config.log_dir, port_info=config.port_info)
        else:
            np05b = NP05B.NP05B(rtu_port=config.ttyUSBPort, log_dir=config.log_dir, port_info=config.port_info)
        pass;
 
    if ports is None :
        np05b.all_on();
    else :
        for p in ports :
            np05b.on(p);
            pass;
        pass;

    return np05b;

### parseCmdLine() ###
def parseCmdLine(args):
    from optparse import OptionParser;
    parser = OptionParser();
    parser.add_option('-p', '--ports', dest='ports', help='port list to be powered on (1-5). It can be specify multiple ports by combinding ports with "," (ex. "1,2").', type = str, default=None);
    (config, args) = parser.parse_args(args);
    if len(args)!=1 :
        print('ERROR! Wrong number of arguments ({}). Shold be 1.'.format(len(args)));
        print('       You should only use options specified by - or --.');
        print('       Please see `python powerOn.py --help`.');
        return 0;
    return config;


### main command when this script is directly run ###
if __name__ == '__main__':

    parseconfig = parseCmdLine(sys.argv);
    if parseconfig :
        ports = parseconfig.ports;
        if not ports is None : 
            ports = [int(p) for p in ports.split(',') ];
            pass;
 
        np05b = powerOn(ports=ports);
        del np05b;
        pass;

    pass;
