# wire\_grid\_loader
This scripts are for controlling the wire grid loader.
** Please don't push output datafiles to the git repositry!! **

## Encoder
Scripts to read the encoder data (position of the wire)

Communication: Ethernet

## MOXA
Library for serial communication

This library is used to send command and receive data 
from devices via USC540 serial converter.

## Kikusui\_PowerSupply (rotation motor)
Scripts to control KIKUSUI power supply (PMX)

Requirements: MOXA 
Communication: RS232 serial communication via the serial converter

## GravitySensor
Scripts to control KIKUSUI power supply (PMX)

Requirements: MOXA 
Communication: RS422 serial communication via the serial converter

- testing : This directory is for test.

## Actuator (Blackbox)
Scripts to control a linear actuator including stopper and limit switch

Requirements: "pyserial", "pytz", "Adafruid\_BBIO" library in python

Communication: USB (Blackbox has a RS232 serial converter inside itself.)

- Stopper : Scripts to control stopper
- LimitSwitch : Scripts to read limit switches
- testing : This directory is for test.

## Synaccess (Power Strip)
Scripts to control a power strip (Synaccess NP05B)

Requirements: "requests", "pytz" library in python

Communication: LAN (Synacess NP05B should be directly connected to PC via LAN.)


## misc

For setup @ Kusaka Lab.
- start\_webcamvideo.sh : To start web camera @ Kusaka Lab.
- iwt120ctl : Controller of the alarm for remote control
    - If you want rotate the wire grid, please run alarm.sh: `./alarm.sh`, which makes 3 second alarm.




# Tags
### v1.0

