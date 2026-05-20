import os
import sys
import readline
import time
import datetime
from tzlocal import get_localzone;

import src.DWL_config as cg
import src.dwl as dwl

outfile = 'aho.txt'
timelength = 10
if len(sys.argv) > 1:
    outfile = sys.argv[1]
    pass
if len(sys.argv) > 2:
    timelength = int(sys.argv[2])
    pass
timelength = datetime.timedelta(seconds=timelength)

isSingle = False
interval = 0.1 # sec

timezone = get_localzone()
DWL = dwl.DWL(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port, timeout=0.5, isSingle=isSingle)

start = datetime.datetime.now(timezone)
now = start
with open(outfile, 'w') as f:
    while now - start < timelength:
        now = datetime.datetime.now(timezone)
        msg, val = DWL.get_angle()
        f.write(f'{now.timestamp()} {val[0]} {val[1]}\n')
        f.flush()
        time.sleep(interval)
        pass
    pass
