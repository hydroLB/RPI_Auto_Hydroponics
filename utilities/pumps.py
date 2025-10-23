# Import components from the main module: motor drivers and nutrient pump times.
import sys


# Import the MotorKit class from the Adafruit Motor HAT library.
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


# Prime pumps with the user's help
def prime(pumps_list):
    for pump in pumps_list:
        counter = 1
        print("Press enter to start priming pump" + str(
            counter) + ", then press enter to stop when liquid level reaches the end of the pumps tubing")
        counter += 1
        sys.stdin.readline()  # Wait for user to hit enter
        pump.start()
        sys.stdin.readline()  # Wait for user to hit enter
        pump.stop()
    print("All pumps primed")


# This is needed to get all the pumps to the same point and ensure any liquid left
# over in the tubes is removed, priming it
def run_pumps_list(pumps_list, reverse=False):
    """
    Start all pumps in the given list in forward or reverse mode.
    Args:
        pumps_list: List of pump objects to be run.
        reverse: Boolean indicating whether pumps should run in reverse mode (default: False).
    """
    for pump in pumps_list:
        if reverse:
            pump.startReverse()
        else:
            pump.start()


def stop_pumps_list(pumps_list):
    """Stop all pumps in the given list."""
    for pump in pumps_list:
        pump.stop(pump)
