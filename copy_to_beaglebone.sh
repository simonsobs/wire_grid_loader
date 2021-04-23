#!/bin/bash
rsync -ruvva --exclude=".*/" --exclude="*aho*" --exclude="*.out" --exclude="*.dat" --exclude="Kikusui_PowerSupply/log" --exclude="Encoder/src/rawdata" ./* beaglebone2:/home/debian/scripts/wire_grid_loader/
# Beaglebone1 is in adachi branch now. Please NOT copy to it.
#rsync -ruvva --exclude=".*/" --exclude="*aho*" --exclude="*.out" --exclude="*.dat" --exclude="Kikusui_PowerSupply/log" --exclude="Encoder/src/rawdata" ./* beaglebone1:/home/debian/scripts/wire_grid_loader/
