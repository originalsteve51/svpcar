# svpcar
Code that I wrote to run my GoPiGo3 car.

After attaching to the car with an ssh terminal, you can run the program using the command **python3 keydriver-mt.py**

Several driving commands are provided that you can use to drive the car manually. 

You can also tell the car to drive itself by issuing the **rove** command. When it roves, it moves forward, scanning the
terrain in front of it looking for obstructions. See more about scanning below. When an obstruction is encountered, it
looks to the left and right of the obstruction to determine how it can best avoid it. It backs up a short distance and then turns in the preferred direction and proceeds forward.

While roving, you can still issue manual commands to alter the course of the vehicle. For example, if you issue a **right 30** command, the vehicle will turn 30 degrees to the right and continue to rove as described earlier.

Scanning: I modified the basic GoPiGo3 by mounting the distance sensor to a gimbal that is turned and rotated using two servo motors. When the car is roving, the gimbal scans to six positions. This allows the distance sensor to 'see' what lies ahead at the six positions. The scan pattern is low left, low right, straight ahead right, straight ahead left, high left, high right. This scan runs continuously as the vehicle roves.




