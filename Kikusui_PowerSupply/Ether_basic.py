# Built-in python functions
import sys
import time
from socket import socket, SOCK_STREAM, AF_INET

# Check the python version
if sys.version_info.major == 2:
    print("\nKikusui PMX control only works with Python 3\n"
          "Usage: sudo python3 command_supply.py")
    sys.exit()
    pass

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('169.254.35.156', 5025))
#sock.connect(('192.168.0.10',5025))

wait_time = 0.05
buffer_size = 128

def check_output():
    sock.sendall(b'output?\n')
    val = int(sock.recv(buffer_size).decode('utf-8'))
    if val == 0:
        msg = "Measured output state = OFF"
    elif val == 1:
        msg = "Measured output state = ON"
    else:
        msg = "Failed to measure output..."
    return msg, val
    pass

def check_current():
    sock.sendall(b'curr?\n')
    val = float(sock.recv(buffer_size).decode('utf-8'))
    msg = "Measured current = %.3f A" % (val)
    return msg, val
    pass

def check_voltage():
    sock.sendall(b'volt?\n')
    val = float(sock.recv(buffer_size).decode('utf-8'))
    msg = "Measured voltafe = %.3f V" % (val)
    return msg, val
    pass

def set_current(curr_lim):
    sock.sendall(b'curr %a\n' % curr_lim)
    wait()
    sock.sendall(b'curr?\n')
    wait()
    val = float(sock.recv(buffer_size).decode('utf-8'))
    msg = "Current set = {}".format(val)
    return msg, val
    pass

def set_voltage(vol_lim):
    sock.sendall(b'volt %a\n' % vol_lim)
    wait()
    sock.sendall(b'volt?\n')
    wait()
    val = float(sock.recv(buffer_size).decode('utf-8'))
    msg = "Voltage set = {}".format(val)
    return msg, val
    pass

def turn_on(notmakesure=False):
    """ Turn the PMX on """
    if notmakesure == True:
        sock.sendall(b'output 1\n')
        msg = "PMX turned ON perhaps\n"
        return msg
        pass
    else:
        sock.sendall(b'output 1\n')
        wait()
        sock.sendall(b'output?\n')
        wait()
        val = int(sock.recv(buffer_size).decode('utf-8'))
        msg = "Output state = {}".format(val)
        return msg
        pass
    pass

def turn_off(notmakesure=False):
    """ Turn the PMX on """
    if notmakesure == True:
        sock.sendall(b'output 0\n')
        msg = "PMX turned OFF perhaps\n"
        return msg
        pass
    else:
        sock.sendall(b'output 0\n')
        wait()
        sock.sendall(b'output?\n')
        wait()
        val = int(sock.recv(buffer_size).decode('utf-8'))
        msg = "Output state = {}".format(val)
        return msg
        pass
    pass

def wait():
    time.sleep(wait_time)
    return 0
    pass

if __name__ == '__main__':
    print('this is basic functions for ethernet control')
