import gopigo3, time

class Scanner(object):
    distanceSensor = None
    _GPG = None
    _gpg = None
    
    highDist = [0.0, 0.0, 0.0]
    lowDist = [0.0, 0.0, 0.0]
    
    count = 0
    
    def __init__(self, GPG, gpg):
        self._running = True
        count = 1
        self._GPG = GPG
        self._gpg = gpg
        self.distanceSensor = self._gpg.init_distance_sensor()

    def reset(self):
        self.highDist = [0.0, 0.0, 0.0]
        self.lowDist = [0.0, 0.0, 0.0]

    def terminate(self):  
        self._running = False
    
    def run(self):
        LEFT = [140, 115]
        CENTER = 97
        RIGHT = [50, 75]
        HIGH = 135
        LOW = 180
        thetaIdx = 0
        self._running = True
        while self._running and self.count > 0:
            if thetaIdx == 0:
                thetaIdx = 1
            else:
                thetaIdx = 0
            for phi in [HIGH,LOW]:
                if self._running==False:
                    break
                self.aim(phi, self._GPG.SERVO_1)
                for theta in [RIGHT[thetaIdx], CENTER, LEFT[thetaIdx], CENTER]:
                    if self._running==False:
                        break
                    self.aim (theta, self._GPG.SERVO_2)
                    distance = self.distanceSensor.read_inches()
                    if phi == HIGH:
                        if theta == LEFT[0] or theta == LEFT[1]:
                            self.highDist[0] = distance
                        elif theta == CENTER:
                            self.highDist[1] = distance
                        else:
                            self.highDist[2] = distance
                    else:
                        if theta == LEFT[0] or theta == LEFT[1]:
                            self.lowDist[0] = distance
                        elif theta == CENTER:
                            self.lowDist[1] = distance
                        else:
                            self.lowDist[2] = distance
            self.count = self.count - 1

            
    def aim(self, theta, servo):
        'Aim the distance sensor to a specified position from 0 to 180, specify GPG.SERVO_1 for tilt, GPG.SERVO_2 for rotate'
        try:
            servo_position = int(theta)
        
            #Pulse width range in microsec corresponding to 0 to 180 degrees
            PULSE_WIDTH_RANGE=1850

            # Servo Position in degrees
            if servo_position > 180:
                servo_position = 180
            elif servo_position < 0:
                servo_position = 0

            pulsewidth = round( (1500-(PULSE_WIDTH_RANGE/2)) +
                            ((PULSE_WIDTH_RANGE /180) * servo_position))
            self._GPG.set_servo(servo, pulsewidth)
        except Exception as exc:
            print("Exception: {0}".format(exc))
