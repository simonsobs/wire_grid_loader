Stopper
=======

**Current scripts for python2 temporarily. Please change it.**
- src/common.py
- command\_supply.py
- on.py
- off.py

## Scripts to read limit switch
- `command\_supply.py` : To set ON/OFF for all of the stoppers interactively. 
- `on.py`  : Turn ON all of the stoppers.
- `off.py` : Turn OFF all of the stoppers.

## Configuration
- `stopper\_config.py` : Here, `GPIOpinInfo` is defined, that determins which pins of the beaglebone are used to set stoppers.

## Main class
- `src/Stopper.py` : Main class to control the stoppers is Stopper.
