from pumps import *

from pump_config import all_pumps  # Import the global pumps list from pump_config


def stop_pumps_list(pumps_list):
    """Stop all pumps in the given list."""
    for pump in pumps_list:
        pump.stop(pump)


# Stop all pumps
stop_pumps_list(all_pumps)
