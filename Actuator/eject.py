import sys, os, argparse, time
from WiregridActuator import WiregridActuator, make_parser

def eject_parser(parser = None):
    if parser is None:
        parser = argparse.ArgumentParser()
        pass

    pgroup = parser.add_argument_group('Eject Options')
    pgroup.add_argument('--homing' , dest='homing' , action='store_true', help='Homing to the motor side (outside) slowly' , default=False);
    return parser

if __name__ == '__main__':
    wg_parser = make_parser()
    parser = eject_parser(wg_parser)

    args = parser.parse_args()

    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    verbose       = args.verbose
    wg_actuator = WiregridActuator(actuator_dev, sleep=sleep, verbose=verbose)

    if args.homing :
        ret, msg = wg_actuator.eject_homing()
    else :
        ret, msg = wg_actuator.eject()
        pass

    print('{}: {}'.format('Success!' if ret else 'Failed!',  msg))

