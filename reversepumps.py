from pumps import *
from stopmotors import stop_pumps_list  # Import stop_all_pumps from stop_motors
from pump_config import all_pumps  # Import the global pumps list from pump_config


# This is needed to get all the pumps to the same point and ensure any liquid left
# over in the tubes is removed, priming it
def reverse_pumps_list(pumps_list):
    """
    Start all pumps in the given list in reverse mode.
    Args:
        pumps_list: List of pump objects to be reversed.
    """
    for pump in pumps_list:
        pump.startReverse()


# Reverse all pumps
reverse_pumps_list(all_pumps)

print("Press Enter to halt the liquid resetting process in the pumps")
input()

# Stop all pumps
stop_pumps_list(all_pumps)
