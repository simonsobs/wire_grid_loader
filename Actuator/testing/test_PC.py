import signal
import serial
import socket
import os, sys
import time

'''
# Limit switch/Stopper modules
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(
    this_dir, ".."))
from LimitSwitch.src import LimitSwitch
from LimitSwitch import limitswitch_config as ls_config
from Stopper.src import Stopper
from Stopper import stopper_config as st_config

limitswitch =  LimitSwitch.LimitSwitch(ls_config.GPIOpinInfo, logdir='./log');
stopper = Stopper.Stopper(st_config.GPIOpinInfo, logdir='./log');
'''

devlocation = '/dev/ttyUSB0'

hostname = socket.gethostname();
print('hostname : {}'.format(hostname));
if hostname.endswith('hepnet.scphys.kyoto-u.ac.jp'): # @ Kyoto
    devlocation = '/dev/ttyUSB4'
elif hostname == 'cmb-daq01' : # @ Tokyo
    devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AL01WX4M-if00-port0'
    #devlocation = '/dev/ttyUSB0'
else :
    print('WARNING!! There is no suitable hostname option in "testing.py" to switch device file for the Actuator.')
    print('--> Temporary set to /dev/ttyUSB0');
    pass
print('devlocation = {}'.format(devlocation));


# This should be used in each step of sending command & geting response
def mysleep(sleeptime=0.05):
    time.sleep(sleeptime); 
    return 0;

# Simple read function
def serial_read(serial) :
    read = serial.readline().decode();
    #print('read "{}"'.format(read));
    return read;

# Read all strings until the buffer is empty.
def readAll(serial) :
    lines = '';
    while True :
        #print('out_waiting = {}'.format(serial.out_waiting));
        #print('in_waiting  = {}'.format(serial.in_waiting ));
        if serial.in_waiting==0 : break ; # if buffer is empty, reading is finished.
        else :
            line = serial_read(serial);
            lines += line;
            pass;
        pass;
    return lines;

# Simple write function
def sendCommand(serial, command, verbose=1, doSleep=True) :
    if verbose>0 :
        print(command+'\n');
        print((command+'\n').encode());
        pass;
    serial.write((command+'\n').encode());
    if doSleep: mysleep();
    return 0;

# Send command & get response
def getresponse(serial,command,verbose=1, doSleep=True) :
    if verbose > 0 :
        print();
        print('## getresponse[ command = {} ]'.format(command));
        pass;
    res = '';
    sendCommand(serial, command, verbose=0, doSleep=doSleep);
    res = readAll(serial);
    if verbose > 0 :
        print(res);
        print();
        pass;
    return res;

"""
# Wait until receiving 'ok'
def waitOK(serial, max_loop = 100000) :
    i = 0;
    while True :
        i++1;
        read = serial_read(serial);
        read = read.strip();
        print('\"{}\"'.format(read));
        if read == 'ok' : 
            print('waitOK() ends correctly.');
            break;
        if read.startswith('error') :
            print('Error! message = {}'.format(read));
            return -1;
        if i>=max_loop : 
            print('Error! Exceed max number of loop = {}'.format(i));
            return -1;
        mysleep();
        pass;
    return 0;
"""


# get status
def getStatus(serial, verbose=1, doSleep=True) :
    res = getresponse(serial,'?',verbose=0,doSleep=doSleep).replace('\r','').replace('\n','/').strip();  # has mysleep()
    if verbose>0 : print('\"{}\"'.format(res));
    status = (res.split('<')[-1].split('>')[0]).split('|')[0];
    if verbose>0 : print('\"{}\"'.format(status));
    if len(status)==0 :
        print('Error! Could not get status!');
        return -1;
    return status;

# Wait for end of moving (Idle status)
def waitIdle(serial, max_loop = 100000, verbose=1) :
    for i in range(max_loop) :
        status = getStatus(serial, verbose);
        if status == 'Idle' : 
            if verbose>0 : print('waitIdle() ends correctly.');
            return 0;
        if len(status)==0 :
            print('Error! Could not get status!');
            return -1;
    print('Error! Exceed max number of loop = {}'.format(i));
    return -1;

def isIdle(serial, verbose=1, doSleep=True):
    if getStatus(serial, verbose, doSleep) == 'Idle' : return True;
    else                                    : return False;

def isRun(serial, verbose=1, doSleep=True):
    status = getStatus(serial, verbose, doSleep);
    if status in ['Jog', 'Run'] : return True;
    else                        : return False;

