from adafruit_motorkit import MotorKit


class Pump:
    def __init__(self, motor, direction):
        """
        Initialize a new Pump object.

        Args:
            motor: Motor object from the MotorKit.
            direction: Integer representing the motor direction (1 or -1).
        """
        self.motor = motor
        self.direction = direction

    def start(self):
        """Start the pump by setting the motor throttle to its direction."""
        self.motor.throttle = self.direction

    def stop(self):
        """Stop the pump by setting the motor throttle to zero."""
        self.motor.throttle = 0

    def startReverse(self):
        """Start the pump in reverse by setting the motor throttle to the opposite of its direction."""
        self.motor.throttle = -self.direction



