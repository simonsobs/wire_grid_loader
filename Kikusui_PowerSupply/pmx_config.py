import socket

# Boolean flag for Ethernet to IP
use_moxa = True

# MOXA IP address
tcp_port =  29 # CH1
hostname = socket.gethostname();
print('hostname : {}'.format(hostname));
if hostname.endswith('hepnet.scphys.kyoto-u.ac.jp'):
  tcp_ip = '192.168.1.70' # USC540 serial converter at Kyoto
elif hostname == 'cmb-daq01' :
  tcp_ip = '192.168.0.7' # USC540 serial converter at Tokyo
else :
  print('WARNING!! There is no suitable hostname option in "pmx_config.py" to switch IP address for the KIKUSUI power supply.')
  #tcp_ip = '10.10.10.71'
  tcp_ip = '192.168.0.130' # UCS540 serial converter for Pton
  pass
print('tcp_ip = {}'.format(tcp_ip));

# ttyUSB port
if not use_moxa:
    rtu_port = '/dev/ttyUSB2'
    pass

# Logger directory
log_dir = 'log';
