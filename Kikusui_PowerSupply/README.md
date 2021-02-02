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
- ``AutoControl.py``
  - To rotate wire grid ring discretely or continuously(default: continuous)
  - command options(continuous rotation):
    - -t <time [sec]>         :time to keep powering on
    - -n <notmakesure>        :not to check the actually current and voltage, for correct time operation
  - command options(discrete rotation, with -d option):
    - -l <laps>               :number of laps in one measurement
    - -f <feedback>           :number of feedback cycles for one action
    - -s <stopped time [sec]> :time holding or staying after one action
  - eg) ``python3 AutoControl.py -d -l 10 -f 8 -s 10``
    - 10 laps discrete rotaion with 8 feedbacks and holding 10 sec

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
