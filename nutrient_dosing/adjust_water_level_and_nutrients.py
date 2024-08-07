from time import sleep
from ph_ppm_pump_sensor.AtlasI2C import get_ppm
from ph_ppm_pump_sensor.pumps import end_fresh_water_pump, start_fresh_water_pump
from water_level_sensor.ETAPE_Calibration import time_to_reach
from water_level_sensor.Water_Level_ETAPE import get_water_level
from ph_manager.ph_manager import balance_PH_exact
from file_operations.logging_water_and_ppm import write_to_file, read_from_file
from user_config.user_configurator import PH_PPM_SAFETY_MARGIN, ph_dosing_time, Plant, FRESH_WATER_PUMP_PIN, \
    PPM_LOOP_SLEEP_TIME, fresh_water_pump_time_on, fresh_water_pump_time_off
from website.app import log_message


def fresh_water_pump_cycle_on_off(fresh_water_pin):
    start_fresh_water_pump(fresh_water_pin)
    sleep(fresh_water_pump_time_on)
    end_fresh_water_pump(fresh_water_pin)
    sleep(fresh_water_pump_time_off)


def fill_water(fresh_water_pin):
    """
    Fill the water reservoir until the target water level is reached.

    param target_level: The desired water level to be reached in the reservoir.
    """
    try:
        # Read target PPM and water level from file
        target_ppm, target_water_level = read_from_file()
        # Continuously check the current water level in the reservoir
        if get_water_level() < target_water_level:
            log_message("Water level filling beginning...")
        while get_water_level() < target_water_level:
            # Display the current water level while adding water
            print("Filling...  current level: %f" % get_water_level() + ",target level: %f" % target_water_level)

            # use the time we kind of know it takes to reach from one to another for faster fillup
            time = time_to_reach(get_water_level, target_water_level) * .92
            start_fresh_water_pump(fresh_water_pin)
            sleep(time)
            end_fresh_water_pump(fresh_water_pin)

            fresh_water_pump_cycle_on_off(fresh_water_pin)

        log_message("Water level filling completed successfully...")
    except Exception as ee:
        print("Error", ee)
        # Log the error message and stop the water pump in case of an exception
        end_fresh_water_pump(fresh_water_pin)


def dose_nutrients(target_ppm_local, pump_info):
    """
    Doses nutrients until the target PPM is reached.

    Args:
        target_ppm_local (float): The target PPM value.
        pump_info (list): A list of tuples containing pump objects and their corresponding dosing times.
    """
    try:
        # Check target_ppm_local type
        if not isinstance(target_ppm_local, (int, float)):
            raise TypeError(
                "Expected target_ppm_local to be an int or float, but got type {}. Error in dose_nutrients.".format(
                    type(target_ppm_local).__name__))

        # Check pump_info type
        if not isinstance(pump_info, list):
            raise TypeError("Expected pump_info to be a list, but got type {}. Error in dose_nutrients.".format(
                type(pump_info).__name__))

        # Ensure pump_info has more than one item
        if len(pump_info) <= 1:
            raise ValueError("pump_info must contain more than one pump. Error in dose_nutrients.")

        # Check each item in pump_info
        for item in pump_info:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("Each item in pump_info should be a tuple of length 2. Error in dose_nutrients.")

            pump, dosing_time = item

            if not hasattr(pump, 'start') or not hasattr(pump, 'stop'):
                raise AttributeError("Pump object missing 'start' or 'stop' method. Error in dose_nutrients.")

            if not isinstance(dosing_time, (int, float)):
                raise TypeError(
                    "Expected dosing_time to be an int or float, but got type {}. Error in dose_nutrients.".format(
                        type(dosing_time).__name__))

        current_ppm = get_ppm()
        if current_ppm < target_ppm_local:
            log_message("Nutrient Dosing Sequence Starting...")

        while current_ppm < target_ppm_local or current_ppm < target_ppm_local - (target_ppm_local * .025):
            # Iterate through each pump and its corresponding dosing time in the pump_info list
            for pump, dosing_time in pump_info:
                # Print the current PPM

                # Start the pump
                pump.start()

                # Sleep for the specified dosing time
                sleep(dosing_time)

                # Stop the pump
                pump.stop()

            current_ppm = get_ppm()

            # Sleep for PPM_LOOP_SLEEP_TIME before checking the PPM again
            sleep(PPM_LOOP_SLEEP_TIME)
            print("Current ppm %f" % current_ppm + "target ppm %f" % target_ppm_local)

        log_message("Nutrient Dosing Sequence Completed successfully...")

    except TypeError as e:
        raise TypeError("Type error occurred in dose_nutrients: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in dose_nutrients: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in dose_nutrients: {}".format(e))


