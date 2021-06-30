def oneaxdtc():

    import sys;
    import serial;
    from time import sleep;
    import struct;
       
    #devlocation = '/dev/tty.usbserial-AC01O8QI'; # mac
    #devlocation = '/dev/ttyUSB0'; # mylinux
    #devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AC01O8QI-if00-port0'; # tandem
    #devlocation = '/dev/serial/by-id/usb-FTDI_USB_to_RS-232_422_485_Adapter_DM2CHF1B-if00- port0'; # EasySync ES-U-3001-M at tandem
    #devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AG0JLDID-if00-port0'; # DTECH USB 2.0 TO RS422/RS485 USB converter for DWL-5000XY S/N 13B50141
    devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AB0L75U1-if00-port0'; # DTECH USB 2.0 TO RS422/RS485 USB converter @ Hongo
    stime = 0.1;
    #stime = 1;

    BAUDRATE = 115200; # for DWL5000XY
    SIZE = 12;
    #SIZE = 1600000;

    MAXLOOP = 10000000;



    if len(sys.argv)>1 :
     isSingle = (int)(sys.argv[1]);
     print(isSingle);
     pass;

    try :
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

        #print('serial closed');
        #ser.close();
    except serial.serialutil.SerialException:
        print('exception');
        sys.exit();
    #ser.rs485_mode = True;


    ser.reset_input_buffer();
    ser.reset_output_buffer();

    # read input device information (for LakeShore Model 218 temperature monitor)

    command=b"\x06\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x24\x00\x00\x00\x00\x00\x00";


    ser.write(command);
    sleep(stime);
    while True :
        if ser.inWaiting() > 0 : break;
        pass;



    
    #print('Single Axis Mode');
    #command=b"\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x01\x01\x00\x00\x00\x00\x00";
    command=b"\x06\x01\x01\xAA\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x01\x01\xAA\x00\x00\x00\x00";
    

    ser.write(command);
    sleep(stime);


    while True :
        if ser.inWaiting() > 0 : break;
        pass;
    read = [];
    #while True :
    for i in range(MAXLOOP) :
        sleep(stime);
        read0 = ser.readline();
        size0 = len(read0);
        #print('read0 = {}'.format(read0));
        if size0>0 : 
            read0hex = ['{}'.format(hex(c)) for c in read0];
            #print( 'read0   ({}) = (unpack) {} / (hex) {} / (raw) {}'.format(size0, struct.unpack('{}c'.format(size0), read0), read0hex, read0 ) );
            add = read0hex ;
            read += add;
            #print('read = {}'.format(read));
            pass;
         #"""
        while len(read) > 0 :
            #print('read = {}'.format(read));
            if read[0:2] == ['0x61','0x11'] :
                #print('read = {}'.format(read));
                break;
            else:
                read = read[1:];
            break;
            pass;
            #"""
        if len(read) >= SIZE : break;
        pass;
    size = len(read);
    if size>0 : 
        readInt = [];
        for c in read : readInt.append( (int)(c,16) );
        #print( 'read (hex)  ({}) = {}'.format(size, read) );
        #print( 'read (int)  ({}) = {}'.format(size, readInt) );
        pass;

    
    nums = [ readInt[5], readInt[4], readInt[3], readInt[2] ];
    #print(readInt);
    #print(nums);
    #print( (nums[1]<<16)/1e+4 , (nums[2]<<8)/1e+4 , (nums[3])/1e+4 );
    #angleX = (nums[0]<<16) + (nums[1]<<8) + (nums[2]) ;
    angleX = (nums[0]<<24) + (nums[1]<<16) + (nums[2]<<8) + (nums[3]) ;
    angleX = (angleX - 1800000) / 10000.;
    #print( 'angle X = {}'.format(angleX) );
    #temp = (nums[3]<<8) + (nums[4]) ;
    #temp = (temp - 3000.) / 100.;
    #print( 'temperature = {}'.format(temp) );
    #print( 'single axis position = {}'.format(nums[4]) );
    ser.close();
    return angleX
    

def twoaxdtc():
    #!/bin/env python3
    import sys;
    import serial;
    from time import sleep;
    import struct;
       
    #devlocation = '/dev/tty.usbserial-AC01O8QI'; # mac
    #devlocation = '/dev/ttyUSB0'; # mylinux
    #devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AC01O8QI-if00-port0'; # tandem
    #devlocation = '/dev/serial/by-id/usb-FTDI_USB_to_RS-232_422_485_Adapter_DM2CHF1B-if00- port0'; # EasySync ES-U-3001-M at tandem
    #devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AG0JLDID-if00-port0'; # DTECH USB 2.0 TO RS422/RS485 USB converter for DWL-5000XY S/N 13B50141
    devlocation = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AB0L75U1-if00-port0'; # DTECH USB 2.0 TO RS422/RS485 USB converter @ Hongo
    #isSingle = True;
    #isSingle = False;

    stime = 0.01;
    #stime = 1;

    BAUDRATE = 115200; # for DWL5000XY
    SIZE = 12;
    #SIZE = 1600000;

    MAXLOOP = 10000000;



    if len(sys.argv)>1 :
     isSingle = (int)(sys.argv[1]);
     print(isSingle);
     pass;

    try :
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

        #print('serial closed');
        #ser.close();
    except serial.serialutil.SerialException:
        print('exception');
        sys.exit();
    #ser.rs485_mode = True;

    ser.reset_input_buffer();
    ser.reset_output_buffer();

    # read input device information (for LakeShore Model 218 temperature monitor)

    command=b"\x06\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x24\x00\x00\x00\x00\x00\x00";


    ser.write(command);
    sleep(stime);
    while True :
        if ser.inWaiting() > 0 : break;
        pass;
    #print('Dual Axis Mode');
    #command=b"\x06\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x01\x02\x00\x00\x00\x00\x00";
    command=b"\x06\x01\x02\xAA\x00\x00\x00\x00\x00\x00\x00\x00";
    #command=b"\x06\x01\x02\xAA\x00\x00\x00\x00";

    ser.write(command);
    sleep(stime);


    while True :
        if ser.inWaiting() > 0 : break;
        pass;
    read = [];
    #while True :
    for i in range(MAXLOOP) :
        sleep(stime);
        read0 = ser.readline();
        size0 = len(read0);
        #print('read0 = {}'.format(read0));
        if size0>0 : 
            read0hex = ['{}'.format(hex(c)) for c in read0];
            #print( 'read0   ({}) = (unpack) {} / (hex) {} / (raw) {}'.format(size0, struct.unpack('{}c'.format(size0), read0), read0hex, read0 ) );
            add = read0hex ;
            read += add;
            #print('read = {}'.format(read));
            pass;
         #"""
        while len(read) > 0 :
            #print('read = {}'.format(read));
            if read[0:2] == ['0x61','0x22'] : break;
            else                            : read = read[1:];
            pass;
        pass

        if len(read) >= SIZE : break;
        pass;
    size = len(read);
    if size>0 : 
        readInt = [];
        for c in read : readInt.append( (int)(c,16) );
        #print( 'read (hex)  ({}) = {}'.format(size, read) );
        #print( 'read (int)  ({}) = {}'.format(size, readInt) );
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

 

    



if __name__ == "__main__":
    
    [a, b] = twoaxdtc()
    c = oneaxdtc()
    print("angle X =",a)
    print("angle Y =",b)
    print("1ax mode angle=", c)