# print status
def printstatus(serial,verbose=1) :
        getresponse(serial, '?', verbose=verbose);
        return 0;

# General command to move
def move(serial, distance, speedrate=0.1) :
    if speedrate<0. or speedrate>1. :
        print("WARNING! Speedrate should be between 0 and 1.");
        print("WARNING! Speedrate is sed to 0.1.");
        speedrate = 0.1;
        pass;
    Fmax =1000;
    Fmin =   0;
    speed = int(speedrate * (Fmax-Fmin) + Fmin);
    serial.write(('$J=G91 F{:d} Y{:d}'.format(speed,distance)+'\n').encode());
    mysleep();
    return 0;
'''
# Simple forward moving (to opposite side of motor)
def forward(serial, distance, speedrate=0.1, verbose=1) :
    if distance < 0 : distance = abs(distance);
    LSL2 = 0; # left  actuator opposite limitswitch
    LSR2 = 0; # right actuator opposite limitswitch
    LSL2,LSR2 = limitswitch.get_onoff(pinname=['LSL2','LSR2']);
    if LSL2==0 and LSR2==0 : move(serial, distance, speedrate);
    isrun = True;
    while LSL2==0 and LSR2==0 and isrun :
        LSL2,LSR2 = limitswitch.get_onoff(pinname=['LSL2','LSR2']);
        isrun = isRun(serial,verbose=verbose, doSleep=True);
        if verbose>0 : print('LSL2={}, LSR2={}, run={}'.format(LSL2,LSR2,isrun));
        pass;
    hold(serial);
    release(serial);
    return 0;
# Simple backward moving (to motor)
def backward(serial, distance, speedrate=0.1, verbose=1) :
    if distance > 0 : distance = -1 * abs(distance);
    LSL1 = 0; # left  actuator opposite limitswitch
    LSR1 = 0; # right actuator opposite limitswitch
    LSL1,LSR1 = limitswitch.get_onoff(pinname=['LSL1','LSR1']);
    if LSL1==0 and LSR1==0 : move(serial, distance, speedrate);
    isrun = True;
    while LSL1==0 and LSR1==0 and isrun :
        LSL1,LSR1 = limitswitch.get_onoff(pinname=['LSL1','LSR1']);
        isrun = isRun(serial,verbose=verbose);
        if verbose>0 : print('LSL1={}, LSR1={}, run={}'.format(LSL1,LSR1,isrun));
        pass;
    hold(serial);
    release(serial);
    return 0;
'''


# Hold with decelerating
def hold(serial) :
    sendCommand(serial, '!');
    mysleep();
    return 0;
# Release(unhold) the hold state
def release(serial) :
    sendCommand(serial, '~');
    mysleep();
    return 0;

# Hold immediately
def rapidhold(serial) :
    sendCommand(serial, '\x85');
    mysleep();
    return 0;

### Main ###

# Open serial communication
ser = serial.Serial(
    devlocation,
    #port = '/dev/ttyUSB4',
    baudrate=115200,
)
if ser == None:
    print ("open error")
else:
    print ("connected")
    pass;
print(ser);

# Initialize blackbox
ser.write(b'\r\n\r\n');
ser.flushInput();
time.sleep(2);
res = readAll(ser); # this is necessary to work correctly.
print(res);


# Move commands
'''
ser.write(b'G91 G0 F100000 X-10 \r\n')
time.sleep(2);
ser.write(b'G91 G0 F100000 X10 \r\n')
time.sleep(2);
ser.write(b'G91 G0 F100000 X-10 \r\n')
time.sleep(2);
ser.write(b'G91 G0 F100000 X10 \r\n')
time.sleep(2);
ser.write(b'G91 G0 F100000 X-10 \r\n')
time.sleep(2);
ser.write(b'G91 G0 F100000 X10 \r\n')
time.sleep(2);
'''

getresponse(ser, '$21=0'); # hard limit switch
getresponse(ser, '$X');

print("sendCommand(ser,'G91 F10 Y100') # forward (motor->motor opposite) @ Hongo");
#sendCommand(ser,'G91 F10 Y-100') # forward
#sendCommand(ser,'G91 F10 Y1') # backward
waitIdle(ser);


# Status check commands
'''
getresponse(ser, '?');
getresponse(ser, '$$');
getresponse(ser, '$#');
getresponse(ser, '$G');
getresponse(ser, '$I');
getresponse(ser, '$N');
getresponse(ser, '$C');
#'''

# Close the serial communication
#ser.close()
