#!/bin/sh

echo "Alarm START!"
echo $(date)

/home/daq01/Downloads/iwt120ctl/iwt120ctl set ANY 33
sleep 120

/home/daq01/Downloads/iwt120ctl/iwt120ctl set ANY 0

echo "Alarm STOP"
echo "Measurement START"
echo $(date)

(
    python3 powerOn.py -v 12 -c 3.0 -t 3
    sleep 120
    python3 powerOn.py -v 12 -c 1.5 -t 600 -n
    sleep 60
    python3 powerOn.py -v 12 -c 2.0 -t 600 -n
    sleep 60
    python3 powerOn.py -v 12 -c 2.5 -t 600 -n
    sleep 60
    python3 powerOn.py -v 12 -c 3.0 -t 600 -n
    sleep 60
) &

wait $!

echo "Measurement STOP!"
echo $(date)
