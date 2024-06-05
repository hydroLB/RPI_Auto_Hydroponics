from time import sleep
import sys
import os

# Append the project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Atlas_and_pump_utilities.AtlasI2C import get_ppm
from Water_Level_Sensor.WaterSensor import *
from Atlas_and_pump_utilities.pumps import *
from Water_Level_Sensor.water_management import fill_water, dose_nutrients, adjust_water_level_and_nutrients
from Water_Level_Sensor.watersensor_calibration import initialize_water_sensor
from Water_level_nutrients_ph_manager.ph_management import balance_PH_exact, balance_ph
from user_config.user_config import *
from file_operations.logging_config import *

# Global variables
global plant, ph_pump_list, all_pumps


def setup_hydroponic_system():
    global plant, ph_pump_list, all_pumps
    if (get_water_level() is None) or (get_water_level() < SKIP_SYSTEM_SETUP_WATER_LEVEL):
        print("Welcome to Hydroponics Heaven, press enter to begin configuring the pumps")
        sys.stdin.readline()  # Wait for user to hit enter
        plant, ph_pump_list = configure_system()
        # Global list of all pumps
        all_pumps = [pump for pump, _ in plant.nutrient_pump_time_list] + ph_pump_list

        # Write initial target levels from user config file, these will be modified as the system progresses
        with open("settings.txt", "w") as file:
            file.write(f"{plant.target_ppm},{plant.target_water_level}")

        # INITIALIZE PUMPS TO STARTING POSITION (NO LIQUIDS LEFT IN TUBES)
        # write the starting user_config target_ppm and target_water_level to file
        print("Next, pumps must be primed...")
        # clear pumps out
        print("Press enter to start reverse sequence")
        sys.stdin.readline()  # Wait for user to hit enter
        print("Reversing all pumps for 25 seconds")
        run_pumps_list(all_pumps, reverse=True)
        sleep(25)
        stop_pumps_list(all_pumps)

        # INITIALIZE PUMPS TO FILLED POSITION (TUBES ARE COMPLETELY FILLED,
        # ENSURES PROPER DOSING (NO LAG TIME BETWEEN THE NUTRIENTS))
        prime(all_pumps)

        # get values from water sensor to get level
        initialize_water_sensor()
        # fill it up with water
        fill_water()
        # get the ppm and water level
        target_ppm, target_water_level = read_from_file()
        dose_nutrients(target_ppm, plant.nutrient_pump_time_list)
        balance_PH_exact(ph_dosing_time, plant, ph_pump_list)
        # keep it precise (things won't be exact when first dose is completed)
        write_to_file(get_ppm(), get_water_level())

        logging.info("Startup completed")
    else:
        logging.info("Hydroponic system already set up")


def monitor_hydroponic_system():
    global plant, ph_pump_list, all_pumps
    while True:
        try:
            # Read target PPM and water level from file
            target_ppm, target_water_level = read_from_file()
            if target_water_level - get_water_level() > WATER_THRESHOLD:
                adjust_water_level_and_nutrients(plant, ph_pump_list)
            else:
                balance_ph(ph_dosing_time, plant, ph_pump_list)
            sleep(WAIT_TIME_BETWEEN_CHECKS)
        except Exception as ex:
            logging.error(f"An error occurred: {ex}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    global plant, ph_pump_list, all_pumps
    setup_hydroponic_system()
    monitor_hydroponic_system()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
