import GravitySensorDetection as gsd
import time
from datetime import datetime

readtime = 600 #unit is sec
#readtime =10
t = 0
stime = 1
ts = time.time()
dt_now = str(datetime.now())
dt_now = dt_now.split(" ")[0].replace("-", "")
#print("Enter Gravity Sensor Device number")
#devnum = input()
#print("Enter Measuring direction number")
#direction = input()
#filename = 'datastrage/gravityoffset_'+dt_now+"dev"+devnum+"dirc"+direction+'.txt'
filename = 'datastrage/gravityoffset_'+dt_now+"dev"+"3or4"+"dirc"+"0"+'.txt'
#filename = "testfile.txt"

with open(filename, 'w') as f:
    while t - ts <= readtime: # if you want change time representation, you should rewrite this line(line10) and the line which define parameter t (line12)
        [a, b] = gsd.twoaxdtc()
        #[c, d] = gsd.twoaxdtc2()
        t = time.time()# - ts #time is written by UNIX time or Elapsed time since start
        print(t, a, b, sep=' ', end='\n', file=f)
        #print(t, a, b, c, d, sep=' ', end='\n', file=f)
        time.sleep(stime)

