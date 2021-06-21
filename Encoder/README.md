This encoder scripts are originated from CHWP encoder scripts.

In the nominal usage, beaglebone gets data from encoder and sends it to a PC with a specific IP address & port via UDP ethernet connection.
So, you need to run a script in the beaglebone and also run a script by a PC to receive and record the data from Encoder.

## Scripts for Beaglebone
- Beaglebone : Main scripts used in Beaglebone

## Scripts for the PC
- DataCollector (old name:src) : to receive encoder data at PC via ethernet from beaglebone
- testing : scripts for CHWP (copied from old CHWP scripts)

## Analysis
- SignalAnalysisScript : encoder signal analysis codes by jupyter
