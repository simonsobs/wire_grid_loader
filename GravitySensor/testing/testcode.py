import GravitySensorDetection2 as gsd
import time

gsd.GravitySensor.__init__(3)
a = gsd.GravitySensor.oneax(3)
print('oneax mode output is', a);
[b, c] = gsd.GravitySensor.twoax(3)
print('X =', b)
print('Y =', c)


