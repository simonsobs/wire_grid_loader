import os
import sys
from datetime import datetime
import time

from USBconverter_test_py3 import *


if __name__ == '__main__':
    dt_now = str(datetime.now())
    dt_now = dt_now.split(" ")[0].replace("-","")
    print("Enter Gravity Sensor Device number")
    devnum = input()
    print("Enter Measuring direction number")
    direction = input()
    filename = "gravityoffset_"+dt_now+"dev"+devnum+"dirc"+direction+".dat"
    outfile = open(filename, 'w')

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
