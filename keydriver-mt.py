#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cmd, gopigo3, time, sys
import easygopigo3 as easy
from threading import Thread
from rover import Rover
from monitors import Monitor


class KeyboardDriver(cmd.Cmd):
    intro = 'Welcome to the svpcar robot vehicle. \
    Type help or ? to list commands.\n'

    prompt = '(key command) '
    file = None
    rover = None
    monitor = None
    _gpg = None
    _GPG = None
    # address where mqtt broker is running...for logging
    broker_ip = None

    def __init__(self, server_ip):
        self.broker_ip = server_ip

        # init the parent class (cmd.Cmd)
        super(KeyboardDriver, self).__init__()

        # Set up the drivers for the motors and sensors
        self._gpg = easy.EasyGoPiGo3()
        self._GPG = gopigo3.GoPiGo3()
        self._gpg.set_speed(100)

    def do_monitor(self, arg):
        if self.monitor is None:
            self.monitor = Monitor(self._gpg, self.rover, self.broker_ip)

        monitorThread = Thread(target=self.monitor.run)
        monitorThread.start()

    # ----- basic svpcar commands -----
    def do_stop(self, arg):
        'Stop the svpcar'
        self.stopEverything(False)

    def do_fwd(self, arg):
        'Move the svpcar forward by the specified number of inches:  fwd 10'
        try:
            self._gpg.drive_inches(int(arg), False)
        except Exception:
            print ("You need to provide an integer number of inches to move")

    def do_back(self, arg):
        'Move the svpcar backward by the specified number of inches:  back 10'
        try:
            self._gpg.drive_inches(-1 * int(arg), False)
        except Exception:
            print ("You need to provide an integer number of inches to move")

    def do_setspeed(self, arg):
        'Set the svpcar speed:  setspeed 100 is slow, 300 is fast, 500 is too fast'
        try:
            self._gpg.set_speed(int(arg))
        except Exception:
            print ("You need to provide a positive integer value")

    def do_right(self, arg):
        'Turn svpcar right by given number of degrees:  RIGHT 20'
        try:
            self.nudge_rover(1.0)
            self._gpg.turn_degrees(int(arg), False)
            self.nudge_complete()
        except Exception:
            print ("You need to provide an integer number of degrees")

    def do_left(self, arg):
        'Turn svpcar left by given number of degrees:  LEFT 90'
        try:
            self.nudge_rover(1.0)
            self._gpg.turn_degrees(-1 * int(arg), False)
            self.nudge_complete()
        except Exception:
            print ("You need to provide an integer number of degrees")

    def do_rove(self, arg):
        if self.rover is None:
            self.rover = Rover(self._gpg, self._GPG, self.broker_ip)

        if (self.monitor is None) == False:
            self.monitor.setRover(self.rover)

        roverThread = Thread(target=self.rover.rove)
        roverThread.start()

    def do_bye(self, arg):
        'Stop recording, stop the svpcar, and exit:  BYE'
        print('Thank you for using svpcar')

        if (self.rover is None) == False:
            self.rover.terminate()
        if (self.monitor is None) == False:
            self.monitor.terminate()
        self._gpg.reset_all()
        self.close()
        return True

    # ----- record and playback -----
    def do_record(self, arg):
        'Save future commands to filename:  RECORD rose.cmd'
        self.file = open(arg, 'w')

    def do_playback(self, arg):
        'Playback commands from a file:  PLAYBACK rose.cmd'
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())

    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def do_battery(self, arg):
        print(self._gpg.get_voltage_battery())

    # servo and distance sensor
    def do_measure(self, arg):
        'Measure distance in inches to an obstacle'
        distance = self.measure()
        print("Distance Sensor Reading: {} inches ".format(distance))

    def do_allmeasurements(self, arg):
        if self.rover is None:
            self.rover = Rover(self._gpg, self._GPG)
        print(self.rover.scanner.highDist,'\n', self.rover.scanner.lowDist)

    def measure(self):
        if self.rover is None:
            self.rover = Rover(self._gpg, self._GPG)
        return self.rover.scanner.distanceSensor.read_inches()

    def do_rotate(self, arg):
        if self.rover is None:
            self.rover = Rover(self._gpg, self._GPG)

        self.rover.scanner.aim(arg, self._GPG.SERVO_2)

    def do_tilt(self, arg):
        if self.rover is None:
            self.rover = Rover(self._gpg, self._GPG)

        self.rover.scanner.aim(arg, self._GPG.SERVO_1)

    def stopEverything(self, resetFlag):
        print("=======>  Stopping everything!")
        if resetFlag:
            self._gpg.reset_all()

        if (self.rover is None) == False:
            self.rover.terminate()

        if (self.monitor is None) == False:
            self.monitor.terminate()

    def nudge_rover(self, nudge_interval):
        if (self.rover is None) == False:
            self.rover.set_nudge_interval(nudge_interval)

    def nudge_complete(self):
        if (self.rover is None) == False:
            self.rover.set_nudge_interval(0.0)

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':

    # cmd line arg that passes ip address where mqtt broker is running
    # mqtt used for logging
    if len(sys.argv) == 2:
        broker_ip = sys.argv[1]
    else:
        broker_ip = None

    cmdProcessor = None
    try:
        cmdProcessor = KeyboardDriver(broker_ip)
        print ("GoPiGo3 controller & peripheral objects instantiated and initialized")

        # Keyboard command processor 
        cmdProcessor.cmdloop()
    except KeyboardInterrupt:
        # when things go very wrong, ctrl-c in the cmdloop breaks it and we end up here
        # with a KeyboardInterrupt. shut the thing down, otherwise the scanner keeps scanning
        # and other asynchronous activity continues.
        cmdProcessor.stopEverything(True)
    except Exception as e:
        print ("Cannot instantiate GoPiGo3 controller & peripheral objects for this vehicle")
        print (e)
        exit(1)
