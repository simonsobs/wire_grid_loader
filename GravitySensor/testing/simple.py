#!/usr/bin/python3

# Built-in python functions
import os
import sys
from time import sleep
import struct
import binascii

# Kill by Ctrl+C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Check the python version
if sys.version_info.major == 2:
    print("\nGravity-sensor control only works with Python 3\n"
          "Usage: python3 test.py")
    sys.exit()
    pass

# Import control modules
pre_dir=os.path.join(os.path.dirname(__file__), '..');
print(pre_dir);
sys.path.append(pre_dir);

import dwl_config as cg  # noqa: E402

from src.common import * # writelog(), openlog()

this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(
    this_dir, "..", "..", "MOXA"))
import moxaSerial as mx  # noqa: E402

### main function ###
def test(DWL=None, isSingle=True) :

    ser = mx.Serial_TCPServer((cg.tcp_ip, cg.tcp_port), 10)
    msg = "Connected to TCP IP %s at port %d" % (cg.tcp_ip, cg.tcp_port)
    ser.flushInput()
    print(msg);

    for i in range(100) :
        command=b"\x06\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        ser.write(command);
        pass;
    sleep(1)


    if isSingle :
      command=b"\x06\x01\x01\xAA\x00\x00\x00\x00\x00\x00\x00\x00"; # for single axis
      #print('set ',command);
    else :
      command=b"\x06\x01\x02\xAA\x00\x00\x00\x00\x00\x00\x00\x00"; # for dual axis
      #command=b"\x06\x01\x02\x00\x00\x00\x00\x00"; # for dual axis
      pass;
    print(command);

    WRITELOOP    = 100 ; # loop of writing command
    MAXLOOP      = 10 ; # max. loop of series of write(read command) -> read()
    MAXREADLOOP  =  1 ; # max. loop of read()
    minsize = 12;

    read = [];
    for n in range(MAXLOOP) :
        for k in range(WRITELOOP) :
            ser.write(command);
            pass;
      
        print('Waiting to read');
        sleep(0.1);
      
        print('Read');
        for m in range(MAXREADLOOP) :
            print('read');
            read0 = ser.readexactly(12);
            #read0 = ser.readline();
            size0 = len(read0);
            #print( 'read ({}) = {}...'.format(len(read0) , struct.unpack('{}c'.format(len(read0)), read0) ) );
            print( 'read ({}) = "{}"'.format(len(read0) , read0 ) );
            if size0>0 : 
                #add = struct.unpack('{}s'.format(size0), read0)[0] ;
                #add = ['0x{}'.format(binascii.hexlify(c)) for c in read0];
                #add = [hex(c) for c in read0];
                add = read0;
                #read += add if len(read)>0 else add.lstrip('\x00') ;
                print('add = {}'.format(add));
                read += add;
                #print(read);
                pass;
            print('{}'.format([ '0x{:x}'.format(c) for c in read ]));
            while len(read) > 0 :
                if isSingle :
                    #print('{}'.format([ '0x{:x}'.format(c) for c in read ]));
                    if read[0:2] == [int(0x61),int(0x11)] : break;
                    else                                  : read = read[1:];
                else :
                    #print('{}'.format([ '0x{:x}'.format(c) for c in read ]));
                    if read[0:2] == [int(0x61),int(0x22)] : break;
                    else                                  : read = read[1:];
                    pass;
                pass;

            # Exit inner loop and proceed
            if len(read) >= minsize : break;
            pass;
     
        # Exit outer loop and proceed
        if len(read) >= minsize : break;
        pass;
    
    size = len(read);
    print(read);
    readHex = [ '0x{:x}'.format(c) for c in read ];
    print(readHex);
    if size < minsize :
      print('Error!! Could not read correctly!');
      return(-1);
      pass;

    if isSingle :
        # ((((Byte [5]<< 24) + (Byte [4] << 16) + (Byte [3]<< 8) + Byte [2]) -1800000) / 10000
        nums = [ read[5], read[4], read[3], read[2] ];
        angleX = (nums[0]<<24) + (nums[1]<<16) + (nums[2]<<8) + (nums[3]) ;
        angleX = (angleX - 1800000) / 10000.;
        #Angle value = (((Byte 6 << 16) + (Byte 5 << 8) + Byte 4) - 180000) / 1000
        #nums = [ read[5], read[4], read[3] ];
        #angleX = (nums[0]<<16) + (nums[1]<<8) + (nums[2]) ;
        #angleX = (angleX - 180000) / 1000.;
        print( 'angle X = {}'.format(angleX) );
    else :
        read1 = read[2:5];
        read2 = read[5:8];
        read11 = read1;
        read12 = read2;
        numsX = [ read11[2], read11[1], read11[0] ];
        numsY = [ read12[2], read12[1], read12[0] ];
        print('numsX', numsX );
        print((numsX[0]<<16)/1e+4 ,(numsX[1]<<8)/1e+4 , (numsX[2])/1e+4 );
        print('numsY', numsY );
        print((numsY[0]<<16)/1e+4 ,(numsY[1]<<8)/1e+4 , (numsY[2])/1e+4 );
        angleX = (numsX[0]<<16) + (numsX[1]<<8) + (numsX[2]);
        angleX = (angleX - 300000) / 10000.;
        angleY = (numsY[0]<<16) + (numsY[1]<<8) + (numsY[2]);
        angleY = (angleY - 300000) / 10000.;
        print( 'angle X = {}'.format(angleX) );
        print( 'angle Y = {}'.format(angleY) );
        pass;



    return DWL




### parseCmdLine() ###
def parseCmdLine(args):
  from optparse import OptionParser;
  parser = OptionParser();
  #parser.add_option('-v', '--verbose', dest='verbose', help='verbosity (0:Normal, -1:output all)', type = int, default=0);
  (config, args) = parser.parse_args(args);
  return config;




### main command when this script is directly run ###
if __name__ == '__main__':

  config = parseCmdLine(sys.argv)

  for  i in range(1000 ) :
      #test(isSingle=True)
      #test(isSingle=True)
      #test(isSingle=True)
      test(isSingle=False)
      #test(isSingle=False)
      #test(isSingle=False)
      pass;

  pass
  
 
