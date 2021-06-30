import sys, os, argparse, time

# import classes / configs
from src.Actuator    import Actuator
from src.log_actuator    import Log as log_actuator
from LimitSwitch.src.LimitSwitch import LimitSwitch
from Stopper.src.Stopper     import Stopper
from LimitSwitch import limitswitch_config
from Stopper import stopper_config

class WiregridActuator:
    def __init__(self, actuator_dev='/dev/ttyUSB0', sleep=0.10, verbose=0):
        self.actuator_dev  = actuator_dev
        self.sleep         = sleep
        self.log           = log_actuator(logdir='./log')
        self.verbose       = verbose

        try:
            self.actuator    = Actuator(self.actuator_dev, sleep=self.sleep, verbose=self.verbose)
        except Exception as e:
            msg = 'Failed to initialize Actuator instance! | ERROR = "actuator is None"'
            self.log.writelog(msg)
            self.actuator = None
            pass
        self.limitswitch = LimitSwitch(limitswitch_config.GPIOpinInfo, logdir='./log')
        self.stopper     = Stopper    (stopper_config    .GPIOpinInfo, logdir='./log') 
        pass

    ######################
    # Internal functions #
    ######################

    def __check_connect(self):
        if self.actuator is None :
            msg = 'No connection to the actuator. | ERROR = "actuator is None"'
            return False, msg
        else :
            ret, msg = self.actuator.check_connect()
            if not ret :
                msg = 'No connection to the actuator. | ERROR = "%s"' %  msg
                return False, msg
            pass
        return True, 'Connection is OK.'

    def __reconnect(self):
        self.log.writelog('*** Trying to reconnect... ***')
        # reconnect
        try :
            if self.actuator : del self.actuator
            self.actuator    = Actuator(self.actuator_dev, sleep=self.sleep, verbose=self.verbose)
        except Exception as e:
            msg = 'Failed to initialize Actuator! | ERROR: %s' % e
            self.log.writelog(msg)
            self.actuator = None
            return False, msg
        # reinitialize cmd
        ret, msg = self.__check_connect()
        if ret :
            msg = 'Successfully reconnected to the actuator!'
            self.log.writelog(msg)
            return True, msg
        else :
            #msg = 'Failed to reconnect to the actuator!'
            self.log.writelog(msg)
            if self.actuator : del self.actuator
            self.actuator = None
            return False, msg


    def __forward(self, distance, speedrate=0.1):
        distance = abs(distance)
        LSL2 = 0 # left  actuator opposite limitswitch
        LSR2 = 0 # right actuator opposite limitswitch
        if self.verbose>0 : self.log.writelog('__forward() : Checking limitswitch on opposite side (outside)');
        LSL2,LSR2 = self.limitswitch.get_onoff(pinname=['LSL2','LSR2'])
        if LSL2==0 and LSR2==0 : 
            if self.verbose>0 : self.log.writelog('__forward() : Moving (distance={}, speedrate={})'.format(distance,speedrate));
            status, msg = self.actuator.move(distance, speedrate)
            if status<0 : return False, msg
        else :
            self.log.writelog('__forward() : WARNING! One of limit switches on opposite side (inside) is ON (LSL2={}, LSR2={})!'.format(LSL2, LSR2));
            self.log.writelog('__forward() :   --> Did not move.');
            pass
        isrun = True
        while LSL2==0 and LSR2==0 and isrun :
            LSL2,LSR2 = self.limitswitch.get_onoff(pinname=['LSL2','LSR2'])
            isrun = self.actuator.isRun()
            pass
        self.actuator.hold()
        if LSL2 or LSR2 :
            self.log.writelog('__forward() : Stopped moving because one of limit switches on opposite side (inside) is ON (LSL2={}, LSR2={})!'.format(LSL2, LSR2))
            pass
        if self.verbose>0 : self.log.writelog('__forward() : Releasing the actuator')
        self.actuator.release()
        return True, 'Finish forward(distance={}, speedrate={})'.format(distance, speedrate)

    def __backward(self, distance, speedrate=0.1):
        distance = abs(distance)
        if self.verbose>0 : self.log.writelog('__backward() : Checking limitswitch on motor side');
        LSL1 = 0 # left  actuator limitswitch @ motor (outside)
        LSR1 = 0 # right actuator limitswitch @ motor (outside)
        LSL1,LSR1 = self.limitswitch.get_onoff(pinname=['LSL1','LSR1'])
        if LSL1==0 and LSR1==0 : 
            if self.verbose>0 : self.log.writelog('__backward() : Moving (distance={}, speedrate={})'.format(distance,speedrate));
            status, msg = self.actuator.move(-1*distance, speedrate)
            if status<0 : return False, msg
        else :
            self.log.writelog('__backward() : WARNING! One of limit switches on motor side (outside) is ON (LSL1={}, LSR1={})!'.format(LSL1, LSR1));
            self.log.writelog('__backward() :   --> Did not move.');
            pass
        isrun = True
        while LSL1==0 and LSR1==0 and isrun :
            LSL1, LSR1 = self.limitswitch.get_onoff(pinname=['LSL1','LSR1'])
            isrun = self.actuator.isRun()
            if self.verbose>0 : self.log.writelog('__backward() : LSL1={}, LSR1={}, run={}'.format(LSL1,LSR1,isrun))
            pass
        self.actuator.hold()
        if LSL1 or LSR1 :
            self.log.writelog('__backward() : Stopped moving because one of limit switches on motor side (outside) is ON (LSL1={}, LSR1={})!'.format(LSL1, LSR1))
            pass
        if self.verbose>0 : self.log.writelog('__backward() : Releasing the actuator')
        self.actuator.release()
        return True, 'Finish backward(distance={}, speedrate={})'.format(distance, speedrate)


    def  __insert(self, main_distance=850, main_speedrate=1.0):
        # check motor limitswitch
        if self.verbose>0 : self.log.writelog('__insert() : Cheking the motor side limit switch')
        LSL1,LSR1 = self.limitswitch.get_onoff(pinname=['LSL1','LSR1'])
        if LSL1==0 and LSR1==0 :
            self.log.writelog('__insert() : WARNING!: The limitswitch on motor side is NOT ON before inserting.')
            if main_speedrate>0.1 :  
                self.log.writelog('__insert() : WARNING!: --> Change speedrate: {} --> 0.1'.format(main_speedrate))
                main_speedrate = 0.1
                pass
        else :
            self.log.writelog('__insert() : The limitswitch on motor side is ON before inserting.')
            self.log.writelog('__insert() : --> Checking connection to the actuator')
            # check connection
            ret, msg = self.__check_connect()
            self.log.writelog(msg)
            # reconnect
            if not ret :
                self.log.writelog('__insert() : Trying to reconnect to the actuator...')
                ret2, msg2 = self.__reconnect()
                self.log.writelog(msg2)
                if not ret2 :
                    self.log.writelog('__insert() : Could not connect to the actuator even after reconnection!')
                    self.log.writelog('__insert() : --> Stop inserting [__insert()] !')
                    return False
                    pass
                pass
            pass

        # release stopper
        if self.verbose>0 : self.log.writelog('__insert() : Unlocking (Powering on) the stopper')
        if self.stopper.set_allon() < 0 : 
            self.log.writelog('__insert() : ERROR!: Stopper set_allon() --> STOP')
            return False
        if self.stopper.set_allon() < 0 : 
            self.log.writelog('__insert() : ERROR!: Stopper set_allon() --> STOP')
            return False
        # forward a bit
        if self.verbose>0 : self.log.writelog('__insert() : First forwarding')
        status, msg  = self.__forward(20, speedrate=0.1)
        if not status : 
            self.log.writelog('__insert() : ERROR!:(in first forwarding) {}'.format(msg))
            return False
        # check limitswitch
        if self.verbose>0 : self.log.writelog('__insert() : Checking the motor side limit switch')
        LSL1,LSR1 = self.limitswitch.get_onoff(pinname=['LSL1','LSR1'])
        #print('LSL1,LSR1',LSL1,LSR1);
        if LSL1==1 or LSR1==1 :
            self.log.writelog('__insert() : ERROR!: The limitswitch on motor side is NOT OFF after moving forward without stopper.--> STOP')
            return False
        # power off stopper
        if self.verbose>0 : self.log.writelog('__insert() : Locking (Powering off) the stopper')
        if self.stopper.set_alloff() < 0 : 
            self.log.writelog('__insert() : ERROR!: Stopper set_alloff() --> STOP')
            return  False
        # check stopper
        if self.verbose>0 : self.log.writelog('__insert() : Checking the stopper')
        while True :
            onoff_st = self.stopper.get_onoff()
            if not any(onoff_st) :
                break
            pass
        time.sleep(1)
        # main forward
        if self.verbose>0 : self.log.writelog('__insert() : Main forwarding')
        status, msg = self.__forward(main_distance, speedrate=main_speedrate)
        if not status : 
            self.log.writelog('__insert() : ERROR!:(in main forwarding) {}'.format(msg))
            return False
        # last forward
        if self.verbose>0 : self.log.writelog('__insert() : Last forwarding')
        status, msg = self.__forward(200, speedrate=0.1)
        if not status : 
            self.log.writelog('__insert() : ERROR!:(in last forwarding) {}'.format(msg))
            return False
        # check limitswitch
        if self.verbose>0 : self.log.writelog('__insert() : Checking the opposite side (inside) limit switch')
        LSL2,LSR2 = self.limitswitch.get_onoff(pinname=['LSL2','LSR2'])
        if LSL2==0 and LSR2==0 :
            self.log.writelog('__insert() : ERROR!: The limitswitch on opposite side is NOT ON after __insert(). --> STOP')
            return False
        return True


    def __eject(self, main_distance=850, main_speedrate=1.0) :
        # check motor limitswitch
        if self.verbose>0 : self.log.writelog('__eject() : Cheking the opposite side (inside) limit switch')
        LSL2,LSR2 = self.limitswitch.get_onoff(pinname=['LSL2','LSR2'])
        if LSL2==0 and LSR2==0 :
            self.log.writelog('__eject() : WARNING!: The limitswitch on opposite side (inside) is NOT ON before ejecting.')
            if main_speedrate>0.1 :  
                self.log.writelog('__eject() : WARNING!: --> Change speedrate: {} --> 0.1'.format(main_speedrate))
                main_speedrate = 0.1
                pass
            pass


        # release stopper
        if self.verbose>0 : self.log.writelog('__eject() : Unlocking (Powering on) the stopper')
        if self.stopper.set_allon() < 0 : 
            self.log.writelog('__eject() : ERROR!: Stopper set_allon() --> STOP')
            return False
        if self.stopper.set_allon() < 0 : 
            self.log.writelog('__eject() : ERROR!: Stopper set_allon() --> STOP')
            return False
        # backward a bit
        if self.verbose>0 : self.log.writelog('__eject() : First backwarding')
        status, msg = self.__backward(20, speedrate=0.1)
        if not status : 
            self.log.writelog('__eject() : ERROR!:(in first backwarding) {}'.format(msg))
            return False
        # check limitswitch
        if self.verbose>0 : self.log.writelog('__eject() : Cheking the opposite side (inside) limit switch')
        LSL2,LSR2 = self.limitswitch.get_onoff(pinname=['LSL2','LSR2'])
        if LSL2==1 or LSR2==1 :
            self.log.writelog('__eject() : ERROR!: The limitswitch on opposite side (inside) is NOT OFF after moving backward. --> STOP')
            return False
        time.sleep(1)
        # main backward
        if self.verbose>0 : self.log.writelog('__eject() : Main backwarding')
        status, msg = self.__backward(main_distance, speedrate=main_speedrate)
        if not status : 
            self.log.writelog('__eject() : ERROR!:(in main backwarding) {}'.format(msg))
            return False
        # last backward
        if self.verbose>0 : self.log.writelog('__eject() : Last backwarding')
        status, msg = self.__backward(200, speedrate=0.1)
        if not status : 
            self.log.writelog('__eject() : ERROR!:(in last backwarding) {}'.format(msg))
            return False
        # check limitswitch
        if self.verbose>0 : self.log.writelog('__eject() : Checking the motor side limit switch')
        LSL1,LSR1 = self.limitswitch.get_onoff(pinname=['LSL1','LSR1'])
        if LSL1==0 and LSR1==0 :
            self.log.writelog('__eject() : ERROR!: The limitswitch on motor side (outside) is NOT ON after __eject(). --> STOP')
            return False
        # power off stopper
        if self.verbose>0 : self.log.writelog('__eject() : Locking (Powering off) the stopper')
        self.log.writelog('__eject() : Stopper set_alloff() (Lock the actuator)')
        if self.stopper.set_alloff() < 0 : 
            self.log.writelog('__eject() : ERROR!: Stopper set_alloff() --> STOP')
            return  False
        return True


    ##################
    # Main functions #
    ##################

    def check_limitswitch(self, pinname=None):
        onoffs = []
        msg = ''
        onoffs    = self.limitswitch.get_onoff(pinname)
        pinnames  = self.limitswitch.get_pinname(pinname)
        pinlabels = self.limitswitch.get_label(pinname)
        for i, pinname in enumerate(pinnames) :
            pinlabel = pinlabels[i]
            msg += '{:10s} ({:20s}) : {}\n'.format(pinname, pinlabel, 'ON' if onoffs[i] else 'OFF')
            pass
        self.log.writelog(msg)
        return onoffs, msg

    def check_stopper(self, pinname=None):
        onoffs = []
        msg = ''
        onoffs   = self.stopper.get_onoff(pinname)
        pinnames = self.stopper.get_pinname(pinname)
        pinlabels= self.stopper.get_label(pinname)
        for i, pinname in enumerate(pinnames) :
            pinlabel = pinlabels[i]
            msg += '{:10s} ({:20s}) : {}\n'.format(pinname, pinlabel, 'ON' if onoffs[i] else 'OFF')
            pass
        self.log.writelog(msg)
        return onoffs, msg


    def insert(self):
        time.sleep(1)
        # Moving commands
        ret = self.__insert(850, 1.0)
        if not ret :
            self.log.writelog('Failed to insert!')
            return False, 'Failed insert() in __insert(850,1.0)'
        return True, 'Finish insert()'


    def eject(self):
        time.sleep(1)
        # Moving commands
        ret = self.__eject(850, 1.0)
        if not ret :
            self.log.writelog('Failed to insert!')
            return False, 'Failed eject() in __eject(850,1.0)'
        return True, 'Finish eject()'


    def insert_homing(self):
        time.sleep(1)
        # Moving commands
        ret = self.__insert(1000, 0.1)
        if not ret :
            self.log.writelog('Failed to insert_homing!')
            return False, 'Failed insert_homing() in __insert(1000,0.1)'
        return True, 'Finish insert_homing()'


    def eject_homing(self):
        time.sleep(1)
        # Moving commands
        ret = self.__eject(1000, 0.1)
        if not ret :
            self.log.writelog('Failed to eject_homing!')
            return False, 'Failed eject_homing() in __eject(1000,0.1)'
        return True, 'Finish eject_homing()'


    def stop(self):
        self.log.writelog('Try to stop and hold the actuator.')
        # This will disable move() command in Actuator class until release() is called.
        self.actuator.STOP = True 
        # Hold the actuator
        ret = self.actuator.hold()
        return True, 'Finish stop()'


    def release(self):
        self.log.writelog('Try to release the actuator.')
        # This will enable move() command in Actuator class.
        self.actuator.STOP = False
        # Relase the actuator
        ret = self.actuator.release()
        return True, 'Finish release()'


    def reconnect(self, devfile=None):
        self.log.writelog('reconnect() will power off the actuator for a short time.')
        self.log.writelog('Usually, please don\'t use this task.')
        # check connection
        ret, msg = self.__check_connect()
        self.log.writelog(msg)
        # try to reconnect if no connection 
        if ret :
            msg = 'Did not tried to reconnect the actuator beacuase the connection is good.'
            self.log.writelog(msg)
            return ret, msg
        else :
            # check new device file
            if devfile is None: devfile = self.actuator_dev
            # check device file
            lsdev = os.listdir('/dev/')
            self.log.writelog('device files in /dev: {}'.format(lsdev))
            if not os.path.exists(devfile) :
                msg = 'ERROR! There is no actuator device file ({}).'.format(devfile)
                self.log.writelog(msg)
                return False, msg
            # set device file
            self.actuator_dev = devfile

            # reconnect
            self.log.writelog('Trying to reconnect to the actuator...')
            ret2, msg2 = self.__reconnect()
            return ret2, msg2


    # End of class WiregridActuator


def make_parser(parser = None):
    if parser is None:
        parser = argparse.ArgumentParser()

    pgroup = parser.add_argument_group('WiregridActuator Options')
    pgroup.add_argument('--actuator-dev', dest='actuator_dev', type=str, default='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AL01WX4M-if00-port0',
                        help='')
    pgroup.add_argument('--sleep', dest='sleep', type=float, default=0.10,
                        help='sleep time for every actuator command')
    pgroup.add_argument('--verbose', dest='verbose', type=int, default=1,
                        help='')
    return parser

if __name__ == '__main__':
    parser = make_parser()

    args = parser.parse_args()

    actuator_dev  = args.actuator_dev
    sleep         = args.sleep
    #print('actuator_dev  = {} (type={})'.format(actuator_dev , type(actuator_dev)))
    wg_actuator = WiregridActuator(actuator_dev, sleep=sleep, verbose=args.verbose)
    print(wg_actuator.check_stopper())
    print(wg_actuator.check_limitswitch())

