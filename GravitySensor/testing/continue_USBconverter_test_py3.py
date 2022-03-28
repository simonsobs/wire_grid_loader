import os
import sys
from datetime import datetime
import time

from USBconverter_test_py3 import *



if __name__ == '__main__':
    output = '20220328_4th-rot.dat'
    outfile = open(output, 'w')

    dt_limit = 60 # seconds

    dt = 0
    start = time.time()
    while dt<dt_limit:
        t = time.time()
        x, y = main()
        print(x,y)
        outfile.write(f'{t} {x} {y}\n')
        #dt = (t - start).seconds
        dt = (t - start)
        print(dt)
        pass
