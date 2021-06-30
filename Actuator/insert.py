import sys, os, argparse, time
from WiregridActuator import WiregridActuator, make_parser

def insert_parser(parser = None):
    if parser is None:
        parser = argparse.ArgumentParser()

    pgroup = parser.add_argument_group('Insert Options')
<<<<<<< HEAD
    pgroup.add_argument('--homing' , dest='homing' , action='store_true', help='Homing to the opposite side (inside) slowly' , default=False);
=======
    pgroup.add_option('--homing' , dest='homing' , action='store_true', help='Homing to the opposite side (inside) slowly' , default=False);
>>>>>>> 50c329bac35f20a92b4787dcf119f424aeb2a2be
    return parser

if __name__ == '__main__':
    wg_parser = make_parser()
    parser = insert_parser(wg_parser)

    args = parser.parse_args()

<<<<<<< HEAD
    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    verbose       = args.verbose
    wg_actuator = WiregridActuator(actuator_dev, sleep=sleep, verbose=verbose)
=======
    interval_time = args.interval_time
    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    wg_actuator = WiregridActuator(agent, actuator_dev, interval_time, sleep=sleep, verbose=args.verbose)
>>>>>>> 50c329bac35f20a92b4787dcf119f424aeb2a2be

    if args.homing :
        ret, msg = wg_actuator.insert_homing()
    else :
        ret, msg = wg_actuator.insert()
        pass

    print('{}: {}'.format('Success!' if ret else 'Failed!',  msg))

