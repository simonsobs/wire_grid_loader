import socket

# Boolean flag for Ethernet to IP
use_moxa = True

# MOXA IP address
#tcp_port =  32 # CH1
#tcp_ip = '10.10.10.71' # USC540 serial converter at Kyoto
#tcp_port = 29
#tcp_ip = '192.168.0.7'
tcp_port =  32 # CH4 USC540 for Pton
#tcp_port =  26 # CH4 USC540 for Pton
tcp_ip = '192.168.0.130' # USC540 for Pton
print('tcp_ip = {}'.format(tcp_ip));

# ttyUSB port
if not use_moxa:
    rtu_port = '/dev/ttyUSB2'
    pass

# Logger directory
log_dir = 'log';
