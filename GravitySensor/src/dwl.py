# Built-in python modules
import time as tm
import serial as sr
import sys as sy
import os

import binascii;
import struct;

# Control modules
this_dir = os.path.dirname(__file__)
sy.path.append(os.path.join(
    this_dir, "..", "..", "MOXA"))
import moxaSerial as mx  # noqa: E402

class DWL:
    """
    The DWL object is for communicating with the DWL-5000XY gravity sensor

    Args:
    rtu_port (str): Serial RTU port
    tcp_ip (str): TCP IP address
    tcp_port (int): TCP port
    """
    waittime = 0.05; # sec

    def __init__(self, rtu_port=None, tcp_ip=None, tcp_port=None, timeout=None):
        # Connect to device
        msg = self.__conn(rtu_port, tcp_ip, tcp_port, timeout)
        print(msg)
        self._remote_Mode()

    def __del__(self):
        if not self.using_tcp:
            print(
                "Disconnecting from RTU port %s"
                % (self._rtu_port))
            self.ser.close()
        else:
            print(
                "Disconnecting from TCP IP %s at port %d"
                % (self._tcp_ip, self._tcp_port))
            pass
        return

    def get_single_angle(self):
        """ Measure the single-axis angle """
        self.clean_serial()
        #command=b"\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        command=b"\x06\x05\x01\x00\x00\x00\x00\x00";
        print(command);
        bts = self.ser.write(command)
        self.wait()

        read = [];
        isSingle = True
        SIZE = 16;
        while True :
            print('aho');
            read0 = self.ser.readline(decopt='ignore');
            size0 = len(read0);
            print(read0);
            if size0>0 : 
              print( 'read0   ({}) = {}'.format(size0 , struct.unpack('{}c'.format(size0), read0) ) );
              add = struct.unpack('{}s'.format(size0), read0)[0] ;
              read += add if len(read)>0 else add.lstrip('\x00') ;
              print(read);
              pass;

            if len(read) > 0 :
              if isSingle :
                print(read);
                if read[0:3] != ['\x01','\x06','\x01'] : read = read[8:];
              else :
                if read[0:3] != ['\x01','\x06','\x02'] : read = read[8:];
                pass;
              pass;
            if len(read) >= SIZE : break;
        pass;
        size = len(read);

        msg = "Measured angle = {}".format(read)
        print(msg)
        return msg, val


    # ***** Helper Methods *****
    def __conn(self, rtu_port=None, tcp_ip=None, tcp_port=None, timeout=None):
        """
        Connect to the PMX module

        Args:
        rtu_port (str): Serial RTU port
        tcp_ip (str): TCP IP address
        tcp_port (int): TCP port
        """
        if rtu_port is None and (tcp_ip is None or tcp_port is None):
            raise Exception(
                "Aborted PMX._conn() due to no RTU or "
                "TCP port specified")
        elif (rtu_port is not None and
              (tcp_ip is not None or tcp_port is not None)):
            raise Exception(
                "Aborted PMX._conn() due to RTU and TCP port both being "
                "specified. Can only have one or the other.")
        elif rtu_port is not None:
            self.ser = sr.Serial(
                port=rtu_port, baudrate=19200, bytesize=8,
                parity='N', stopbits=1, timeout=timeout)
            self._rtu_port = rtu_port
            self.using_tcp = False
            msg = "Connected to RTU port %s" % (rtu_port)
        elif tcp_ip is not None and tcp_port is not None:
            self.ser = mx.Serial_TCPServer((tcp_ip, tcp_port), timeout)
            self._tcp_ip = tcp_ip
            self._tcp_port = int(tcp_port)
            self.using_tcp = True
            msg = "Connected to TCP IP %s at port %d" % (tcp_ip, tcp_port)
        else:
            raise Exception(
                "Aborted PMX._conn() due to unknown error")
        return msg

    def wait(self):
        """ Sleep """
        tm.sleep(self.waittime)
        return True

    def clean_serial(self):
        """ Flush the serial buffer """
        #if not False:
        #    self.ser.reset_input_buffer()
        #    self.ser.reset_output_buffer()
        #    self.ser.flush()
        #else:
            #self.ser.flushInput()
        self.ser.flushInput()
        return True

    def _remote_Mode(self):
        """ Enable remote control """
        self.clean_serial()
        self.ser.write(str.encode('SYST:REM\n\r'))
        self.wait()
        return True
