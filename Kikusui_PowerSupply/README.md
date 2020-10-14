 Kikusui\_PowerSupply
 ====================

## Main scripts
- ``command\_supply.py`` 
  - To control KIKUSUI by typing commands interactively
- ``powerOff.py``
  - To power off KIKUSUI
  - ex) ``python3 powerOff.py``
- ``powerOn.py``
  - To power on KIKUSUI
  - command options:
    - -v <voltage [V]> : to set voltage
    - -c <current [A]> : to set current
    - -t <time [sec]>  : time to keep powering on
  - Please see help by ``python3 powerOn.py -h``
  - ex) ``python3 powerOn.py -v 12 -c 3 -t 10``
    - set voltage=12V & current=3A and keep on for 10 seconds.

## Configuration
- ``pmx\_config.py``
  - configuration of the USC540 serial converter (This transfers the commands from PC to KIKUSUI via RS-232.)
  - important items:
    - tcp\_ip   : IP address of the USC540 serial converter
    - tcp\_port : Port to specify the channel of the serial converter (CH1 = port 23)

## Library
This scripts uses the scripts in ``src/``.
The main control script for KIKUSUI is ``src/pmx.py``.

## Log
``log`` directory will have powering on/off log files for each day. (One day = 1 file)


## Other scripts to control KIKUSUI
``utils`` should have macros to control KIKUSUI. (ex. scheduling powering on/off, repeating powering on/off, analizing log file..)
