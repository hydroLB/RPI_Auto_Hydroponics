# Import components from the main module: motor drivers and nutrient pump times.
from main import driver0, driver1, nutrient_pump_times
import sys

# Instantiate the fresh water pump object.
fresh_water_pump = waterPump

# Create a list of tuples with nutrient pump objects and corresponding pump times.
nutrient_pump_time_list = [(nutrientPump1, nutrient_pump_times[0]), (nutrientPump2, nutrient_pump_times[1]),
                           (nutrientPump3, nutrient_pump_times[2]), (nutrientPump4, nutrient_pump_times[3])]

# List containing the pH Up and pH Down pump objects.
ph_pump_list = [pHUpPump, pHDownPump]

# Global list of all pump objects: fresh water, nutrient, and pH pumps.
all_pumps = [fresh_water_pump] + [pump for pump, _ in nutrient_pump_time_list] + ph_pump_list


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

