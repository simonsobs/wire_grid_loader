# Boolean flag for Ethernet to IP
use_moxa = True

# MOXA IP address
tcp_ip = '192.168.0.7' # USC540 serial converter
#tcp_ip = '192.168.1.70' # USC540 serial converter at Kyoto
tcp_port =  23 # CH1

# ttyUSB port
if not use_moxa:
    rtu_port = '/dev/ttyUSB2'
    pass

# Logger directory
log_dir = 'log';
