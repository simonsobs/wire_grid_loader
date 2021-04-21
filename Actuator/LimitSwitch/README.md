Limit Switch
============

## Scripts to read limit switch
- `command\_supply.py` : To read the limit switch ON/OFF interactively. It will print 0(=OFF) or 0(=ON). You can also use the arguments of this script to read specific pinname (See limitswitch\_config.py).
- `start\_logging.py` : Start to write log in `./log` with a time interval (default:1sec).
- `get\_status.py` : Print ON/OFF of the limit switches. You can specify pin by python get\_status.py -p \<pin name\>.

# Configuration
- `limitswitch\_config.py` : Here, `GPIOpinInfo` is defined, which determined which pin in the beaglebone reads which limit switch.

## Main class
- `src/LimitSwitch.py` : Main class to read limit switches is LimitSwitch.

## Requirements
- pip install pytz
- pip install Adafruit\_BBIO
