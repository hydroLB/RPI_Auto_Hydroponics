import logging
from pump_control import *
from water_management import *
from nutrient_management import *
from ph_management import *
from file_operations import *
from sensor_management import *
from logging_config import *


# Target pH values and limits
TARGET_PH, MIN_PH, MAX_PH = 5.8, 5.6, 6.2

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
# WAIT_TIME_BETWEEN_CHECKS = how long should the raspberry pi wait to check the water level and then if the ph is within soft range
WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 3, 1000

# Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced (which always raises it to some degree).
NUTRIENT_PPM_SAFETY_MARGIN = 30

PH_UP_SLEEP_TIME = 0.1  # Sleep time for pH up pump (how long is it on)
PH_DOWN_SLEEP_TIME = 0.1  # Sleep time for pH down pump (how long is it on)
LOOP_SLEEP_TIME = 10  # Sleep time for the loop ((how long to wait between each increment dosing)


def setup_hydroponic_system():
    """
    Set up the hydroponic system by priming pumps, filling water, dosing nutrients, and balancing pH.
    """
    # Check if the water level is below the threshold for system setup
    if get_water_level() < 2.0:

        # Log the system startup message
        logging.info("RPI Hydroponic System Startup\nTo start, pumps must be primed")

        # Reverse all pumps to ensure consistent starting state
        print("Reversing all pumps for 25 seconds")
        run_pumps_list(all_pumps, reverse=True)
        sleep(25)  # Wait for pumps to reset

        # Stop all pumps after reversing
        stop_pumps_list(all_pumps)

        # Prime all pumps to prepare for nutrient dosing
        prime(all_pumps)

        # Get user input for target PPM and water level
        target_ppm = int(input("\nInput starting target plant ppm value (it will adapt): "))
        target_water_level = int(input("Input target water level (in inches): "))

        # Save target PPM and water level to the file
        write_to_file(target_ppm, target_water_level)

        # Fill water to the target level in the reservoir
        fill_water(target_water_level)

        # Dose nutrients based on the target PPM
        dose_nutrients(target_ppm, nutrient_pump_time_list)

        # Balance pH levels to the desired range
        balance_PH_exact()

        # Log the completion of the system setup
        logging.info("Startup completed")

        # Wait for 30 seconds to allow PPM to settle
        sleep(30)

        # Update target PPM based on the plant's behavior
        target_ppm = get_ppm()
        write_to_file(target_ppm, target_water_level)
    else:
        # If the water level is above the threshold, log that the system is already set up
        logging.info("Hydroponic system already set up")


def monitor_hydroponic_system():
    """
    Continuously monitor the hydroponic system, adjusting water level, dosing nutrients, and balancing pH as needed.
    """
    while True:
        try:
            # Read the target PPM and water level values from the file
            target_ppm, target_water_level = read_from_file()

            # Check if the difference between the current water level and the target water level
            # is greater than the defined threshold
            if get_water_level() - target_water_level > WATER_THRESHOLD:
                # Adjust water level and nutrients if the difference is greater than the threshold
                adjust_water_level_and_nutrients()

            else:
                # If the difference is within the threshold, balance the pH levels
                balance_ph()  # Keep within range

            # Sleep for a defined time before checking water level and pH again
            sleep(WAIT_TIME_BETWEEN_CHECKS)

        except Exception as e:
            # Log any errors that occur during the monitoring process
            logging.error(f"An error occurred: {e}")

            # Sleep for a defined time before attempting to monitor the hydroponic system again
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    # Set up the hydroponic system
    setup_hydroponic_system()
    # Continuously monitor the hydroponic system
    monitor_hydroponic_system()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        stop_pumps_list(all_pumps)
