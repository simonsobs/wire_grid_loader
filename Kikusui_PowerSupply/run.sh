#!/bin/sh

echo "Alarm START!"
echo $(date)

/home/daq01/Downloads/iwt120ctl/iwt120ctl set ANY 33
sleep 180

/home/daq01/Downloads/iwt120ctl/iwt120ctl set ANY 0

echo "Alarm STOP"
echo "Measurement START"
echo $(date)

(
    #python3 TimeControl.py -v 12 -c 2.0 -t 0.5 -n
    #python3 powerOn.py -v 12 -c 2.1 -t 3600
    echo "Hello"
) &

wait $!

echo "Measurement STOP!"
echo $(date)
