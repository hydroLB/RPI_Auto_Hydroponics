import logging

from WaterSensor import *
from time import sleep

from file_operations import read_from_file, write_to_file
from main import NUTRIENT_PPM_SAFETY_MARGIN, ph_dosing_time, target_min_max_ph, NUTRIENT_WAIT_TIME_LOOP, b, a, c, \
    filename
from nutrient_management import dose_nutrients
from ph_management import balance_PH_exact
from pump_config import nutrient_pump_time_list
from pumps import waterPump
from tempAtlas import get_ppm


def fill_water(target_level):
    """
    Fill the water reservoir until the target water level is reached.

    param target_level: The desired water level to be reached in the reservoir.
    """
    try:
        # Continuously check the current water level in the reservoir
        while get_water_level(a, b, c) < target_level:
            # Display the current water level while adding water
            print("Adding water... level %f" % (get_water_level(a, b, c)))
            # Start the water pump to fill the reservoir
            waterPump.start()
            # Wait for 5 seconds to allow the water pump to operate
            sleep(5)
        # Stop the water pump once the target water level is reached
        waterPump.stop()
    except Exception as ee:
        # Log the error message and stop the water pump in case of an exception
        logging.error(f"An error occurred while filling water: {ee}")
        waterPump.stop()


def adjust_water_level_and_nutrients():
    # Read target PPM and water level from file
    target_ppm, target_water_level = read_from_file(filename)

    # Measure PPM before adjusting water level
    pre_fillup_ppm = get_ppm()

    # Fill water to the target level
    fill_water(target_water_level)
    sleep(30)  # Wait for PPM readings to settle

    # Call proprietary algorithm for updating target PPM
    target_ppm = proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm)

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(target_ppm - NUTRIENT_PPM_SAFETY_MARGIN, nutrient_pump_time_list, NUTRIENT_WAIT_TIME_LOOP)
    balance_PH_exact(target_min_max_ph, ph_dosing_time)
    dose_nutrients(target_ppm, nutrient_pump_time_list, NUTRIENT_WAIT_TIME_LOOP)

    # Write the new water level and new ppm to the file
    write_to_file(filename, get_ppm(), get_water_level(a, b, c))


def proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm):
    # This function contains the proprietary algorithm for updating the target PPM
    # based on the plant's nutrient consumption rate. The implementation details are
    # protected by copyright and licensed under AGPLv3. Using this without proper
    # attribution is illegal. 

    updated_ppm = target_ppm + (target_ppm - pre_fillup_ppm)
    return updated_ppm
