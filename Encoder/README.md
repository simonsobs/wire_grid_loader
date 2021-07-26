This encoder scripts are originated from CHWP encoder scripts.

In the nominal usage, beaglebone gets data from encoder and sends it to a PC with a specific IP address & port via UDP ethernet connection.
So, you need to run a script in the beaglebone and also run a script by a PC to receive and record the data from Encoder.

## Scripts for Beaglebone
- Beaglebone : Main scripts used in Beaglebone
    - Beaglebone_Encoder_DAQ.c : Main Code to store/send data from PRU
        - To switch the data output method, change the value of SAVETOBB
    - Encoder_Detection.c : Code to catch signals of Encoder w/ PRU
    - IRIG_Detection.c : Code to catch signals of IRIG w/ PRU
- if you do not need to store the data into BB, you execute only one command ``./run.sh``

## Scripts for the PC
- DataCollector (old name:src) : to receive encoder data at PC via ethernet from beaglebone
- testing : scripts for CHWP (copied from old CHWP scripts)
- CheckByADALM2000 : to send pulses that imitates the Encoder signal w/ ADALM2000

## Analysis
- SignalAnalysisScript : encoder signal analysis codes by jupyter
