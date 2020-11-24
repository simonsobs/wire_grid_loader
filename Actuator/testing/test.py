import signal
import serial
import socket
import sys
import time

#devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AL01WX4M-if00-port0'
devlocation = '/dev/ttyUSB4'

# This should be used in each step of sending command & geting response
def mysleep(sleeptime=0.1):
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
def sendCommand(serial, command) :
  serial.write((command+'\n').encode());
  mysleep();
  return 0;

# Send command & get response
def getresponse(serial,command,verbose=1) :
  if verbose > 0 :
    print();
    print('## getresponse[ command = {} ]'.format(command));
    pass;
  res = '';
  sendCommand(serial, command);
  res = readAll(serial);
  if verbose > 0 :
    print(res);
    print();
    pass;
  return res;

'''
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
'''


# Wait for end of moving (Idle status)
def waitIdle(serial, max_loop = 100000) :
  i = 0;
  mysleep();
  while True :
    i++1;
    res = getresponse(serial,'?',False).replace('\r','').replace('\n','/').strip();
    print('\"{}\"'.format(res));
    status = (res[1:]).split('|')[0];
    print('\"{}\"'.format(status));
    if status == 'Idle' : 
      print('waitIdle() ends correctly.');
      break;
    if len(status)==0 :
      print('Error! Could not get status!');
      return -1;
    if i>=max_loop : 
      print('Error! Exceed max number of loop = {}'.format(i));
      return -1;
    mysleep();
    pass;
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

#sendCommand(ser,'G91 G0 F100000 X300Y-300') # forward
sendCommand(ser,'G91 G0 F100000 X-300Y300') # backward
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
'''

# Close the serial communication
ser.close()
