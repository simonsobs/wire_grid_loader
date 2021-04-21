#!/usr/bin/python3

# Built-in python functions
import sys
# To kill this script by Ctrl+C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Check the python version
if sys.version_info.major == 2:
    print(
        "\nstart_logging.py only works with Python 3\n"
        "Usage: python3 start_logging.py")
    sys.exit()

# Import control modules
from src import NP05B;
import NP05B_config as config;


if config.use_tcp:
    np05b = NP05B.NP05B(tcp_ip=config.tcp_ip, user=config.user, password=config.password, log_dir=config.log_dir, port_info=config.port_info)
else:
    np05b = NP05B.NP05B(rtu_port=config.ttyUSBPort, log_dir=config.log_dir, port_info=config.port_info)
    pass;
 
np05b.start_logging(interval=1.);
