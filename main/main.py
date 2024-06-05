from time import sleep
import sys
import os

# Append the project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Atlas_and_pump_utilities.AtlasI2C import test_temp_sensor, test_ph_sensor, test_ec_sensor, get_ppm, get_ph
from Water_Level_Sensor.Water_Level_ETAPE import get_water_level
from Atlas_and_pump_utilities.pumps import run_pumps_list, stop_pumps_list, prime
from Water_Level_Sensor.adjust_water_level_and_nutrients import fill_water, dose_nutrients, adjust_water_level_and_nutrients
from Water_Level_Sensor.ETAPE_Calibration import initialize_water_sensor
from Water_level_nutrients_ph_manager.ph_manager import balance_PH_exact, balance_ph
from user_config.user_configurator import SKIP_SYSTEM_SETUP_WATER_LEVEL, configure_system, ECSensor, PHSensor, \
    ph_dosing_time, WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS
from file_operations.logging_water_lvl_and_target_ppm import read_from_file, write_to_file

# Global variables
global plant, ph_pump_list, all_pumps


def setup_hydroponic_system():
    """
    Sets up the hydroponic system, including configuring pumps, priming pumps,
    initializing sensors, and dosing nutrients, only if water level is below threshold to skip this step
    """
    global plant, ph_pump_list, all_pumps

    # Check the water level to determine if setup is needed
    if (get_water_level() is None) or (get_water_level() < SKIP_SYSTEM_SETUP_WATER_LEVEL):
        print("Welcome to RPI Auto Hydroponics, aka RAH, press enter to begin configuring the pumps")
        sys.stdin.readline()  # Wait for user to hit enter to start configuration

        # Configure the system and get the plant and pH pump list
        plant, ph_pump_list = configure_system()

        # Create a global list of all pumps
        all_pumps = [pump for pump, _ in plant.nutrient_pump_time_list] + ph_pump_list

        # Write initial target levels from user config file to settings.txt
        with open("settings.txt", "w") as file:
            file.write(f"{plant.target_ppm},{plant.target_water_level}")

        # Inform user about priming the pumps
        print("Pumps must now be primed for proper pH nutrient dosing...")

        # Clear pumps out
        print("Press enter to start reverse sequence...")
        sys.stdin.readline()  # Wait for user to hit enter to start reversing pumps
        print("Reversing all pumps for 25 seconds...")
        run_pumps_list(all_pumps, reverse=True)  # Run all pumps in reverse

        # Wait for 25 seconds while pumps are reversing
        for x in range(1, 26):
            sleep(1)
            print(26 - x, "seconds left")
        stop_pumps_list(all_pumps)  # Stop all pumps after reversing

        # Prime the pumps to fill them completely
        prime(all_pumps)

        # Initialize water sensor to get the water level
        initialize_water_sensor()

        # Fill the system with water
        fill_water()

        # Test temperature sensor
        test_temp_sensor()

        # Test pH and EC sensors
        test_ph_sensor(PHSensor)
        test_ec_sensor(ECSensor)

        # Get the target PPM and water level from settings file
        target_ppm, target_water_level = read_from_file()

        # Dose nutrients based on the target PPM
        dose_nutrients(target_ppm, plant.nutrient_pump_time_list)

        # Balance the pH exactly
        balance_PH_exact(ph_dosing_time, plant, ph_pump_list)

        # Write the current PPM and water level to the settings file
        write_to_file(get_ppm(), get_water_level())

        print("Startup completed")  # Log that startup is complete
    else:
        print("Hydroponic system already set up")  # Log if the system is already set up


def monitor_hydroponic_system():
    """
    Continuously monitors the hydroponic system, including water level, PPM level, and pH level.
    Adjusts water level and nutrients or balances pH as needed based on target values.
    """
    global plant, ph_pump_list, all_pumps

    while True:
        try:
            # Print the current water level
            print("Current Water level:", get_water_level())

            # Print the current PPM level
            print("Current PPM level:", get_ppm())

            # Print the current pH level
            print("Current PH level:", get_ph())

            # Read target PPM and water level from the settings file
            target_ppm, target_water_level = read_from_file()

            # Check if the water level is below the target threshold
            if target_water_level - get_water_level() > WATER_THRESHOLD:
                # Adjust water level and nutrients if below threshold
                adjust_water_level_and_nutrients(plant, ph_pump_list)
            else:
                # Balance the pH if water level is within the acceptable range
                balance_ph(ph_dosing_time, plant, ph_pump_list)

            # Wait for a specified time before the next check
            sleep(WAIT_TIME_BETWEEN_CHECKS)

        except Exception as ex:
            # Log any errors that occur and wait before the next check
            print(f"An error occurred: {ex}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    """
    Main function to set up and monitor the hydroponic system.
    """
    global plant, ph_pump_list, all_pumps

    # Initial setup of the hydroponic system
    setup_hydroponic_system()

    if plant is None:
        # If the plant is not configured, configure the system
        plant, ph_pump_list = configure_system()

        # Create a global list of all pumps
        all_pumps = [pump for pump, _ in plant.nutrient_pump_time_list] + ph_pump_list
    else:
        # If the plant is already configured, start monitoring the system
        monitor_hydroponic_system()


if __name__ == "__main__":
    """
        Entry point for the script. This block ensures that the script runs
        the main function when executed directly.
    """
    try:
        main()
    except Exception as e:
        print(f"An error occurred in the main function: {e}")
