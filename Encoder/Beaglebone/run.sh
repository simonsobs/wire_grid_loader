#!/bin/bash
# Automatically start in /etc/systemd/system/wiregrid-encoder-pru.service

make clean && make

./Beaglebone_Encoder_DAQ
#./Beaglebone_Encoder_DAQ test.txt 600
#./Beaglebone_Encoder_DAQ test20230816.txt

#./Beaglebone_Encoder_DAQ Encoder1.bin Encoder2.bin IRIG1.bin IRIG2.bin
