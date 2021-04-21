#from __future__ import print_function

import sys
import readline

# Check the python version
if sys.version_info.major == 2:
    print(
        "\ncommand_supply.py only works with Python 3\n"
        "Usage: python3 command_supply.py")
    sys.exit()

from src import NP05B          
from src import command_NP05B
import NP05B_config as config

        
if __name__ == "__main__":

    if config.use_tcp:
        np05b = NP05B.NP05B(tcp_ip=config.tcp_ip, user=config.user, password=config.password, log_dir=config.log_dir, port_info=config.port_info)
    else:
        np05b = NP05B.NP05B(rtu_port=config.ttyUSBPort, log_dir=config.log_dir, port_info=config.port_info)
        pass;
    CMD = command_NP05B.Command(np05b)

    #If user supplies a command-line argument, interpret it as a command to the cyberswitch
    if len(sys.argv[1:]) > 0:
        args = sys.argv[1:]
        command = ' '.join(args)
        result = CMD.CMD(command)
    else:
        #Otherwise, ask the user for a command
        while True:
            command = input('Synaccess command [HELP for help]: ')
            result = CMD.CMD(command)
            if result is True:
                print('Notification in command_NP05B(): Command executed successfully')
            elif result is False:
                print('Error in comand_NP05B(): Command failed...')
            else:
                pass;
            pass;
        pass;

    pass;
