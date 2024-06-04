import logging
from time import sleep
from Atlas_and_pump_utilities.AtlasI2C import get_ppm
from Atlas_and_pump_utilities.pumps import end_fresh_water_pump, start_fresh_water_pump
from Water_Level_Sensor.WaterSensor import get_water_level
from Water_level_nutrients_ph_manager.ph_management import balance_PH_exact
from file_operations.logging_config import write_to_file, read_from_file
from user_config.user_config import *


def fill_water():
    """
    Fill the water reservoir until the target water level is reached.

    param target_level: The desired water level to be reached in the reservoir.
    """
    try:
        # Read target PPM and water level from file
        target_ppm, target_water_level = read_from_file()
        # Continuously check the current water level in the reservoir
        while get_water_level < target_water_level:
            # Display the current water level while adding water
            print("Adding water... level %f" % get_water_level)
            # Start the water pump to fill the reservoir
            start_fresh_water_pump(FRESH_WATER_PUMP_PIN)
            # Wait for 5 seconds to allow the water pump to operate
            sleep(4)
        # Stop the water pump once the target water level is reached
        end_fresh_water_pump(FRESH_WATER_PUMP_PIN)
    except Exception as ee:
        # Log the error message and stop the water pump in case of an exception
        logging.error(f"An error occurred while filling water: {ee}")
        end_fresh_water_pump(FRESH_WATER_PUMP_PIN)


def dose_nutrients(target_ppm_local, pump_info):
    # Keep dosing nutrients until the target PPM is reached
    while get_ppm() < target_ppm_local:
        # Iterate through each pump and its corresponding dosing time in the pump_info list
        for pump, dosing_time in pump_info:
            # Print the current PPM
            print("Adding nutrients... PPM %f" % (get_ppm()))

            # Start the pump
            pump.start()

            # Sleep for the specified dosing time
            sleep(dosing_time)

            # Stop the pump
            pump.stop()

        # Sleep for 10 seconds before checking the PPM again
        sleep(10)


def adjust_water_level_and_nutrients():
    # Read target PPM and water level from file
    target_ppm, target_water_level = read_from_file()

    # Measure PPM before adjusting water level
    pre_fillup_ppm = get_ppm()

    # Call proprietary algorithm for updating target PPM
    target_ppm = proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm)

    # Fill water to the target level
    fill_water()
    sleep(15)  # Wait for PPM readings to settle

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(target_ppm - PH_PPM_SAFETY_MARGIN, plant.nutrient_pump_time_list)

    balance_PH_exact(ph_dosing_time)

    dose_nutrients(target_ppm, plant.nutrient_pump_time_list)

    # Write the new water level and new ppm to the file
    write_to_file(target_ppm, target_water_level)


def proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm):
    # This function contains the proprietary algorithm for updating the target PPM
    # based on the plant's nutrient consumption rate.
    
    # the new feed amount will be found by finding the difference (the drift) from the target ppm set 
    # before and what it is now before the fillup, what did the plant do? 
    # If the plant was hungry -> ppm would have dropped as it ate more and there is less food (ppm) in the water
    # If the plant was full -> ppm would have rose as it ate less and there is more food (ppm) in the water
    # For example if the "targetppm" was 100, and a fillup is triggered and the ppm is seen to be 120,
    # It will be calculated as 100-120= -20, meaning the target_ppm should be lowered by that amount
    updated_ppm = target_ppm + (target_ppm - pre_fillup_ppm)
    # updated_ppm = target_ppm*2 - pre_fillup_ppm
    return updated_ppm
