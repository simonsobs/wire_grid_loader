# Built-in python modules
import time
import sys
import os
import requests # need for ethernet connection

import log_NP05B as log


class NP05B:
    """
    The NP05B object for communicating with the Synaccess power strip

    Args:
    rtu_port (int): Modbus serial port for USB connection (defualt None).
    tcp_ip (str): IP address for ethernet connection (default None)
    user : user name to connect via ethernet
    password : password to connect via ethernet

    Only either rtu_port or tcp_ip can be defined.
    """
    def __init__(self, rtu_port=None, tcp_ip=None, user='', password='', log_dir='./log', port_info=None):
        # Synaccess info
        self.port_info = port_info;
        self.user      = user;
        self.password  = password;

        # Logging object
        self.log = log.Log([p['labels'] for p in self.port_info],logdir)

        # Connect to device
        if rtu_port is None:
            self._use_tcp = False;
            self._request_header = '';
            self.__conn(tcp_ip=config.tcp_ip)
        else:
            self._use_tcp = True;
            self.__conn(rtu_port=rtu_port)
            pass;

        # Read parameters
        self._num_tries = 1
        self._bytes_to_read = 20
        self._tstep = 0.2
        pass;

    def __del__(self):
        if not self._use_tcp:
            self.log.writelog(
                "Closing RTU serial connection at port %s"
                % (config.rtu_port))
            self._clean_serial()
            self._ser.close()
        else:
            self.log.writelog(
                "End of TCP connection to IP %s"
                % (self._tcp_ip));
            pass;
        return

    def on(self, port):
        """ Power on a specific port """
        cmd = b'$A3 {} 1'.format(port);
        self._command(cmd)
        self._wait();
        self._writestatus();
        return True

    def off(self, port):
        """ Power off a specific port """
        cmd = b'$A3 %d 0' % (port)
        self._command(cmd)
        self._wait();
        self._writestatus();
        return True

    def all_on(self):
        """ Power on all ports """
        cmd = b'$A7 1'
        self._command(cmd)
        self._wait();
        self._writestatus();
        return True

    def all_off(self):
        """ Power off all ports """
        cmd = b'$A7 0'
        self._command(cmd)
        self._wait();
        self._writestatus();
        return True

    def reboot(self, port):
        """ Reboot a specific port """
        cmd = b'$A4 %d' % (port)
        self._command(cmd)
        self._wait();
        self._writestatus();
        return True

    def getstatus(self):
        """ Print the power status for all ports """
        cmd = b'$A5'
        for n in range(self._num_tries):
            out = self._write(cmd);
            if not self._use_tcp : out = self._read();
            if len(out) == 0:
                continue
            elif len(out) != 0:
                if not self._use_tcp :
                    stat = out[1].decode().replace("\x00", '').replace(",", '').replace("$A0", '').replace("\n", '').replace("\r", '').replace("$A5", '')
                    return list(stat)[::-1]
                else :
                    out = out.content;
                    if len(out)!=9 or out[:3]=='$A0' :
                        self.writelog('WARNING! Could not read a correct status from NP05B. output = {}'.format(out));
                        self.writelog('         Expected output = $A0,?????');
                        continue;
                    stat = [(int)onoff for onoff in out[4:10]];
                    return stat;
            else:
                self.writelog(
                    "ERROR! Did not understand NP05B output %s" % (out))
                continue
            pass;
        return True

    # Keep logging until stop=True
    # interval : time interval to write log [sec]
    # The defaut interval is 1sec
    def start_logging(self, stop=False, interval=1.):
        print('Start logging about synaccess NP05B status. (interval={} sec)'.format(interval));
        while stop is False :
            self._writestatus();
            time.sleep(interval);
            pass;
        return 0;


    # ***** Helper methods *****
    def __conn(self, rtu_port=None, tcp_ip=None):
        """ Connect to device either via TCP or RTU """
        if rtu_port is None and tcp_ip is None:
            raise Exception('NP05B Exception: no RTU port or TCP IP specified')
        elif (rtu_port is not None and tcp_ip is not None):
            raise Exception(
                "NP05B Exception: RTU port and TCP IP specified. "
                "Can only have one or the other.")
        elif rtu_port is not None:
            self._ser = sr.Serial(
                port=rtu_port, baudrate=9600, bytesize=8,
                parity='N', stopbits=1, timeout=1)
            self.witelog(
                "Connecting to RTU serial port %s" % (rtu_port))
            config.use_tcp = False
            config.rtu_port = rtu_port
        elif tcp_ip is not None:
            self._request_header = "http://{}:{}@{}/cmd.cgi?".format(self.user,self.password,tcp_ip);
            self.writelog(
                "Connecting to IP %s via HTTP requests"
                % (tcp_ip))
            self._tcp_ip = tcp_ip
            pass;
        return 0;

    def _wait(self):
        """ Wait a specific timestep """
        time.sleep(self._tstep)
        return True

    def _clean_serial(self):
        """ Flush the serial buffer """
        if not self._use_tcp:
            self._ser.reset_input_buffer();
            self._ser.reset_output_buffer();
            self._ser.flush();
            pass;
        return True

    def _write(self, cmd):
        """ Write to the serial port """
        ret = None;
        if not self._use_tcp : 
            self._clean_serial()
            self._ser.write((cmd+b'\r'))
            ret = 0;
        else :
            request = self._request_header + cmd ;
            ret = requests.get(request);
            pass;
        self._wait()
        return ret;

    def _read(self):
        """ Read from the serial port """
        if not config.use_tcp:
            return self._ser.readlines()
        return True;

    def _command(self, cmd):
        """ Send a command to the device """
        for n in range(self._num_tries):
            self._write(cmd)
            pass;
        return True

    def _writestatus(self):
        stat = getstatus();
        self.writestatus(stat);
        return True;


