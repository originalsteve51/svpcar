import gopigo3, time
import easygopigo3 as easy
from scanner import Scanner
from threading import Thread
import paho.mqtt.client as mqtt

ROVER_TOPIC = "rover"

class Rover(object):
    scanner = None
    _gpg = None
    _GPG = None
    _logger = None
    _broker_ip = None
    nudge_interval = 0.0

    def __init__(self, gpg, GPG, broker_ip):
        self._gpg = gpg
        self._GPG = GPG
        if (broker_ip is None) == False:
            self._broker_ip = broker_ip
        self._running = True
        # make sure there is a Scanner instance
        if self.scanner is None:
            self.scanner = Scanner(self._GPG, self._gpg)
        self.scanner.reset()

	# use mqtt client api to post messages to an mqtt broker
	# subscribers to the 'rover' topic can monitor messages
        if (self._broker_ip is None) == False:
            self._logger = mqtt.Client("rover logger")
            self._logger.connect(self._broker_ip)

    def set_nudge_interval(self, interval):
        self.nudge_interval = interval

    def terminate(self):
        self._running = False
        self._gpg.stop()
        self.scanner.terminate()

    def rove(self):
        self._running = True

        # the scanner runs on its own thread, constantly looking forward and to both
        # sides for obstructions.
        self.scanner.count = 9999
        self.scanner.reset()

        scannerThread = Thread(target=self.scanner.run)
        scannerThread.start()

        # before roving, wait for the scanner to see something (it is still unaware of anything 
        # as long as the distances are 0.0)
        while self.scanner.highDist[1]==0.0 or self.scanner.lowDist[1]==0.0:
            time.sleep(2)

        while self._running:
            rHigh = self.scanner.highDist[0]
            rLow = self.scanner.lowDist[0]
            high = self.scanner.highDist[1]
            low = self.scanner.lowDist[1]
            lHigh = self.scanner.highDist[2]
            lLow = self.scanner.lowDist[2]

            if  high > 10.0 and low > 7.0 and lHigh > 5.0 and lLow > 5.0 and rHigh > 5.0 and rLow > 5.0:
                self._gpg.set_speed(200)
                self._gpg.drive_inches(2, False)
                time.sleep(self.nudge_interval)
            elif high > 5.0 and low > 5.0 and lHigh > 4.0 and lLow > 4.0 and rHigh > 4.0 and rLow > 4.0:
                self._gpg.set_speed(50)
                self._gpg.drive_inches(2, False)
                time.sleep(self.nudge_interval)
            elif high < 4.0 or low < 4.0 or lHigh < 4.0 or lLow < 4.0 or rHigh < 4.0 or rLow < 4.0:
                self._gpg.set_speed(50)
                self._gpg.drive_inches(-3, False)
                time.sleep(self.nudge_interval)
                if (lLow + lHigh < rLow + rHigh):
                    self.post_log ("turning LEFT: " + str(lLow + lHigh) + " < " +  str(rLow + rHigh))
                    self._gpg.turn_degrees(-50, False)
                else:
                    self.post_log ("turning RIGHT: " + str(lLow + lHigh) + " >= " + str(rLow + rHigh))
                    self._gpg.turn_degrees(50, False)
                time.sleep(self.nudge_interval)

    def post_log(self, msg):
        if (self._logger is None) == False:
            self._logger.publish(ROVER_TOPIC, msg)
        else:
            pass
