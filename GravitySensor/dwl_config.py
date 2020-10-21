# Boolean flag for Ethernet to IP
use_moxa = True

# MOXA IP address
tcp_ip = '192.168.1.7' # USC540 serial converter
#tcp_ip = '192.168.0.7' # USC540 serial converter
tcp_port =  26 # CH2

# ttyUSB port
if not use_moxa:
    rtu_port = '/dev/ttyUSB2'
    pass

# Logger directory
log_dir = 'log';
