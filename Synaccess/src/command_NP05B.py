import sys as sy
import src.NP05B as NP05B

class Command:
    def __init__(self, NP05B):
        if NP05B is None:
            raise Exception(
                "Must provide NP05B object to Command_NP05B() init function")
        else:
            self._NP05B = NP05B
            self._log = self._NP05B.log
            self._port_info = self._NP05B.port_info
        return

    def HELP(self):
        wrstr = (
            "\nAvailable commands to the Synaccess NP-05B:\n"
            "ON [port]:  turn on port [port], for which the options are 1-5\n"
            "OFF [port]: turn off port [port], for which the options are 1-5\n"
            "ALL ON:  turn on all ports\n"
            "ALL OFF: turn off all ports\n"
            "REBOOT [port]: reboot port [port], for which the options are 1-5"
            "STATUS: print status of each port"
            "HELP: display this help menu"
            "EXIT: quit program\n")
        print(wrstr)
        wrstr = (
                "Port info:\n"
                "".join("    Port {}: {}\n".format(i+1, self._port_info[i]['label']) for i in len(self._port_info))
                );
        print(wrstr)
        return True

    def CMD(self, cmd):
        args = cmd.split()
        if len(args) == 0:
            return None
        cmdarg = args[0].upper()
        # Turn on/off or reboot specific port
        if cmdarg == 'ON' or cmdarg == 'OFF' or cmdarg == 'REBOOT':
            if len(args) == 2 and args[1].isdigit():
                port = int(args[1])
                if port <= 5 and port >= 1:
                    if cmdarg == 'ON':
                        self._NP05B.on(port)
                    elif cmdarg == 'OFF':
                        self._NP05B.off(port)
                    elif cmdarg == 'REBOOT':
                        self._NP05B.reboot(port)
                    else:
                        self._log.writelog(
                            "ERROR! Parsing error for command %s" % (' '.join(args)))
                        return False
                else:
                    self._log.writelog(
                        "ERROR! Provided port %d not in allowed range 1-5")
                    return False
            else:
                self._log.writelog(
                    "ERROR! Could not understand command %s" % (cmd))
                return False
        # Turn on/off or reboot all ports
        elif cmdarg == 'ALL':
            if args[1].upper() == 'ON':
                self._NP05B.all_on()
            elif args[1].upper() == 'OFF':
                self._NP05B.all_off()
            else:
                self._log.writelog("ERROR! Could not understand command %s" % (cmd))
                return False
        # Retrieve port status
        elif cmdarg == 'STATUS':
            outputs = self._NP05B.getstatus()
            self._log.writelog("\nPort power status:")
            if outputs == True:
                self._log.writelog('WARNING! Jumbled...try again')
            elif len(outputs) == 5:
                for i in range(len(outputs)):
                    self._log.writelog(
                        "Port %d = %s\n"
                        % (i + 1, bool(int(outputs[i]))))
                return outputs
            else:
                self._log.writelog('WARNING! Extra bytes, try again')
        # Print help menu
        elif cmdarg == 'HELP':
            self.HELP()
        # Exit the program
        elif cmdarg == 'EXIT':
            self._log.writelog("Exiting...")
            sy.exit(0)
        else:
            self._log.writelog("Error! Could not understand command %s" % (cmd))
            return False
        return True
