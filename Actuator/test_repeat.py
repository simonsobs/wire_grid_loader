import sys, os, argparse, time
from WiregridActuator import WiregridActuator, make_parser

NLOOP = 10;

if __name__ == '__main__':
    wg_parser = make_parser()

    args = wg_parser.parse_args()

    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    verbose       = args.verbose
    print('verbose = {}'.format(verbose))
    wg_actuator = WiregridActuator(actuator_dev, sleep=sleep, verbose=verbose)

    for i in range(NLOOP) :
        print('**** {}th insert&eject ****'.format(i));
        print();
        print('** {}th insert **'.format(i));
        time.sleep(1);
        ret, msg = wg_actuator.insert()
        print('{} ({}th insert) : {}'.format('Success !' if ret else 'Failed!',  i, msg));
        print('** {}th eject  **'.format(i));
        time.sleep(1);
        ret, msg = wg_actuator.eject()
        print('{} ({}th eject)  : {}'.format('Success !' if ret else 'Failed!',  i, msg));
        print();
        pass;
 
