import GravitySensorDetection as gsd
import time

readtime = 600 #unit is sec
t = 0
stime = 0.1
ts = time.time()
filename = 'gravity_'+str(ts)+'.txt'
with open(filename, 'w') as f:
    while t - ts <= readtime: # if you want change time representation, you should rewrite this line(line10) and the line which define parameter t (line12)
        [a, b] = gsd.twoaxdtc()
        [c, d] = gsd.twoaxdtc2()
        t = time.time()# - ts #time is written by UNIX time or Elapsed time since start
        #print(t, a, b, sep=' ', end='\n', file=f)
        print(t, a, b, c, d, sep=' ', end='\n', file=f)
        time.sleep(stime)

