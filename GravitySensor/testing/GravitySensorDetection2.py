import sys;
import serial;
from time import sleep;
import struct;
BAUDRATE = 115200; #for DWL5000XY
SIZE = 12;
MAXLOOP = 10000000;
devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AB0L75U1-if00-port0'; # DTECH USB 2.0 TO RS422/RS485 USB
stime = 0.1;
print('Initializaition1 happened')

class GravitySensor:
    def __init__(self): #, devlocation, stime/ these are the candidate of other parameters
        print('Initializaition2 happened')
        #self.devlocation = declocation
        #self.stime = stime
        if len(sys.argv)>1 :
            isSingle = (int)(sys.argv[1]);
            print(isSingle);
            pass;
        try:
            ser = serial.Serial(devlocation, 
                   baudrate =BAUDRATE, 
                   timeout  =0, 
                   #rtscts   =False,
                   #dsrdtr   =False,
                   bytesize =serial.EIGHTBITS, 
                   parity   =serial.PARITY_NONE, 
                   stopbits =serial.STOPBITS_ONE, 
                   #xonxoff  =False
                   );
            print('the trial successed')
        except serial.serialutil.SerialException:
            print('exception');
            sys.exit();
        ser.reset_input_buffer();
        ser.reset_output_buffer();

    def oneax(self):
        command=b"\x06\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        ser.write(command);
        sleep(stime);
        while True:
            if ser.inWaiting() > 0 :break;
            pass;

        command=b"\x06\x01\x01\xAA\x00\x00\x00\x00\x00\x00\x00\x00";
        ser.write(command);
        sleep(stime);

        while True:
            if ser.inWaiting() > 0: break;
            pass;
        read = [];
        for i in range(MAXLOOP):
            sleep(stime);
            read0 = ser.readline();
            size0 = len(read0);
            if size0>0:
                read0hex = ['{}'.format(hex(c)) for c in read0];
                add = read0hex ;
                read += add;
                pass;
            while len(read) > 0:
                if read[0:2] == ['0x61','0x11'] : break;
                else                            : read = read[1:];
                break;
                pass;
            if len(read) >= SIZE : break;
            pass;
        size = len(read);
        if  size>0 :
            readInt = [];
            for c in read : readInt.append((Int)(c,16));
            pass;

        nums = [readInt[5], readInt[4], readInt[3], readInt[2]];
        angleX = (nums[0]<<24)+(nums[1]<<16)+(nums[2]<<8)+(nums[3]);
        angleX = (angleX - 1800000)/10000;
        ser.close();
        return angleX

    def twoax(self):
        command=b"\x06\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        ser.write(command);
        sleep(stime);
        while True:
            if ser.inWaiting() > 0 :break;
            pass;

        command=b"\x06\x01\x02\xAA\x00\x00\x00\x00\x00\x00\x00\x00";
        ser.write(command);
        sleep(stime);

        while True:
            if ser.inWaiting() > 0: break;
            pass;
        read = [];
        for i in range(MAXLOOP):
            sleep(stime);
            read0 = ser.readline();
            size0 = len(read0);
            if size0>0:
                read0hex = ['{}'.format(hex(c)) for c in read0];
                add = read0hex ;
                read += add;
                pass;
            while len(read) > 0:
                if read[0:2] == ['0x61','0x22'] : break;
                else                            : read = read[1:];
                break;
                pass;
            if len(read) >= SIZE : break;
            pass;
        size = len(read);
        if  size>0 :
            readInt = [];
            for c in read : readInt.append((Int)(c,16));
            pass;

        readInt1 = readInt[5:8];
        readInt2 = readInt[2:5];
        #readInt11 = readInt1 if readInt1[-1]==10 else readInt2 ; 
        #readInt12 = readInt1 if readInt1[-1]==11 else readInt2 ; 
        readInt11 = readInt1;
        readInt12 = readInt2;
        numsX = [ readInt11[2], readInt11[1], readInt11[0] ];
        numsY = [ readInt12[2], readInt12[1], readInt12[0] ];
        #print(readInt);
        #print('numsX', numsX );
        #print((numsX[0]<<16)/1e+4 ,(numsX[1]<<8)/1e+4 , (numsX[2])/1e+4 );
        #print('numsY', numsY );
        #print((numsY[0]<<16)/1e+4 ,(numsY[1]<<8)/1e+4 , (numsY[2])/1e+4 );
        angleX = (numsX[0]<<16) + (numsX[1]<<8) + (numsX[2]);
        angleX = (angleX - 300000) / 10000.;
        angleY = (numsY[0]<<16) + (numsY[1]<<8) + (numsY[2]);
        angleY = (angleY - 300000) / 10000.;
        #print( 'angle X = {}'.format(angleX) );
        #print( 'angle Y = {}'.format(angleY) );
        pass;
        ser.close();
        return angleX, angleY