def adjust_water_level_and_nutrients(plant, ph_pump_list):
    """
    Adjusts the water level and nutrients in the hydroponic system.

    Args:
        plant (Plant): A Plant object containing nutrient pump time list.
        ph_pump_list (list): A list of pH pump objects.
    """
    try:
        if not isinstance(plant, Plant):
            raise TypeError(
                "Expected plant to be a Plant object, but got type {}. "
                "Error in adjust_water_level_and_nutrients.".format(
                    type(plant).__name__))
        if not isinstance(ph_pump_list, list):
            raise TypeError(
                "Expected ph_pump_list to be a list, but got type {}. "
                "Error in adjust_water_level_and_nutrients.".format(
                    type(ph_pump_list).__name__))

        # Read target PPM and water level from file
        target_ppm, target_water_level = read_from_file()

        if not isinstance(target_ppm, (int, float)):
            raise TypeError("Expected target_ppm to be an int or float, but got type {}. "
                            "Error in adjust_water_level_and_nutrients.".format(type(target_ppm).__name__))
        if not isinstance(target_water_level, (int, float)):
            raise TypeError("Expected target_water_level to be an int or float, but got type {}. "
                            "Error in adjust_water_level_and_nutrients.".format(type(target_water_level).__name__))

        # Measure PPM before adjusting water level
        pre_fill_up_ppm = get_ppm()

        # Call proprietary algorithm for updating target PPM
        new_target_ppm = proprietary_ppm_update_algorithm(target_ppm, pre_fill_up_ppm)

        # Fill water to the target level
        fill_water(FRESH_WATER_PUMP_PIN)

        # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
        # then finally ensure it's exactly at the target PPM
        dose_nutrients(new_target_ppm - PH_PPM_SAFETY_MARGIN, plant.nutrient_pump_time_list)

        balance_PH_exact(ph_dosing_time, plant, ph_pump_list)

        dose_nutrients(new_target_ppm, plant.nutrient_pump_time_list)

        # Write the new water level and new ppm to the file
        write_to_file(new_target_ppm, target_water_level)

    except TypeError as e:
        raise TypeError("Type error occurred in adjust_water_level_and_nutrients: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in adjust_water_level_and_nutrients: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in adjust_water_level_and_nutrients: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in adjust_water_level_and_nutrients: {}".format(e))


def proprietary_ppm_update_algorithm(target_ppm, pre_fill_up_ppm):
    """
    Updates the target PPM based on the plant's nutrient consumption rate.

    Args:
        target_ppm (float): The initial target PPM value.
        pre_fill_up_ppm (float): The PPM value measured before the fill_up.

    Returns:
        float: The updated target PPM.
    """
    # This function contains the proprietary algorithm for updating the target PPM
    # based on the plant's nutrient consumption rate.

    # the new feed amount will be found by finding the difference (the drift) from the target ppm set
    # before and what it is now before the fill_up, what did the plant do?
    # If the plant was hungry -> ppm would have dropped as it ate more and there is less food (ppm) in the water
    # If the plant was full -> ppm would have rose as it ate less and there is more food (ppm) in the water
    # For example if the "target_ppm" was 100, and a fill_up is triggered and the ppm is seen to be 120,
    # It will be calculated as 100-120= -20, meaning the target_ppm should be lowered by that amount
    try:
        if not isinstance(target_ppm, (int, float)):
            raise TypeError("Expected target_ppm to be an int or float, but got type {}. "
                            "Error in proprietary_ppm_update_algorithm.".format(type(target_ppm).__name__))
        if not isinstance(pre_fill_up_ppm, (int, float)):
            raise TypeError("Expected pre_fill_up_ppm to be an int or float, but got type {}. "
                            "Error in proprietary_ppm_update_algorithm.".format(type(pre_fill_up_ppm).__name__))

        # Calculate the updated PPM based on the plant's nutrient consumption rate
        updated_ppm = target_ppm + (target_ppm - pre_fill_up_ppm)
        return updated_ppm

    except TypeError as e:
        raise TypeError("Type error occurred in proprietary_ppm_update_algorithm: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in proprietary_ppm_update_algorithm: {}".format(e))
