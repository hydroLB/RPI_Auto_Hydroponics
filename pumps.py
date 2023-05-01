from main import driver0, driver1


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


# Initialize pump objects with corresponding motor and direction

# direction value of each (-1 or 1) is due to the direction of the peristaltic pump, in our case we had some pumps that
# were moving in the opposite direction of what we expected

# position of each pump (driver0/driver1) dependent on how its setup physically
waterPump = Pump(driver0.motor4, -1)
nutrientPump1 = Pump(driver0.motor3, 1)
nutrientPump2 = Pump(driver1.motor3, 1)
nutrientPump3 = Pump(driver1.motor2, 1)
nutrientPump4 = Pump(driver1.motor1, -1)
pHDownPump = Pump(driver1.motor4, -1)
pHUpPump = Pump(driver0.motor1, 1)
