import os
import sys
import readline
import time

import src.DWL_config as cg
import src.dwl_cp as dwl

DWL = dwl.DWL(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5)

angleX = DWL.get_single_angle()

print(angleX)
