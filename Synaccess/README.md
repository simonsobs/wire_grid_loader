Synaccess NP05B (Power Strip)
=============================

## Scripts to read Synaccess NP05B
- `command\_supply.py` : To control or read the status of the power strip Synaccess NP05B interactively. It will print 0(=OFF) or 1(=ON).
- `start\_logging.py` : Start to write log in `./log` with a time interval (default:1sec).

## Configuration
- `NP05B\_config.py` : Here, IP or port of the NP05B is defined.

## Main class
- `src/NP05B.py` : Main class to control the Synaccess NP05B 


## Requirements
- pip install pytz
- pip install requests
