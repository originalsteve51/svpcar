
from adxl345 import ADXL345
import time
import paho.mqtt.client as mqtt

MONITOR_TOPIC = "monitor"

class Monitor(object):
    _running = False
    _accelerometer = None
    _gpg = None
    _rover = None
    _logger = None
    _broker_ip = None
    xyz = [0.0, 0.0, 0.0]
    tilt = 0.0

    def __init__(self, gpg, rover, broker_ip):
        self._accelerometer = ADXL345()
        self._gpg = gpg
        self._rover = rover
        self._broker_ip = broker_ip
        _running = True

        if (broker_ip is None) == False:
            self._logger = mqtt.Client("monitor logger")
            self._logger.connect(self._broker_ip)

    def run(self):
        self._running = True
        self._accelerometer.enableMeasurement()
        last_tilt = 0.0
        while self._running:
            self.xyz = self._accelerometer.getAxes(True)
            self.tilt = self.xyz['x'] ** 2 + self.xyz['y'] ** 2 + (self.xyz['z']-1.0) ** 2
            self.post_log("tilt: "+str(self.tilt))
            # when two consecutive tilts are too musc, stop the car
            if self.tilt > 0.1 and last_tilt > 0.1:
                self.post_log("========> svpcar max tilt value has been exceeded <============")
                self._gpg.set_led(self._gpg.LED_RIGHT_EYE, 255)
                if (self._rover is None) == False:
                    self._rover.terminate()

                # print("==========> Tilt limit exceeded!! {:4.3f} <============".format(self.tilt));
            else:
		# two consecutive over-tilts are needed to shut down, so
		# record each tilt value as one of the values to use
                last_tilt = self.tilt
                self._gpg.set_led(self._gpg.LED_RIGHT_EYE, 0)
                
            # print("xyz: {}, tilt: {}".format(self.xyz, self.tilt))
            time.sleep(1)
            
    def terminate(self):
        self._running = False
        
    def setRover(self, rover):
        self._rover = rover

    def post_log(self, msg):
        if (self._logger is None) == False:
            self._logger.publish(MONITOR_TOPIC, msg)
        else:
            pass
