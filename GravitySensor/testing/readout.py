import GravitySensorDetection as gsd
import time

readtime = 10 #unit is sec
t = 0
stime = 0.1
ts = time.time()
filename = 'gravity_'+str(ts)+'.txt'
with open(filename, 'w') as f:
    while t <= readtime: 
        [a, b] = gsd.twoaxdtc()
        t = time.time() - ts
        print(t, a, b, sep=' ', end='\n', file=f)
        time.sleep(stime)

