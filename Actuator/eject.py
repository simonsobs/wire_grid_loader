import sys, os, argparse, time
from WiregridActuator import WiregridActuator, make_parser

def eject__parser(parser = None):
    if parser is None:
        parser = argparse.ArgumentParser()

    pgroup = parser.add_argument_group('Eject  Options')
    pgroup.add_option('--homing' , dest='homing' , action='store_true', help='Homing to the motor side (outside) slowly' , default=False);
    return parser

if __name__ == '__main__':
    wg_parser = make_parser()
    parser = eject_parser(wg_parser)

    args = parser.parse_args()

    interval_time = args.interval_time
    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    wg_actuator = WiregridActuator(agent, actuator_dev, interval_time, sleep=sleep, verbose=args.verbose)

    if args.homing :
        ret, msg = wg_actuator.eject_homing()
    else :
        ret, msg = wg_actuator.eject()
        pass

    print('{}: {}'.format('Success!' if ret else 'Failed!',  msg))

