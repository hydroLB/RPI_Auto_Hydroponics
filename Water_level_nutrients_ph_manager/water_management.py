from Water_level_nutrients_ph_manager.read_water_sensor import get_water_level
from main import *
from time import sleep
from utilities.AtlasI2C import get_ppm


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
            fresh_waterPump.start()
            # Wait for 5 seconds to allow the water pump to operate
            sleep(5)
        # Stop the water pump once the target water level is reached
        fresh_waterPump.stop()
    except Exception as ee:
        # Log the error message and stop the water pump in case of an exception
        logging.error(f"An error occurred while filling water: {ee}")
        fresh_waterPump.stop()


def dose_nutrients(target_ppm_local, pump_info, NUTRIENT_WAIT_TIME_LOOP):
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
        sleep(NUTRIENT_WAIT_TIME_LOOP)


def adjust_water_level_and_nutrients(FILENAME, NUTRIENT_PPM_SAFETY_MARGIN, NUTRIENT_PUMP_TIME_LIST,
                                     NUTRIENT_WAIT_TIME_LOOP, target_min_max_ph, ph_dosing_time):
    # Read target PPM and water level from file
    target_ppm, target_water_level, _, _ = read_from_file(FILENAME)

    # Measure PPM before adjusting water level
    pre_fillup_ppm = get_ppm()

    # Fill water to the target level
    fill_water(target_water_level)
    sleep(30)  # Wait for PPM readings to settle

    # Call proprietary algorithm for updating target PPM
    target_ppm = proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm)

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(target_ppm - NUTRIENT_PPM_SAFETY_MARGIN, NUTRIENT_PUMP_TIME_LIST, NUTRIENT_WAIT_TIME_LOOP)
    balance_PH_exact(target_min_max_ph, ph_dosing_time)
    dose_nutrients(target_ppm, NUTRIENT_PUMP_TIME_LIST, NUTRIENT_WAIT_TIME_LOOP)

    # Write the new water level and new ppm to the file
    write_to_file(FILENAME, target_ppm, target_water_level, get_ppm(), get_water_level(a, b, c))


def proprietary_ppm_update_algorithm(target_ppm, pre_fillup_ppm):
    # This function contains the proprietary algorithm for updating the target PPM
    # based on the plant's nutrient consumption rate. The implementation details are
    # protected by copyright and licensed under AGPLv3. Using this without proper
    # attribution is illegal. 

    updated_ppm = target_ppm + (target_ppm - pre_fillup_ppm)
    return updated_ppm
