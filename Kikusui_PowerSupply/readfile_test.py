import time

for i in range(100):
    f = open('/home/kyoto/nfs/scripts/wire_grid_loader/Encoder/Beaglebone/iamhere.txt', 'r')
    data = f.readlines()
    print(int(data[0]))

    f.close()

    time.sleep(0.1)
    pass
