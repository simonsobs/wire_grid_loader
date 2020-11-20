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

## Actuator (Blackbox)
Scripts to control a linear actuator

Requirements: No (need pyserial library in python)
Communication: USB (Blackbox has a RS232 serial converter inside itself.)

- testing : This directory is for test.


# Tags
### v1.0

