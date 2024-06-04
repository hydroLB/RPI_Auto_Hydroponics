from time import sleep
import sys
import os

# Append the project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Atlas_and_pump_utilities.AtlasI2C import get_ppm
from Water_Level_Sensor.WaterSensor import *
from Atlas_and_pump_utilities.pumps import *
from Water_Level_Sensor.water_management import fill_water, dose_nutrients
from Water_Level_Sensor.watersensor_calibration import initialize_water_sensor
from Water_level_nutrients_ph_manager.ph_management import balance_PH_exact, balance_ph
from user_config.user_config import *
from file_operations.logging_config import *


ph_pump_list = [pHUpPump, pHDownPump]

# Global list of all pumps
all_pumps = [pump for pump, _ in plant.nutrient_pump_time_list] + ph_pump_list


def setup_hydroponic_system():
    if (get_water_level() is None) or (get_water_level() < SKIP_SYSTEM_SETUP_WATER_LEVEL):
        # write the starting user_config target_ppm and target_water_level to file
        with open("settings.txt", "w") as file:
            file.write(f"{plant.target_ppm},{plant.target_water_level}")
        print("RPI Hydroponic System Startup\nTo start, pumps must be primed")
        # clear pumps out
        print("Reversing all pumps for 25 seconds")
        run_pumps_list(all_pumps, reverse=True)
        sleep(25)
        stop_pumps_list(all_pumps)
        prime(all_pumps)
        # get values from water sensor to get level
        initialize_water_sensor()
        # fill it up with water
        fill_water()
        # get the ppm and water level
        target_ppm, target_water_level = read_from_file()
        dose_nutrients(target_ppm, plant.nutrient_pump_time_list)
        balance_PH_exact(ph_dosing_time)
        # keep it precise (things won't be exact when first dose is completed)
        write_to_file(get_ppm(), get_water_level())

        logging.info("Startup completed")
    else:
        logging.info("Hydroponic system already set up")


def monitor_hydroponic_system():
    while True:
        try:
            # Read target PPM and water level from file
            target_ppm, target_water_level = read_from_file()
            if target_water_level - get_water_level() > WATER_THRESHOLD:
                adjust_water_level_and_nutrients()
            else:
                balance_ph(ph_dosing_time)
            sleep(WAIT_TIME_BETWEEN_CHECKS)
        except Exception as ex:
            logging.error(f"An error occurred: {ex}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    setup_hydroponic_system()
    monitor_hydroponic_system()


# a new fillup is occurring

def adjust_water_level_and_nutrients():
    # Read target PPM and water level from file
    target_ppm, target_water_level = read_from_file()

    pre_fillup_ppm = get_ppm()
    fill_water()
    sleep(30)  # Wait for PPM readings to settle

    # Update target PPM based on plant's nutrient consumption rate
    target_ppm += (target_ppm - pre_fillup_ppm)
    write_to_file(target_ppm, get_water_level())

    # Read target PPM and water level from file AGAIN as we updated it
    target_ppm, target_water_level = read_from_file()

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(target_ppm - PH_PPM_SAFETY_MARGIN, plant.nutrient_pump_time_list)
    balance_PH_exact(ph_dosing_time)
    # one last check
    dose_nutrients(target_ppm, plant.nutrient_pump_time_list)
    # update new target ppm based on plant response and water level
    write_to_file(target_ppm, get_water_level())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
