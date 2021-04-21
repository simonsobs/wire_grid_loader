Synaccess NP05B (Power Strip)
=============================

## Scripts to read Synaccess NP05B
- `command\_supply.py` : To control or read the status of the power strip Synaccess NP05B interactively. It will print 0(=OFF) or 1(=ON).
- `start\_logging.py` : Start to write log in `./log` with a time interval (default:1sec).
- `get\_status.py` : Print the current status of ON/OFF for each ports
- `powerOn.py` : To power on. Ports of Synaccess (1-5) can be specidied by -p option. Please see --help for the option details. If you do not specify port, all the ports are turned on.
- `powerOff.py` : To power off. Ports of Synaccess (1-5) can be specidied by -p option. Please see --help for the option details. If you do not specify port, all the ports are turned off.

## Configuration
- `NP05B\_config.py` : Here, IP or port of the NP05B is defined.

## Main class
- `src/NP05B.py` : Main class to control the Synaccess NP05B 


## Requirements
- pip install pytz
- pip install requests
