# Import global configuration to define the experiment environment
import socket

# Boolean flag for Ethernet or USB
use_tcp = True

# User / Password for NP05B
user = 'admin';
password = 'admin';

# IP address
hostname = socket.gethostname();
print('hostname : {}'.format(hostname));
if hostname.endswith('hepnet.scphys.kyoto-u.ac.jp'):
  tcp_ip = '192.168.1.70' # Synaccess at Kyoto
elif hostname == 'cmb-daq01' :
  tcp_ip = '192.168.0.100' # Synaccess at Tokyo
else :
  print('WARNING!! There is no suitable hostname option in "NP05B_config.py" to switch IP address for the Synaccess power strip.')
  tcp_ip = '10.10.10.0.1'
  pass
print('tcp_ip = {}'.format(tcp_ip));

# ttyUSB port
if not use_tcp:
    rtu_port = '/dev/ttyUSB2'
    pass

# Label of each ports in Synaccess
port_info = [
        {'name':'CH1:USB&LAN&Serial' , 'label':'USB Hub (Beaglebones), LAN Hub, Serial Converter'  }, # ch1
        {'name':'CH2:Encoder&Gravity', 'label':'Encoder, Gravity Sensor, Stopper switch'                  }, # ch2
        {'name':'CH3:Fan'            , 'label':'Electronics Box Fans'                      }, # ch3
        {'name':'CH4:DC24V'          , 'label':'DC 24V Power Supply for Actuator&Stopper'          }, # ch4
        {'name':'CH5:Motor'          , 'label':'KIKUSUI Power Supply for Motor'            }, # ch5
        ];

# Logger directory
logdir = 'log';
