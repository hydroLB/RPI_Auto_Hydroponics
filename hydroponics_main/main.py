import os
import sys
import threading
from time import sleep
# Add the project directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from file_operations.log_sensor_data import log_sensor_data
from ph_ppm_pump_sensor.AtlasI2C import test_temp_sensor, test_ph_sensor, test_ec_sensor, get_ppm, get_ph, \
    test_fresh_water_pump, get_temp_f
from water_level_sensor.Water_Level_ETAPE import get_water_level
from ph_ppm_pump_sensor.pumps import stop_pumps_list
from nutrient_dosing.adjust_water_level_and_nutrients import fill_water, dose_nutrients, \
    adjust_water_level_and_nutrients
from water_level_sensor.ETAPE_Calibration import initialize_water_sensor
from ph_manager.ph_manager import balance_PH_exact, balance_ph
from user_config.user_configurator import SKIP_SYSTEM_SETUP_WATER_LEVEL, configure_system, \
    ph_dosing_time, WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS, FRESH_WATER_PUMP_PIN
from file_operations.logging_water_and_ppm import read_from_file, write_to_file
from website.app import temperature_value_lock, ppm_value_lock, water_level_lock, ph_value_lock, log_message

previous_ph_value = 7.0
previous_ppm_value = 0.0
previous_temperature_value = 70.0
previous_water_level = 0.0


# noinspection PyCompatibility
def setup_hydroponic_system():
    """
    Sets up the hydroponic system, including configuring pumps, priming pumps,
    initializing sensors, and dosing nutrients, only if water level is below threshold to skip this step.
    """

    try:
        # Check the water level to determine if setup is needed
        water_level = get_water_level()
        if water_level is None or water_level < SKIP_SYSTEM_SETUP_WATER_LEVEL:
            sys.stdin.readline()  # Wait for user to hit enter to start configuration

            # Configure the system and get the plant and pH pump list
            plant, ph_pump_list = configure_system()

            # Write initial target levels from user config file to settings.txt
            write_to_file(plant.target_ppm, plant.target_water_level)

            # test the pump control over bringing in fresh water during a refill
            test_fresh_water_pump()

            # Initialize water sensor to get the water level
            initialize_water_sensor()
            log_message("Water sensor initialization begun")

            # Fill the system with water
            fill_water(FRESH_WATER_PUMP_PIN)

            # Test temperature sensor
            test_temp_sensor()

            # Test pH and EC sensors
            test_ph_sensor()
            test_ec_sensor()

            # Get the target PPM and water level from settings file
            target_ppm, target_water_level = read_from_file()

            # Dose nutrients based on the target PPM
            dose_nutrients(target_ppm, plant.nutrient_pump_time_list)

            # Balance the pH exactly
            balance_PH_exact(ph_dosing_time, plant, ph_pump_list)

            # Write the current PPM and water level to the settings file
            write_to_file(get_ppm(), get_water_level())

            print("Startup completed")  # Log that startup is complete
            log_message("Startup sequence completed, moving to monitoring!")

        else:
            # water is above the skip_system water level
            print("Hydroponic system already set up, moving to monitoring")

    except (TypeError, ValueError, KeyError) as ex:
        raise Exception(f"Specific error occurred in setup_hydroponic_system: {ex}")

    except IOError as ex:
        raise Exception(f"I/O error occurred in setup_hydroponic_system: {ex}")

    except Exception as ex:
        raise Exception(f"An unexpected error occurred in setup_hydroponic_system: {ex}")


def write_value_to_file(file_path, value):
    """Write a float value to a file."""
    with open(file_path, 'w') as file:
        file.write(str(value))


# Define file paths for shared data
ph_value_file = 'website_vals/ph_value.txt'
water_level_file = 'website_vals/water_level.txt'
ppm_value_file = 'website_vals/ppm_value.txt'
temperature_value_file = 'website_vals/temperature_value.txt'


def write_to_website_file(file_path, value):
    with open(file_path, 'w') as f:
        f.write(str(value))


def common_sense_checks(new_ph_value, new_ppm_value, new_temperature_value, new_water_level):
    global previous_ph_value, previous_ppm_value, previous_temperature_value, previous_water_level

    if not (3 <= new_ph_value <= 11):
        log_message("CSC: pH out of range (3-11).")
    if abs(new_ph_value - previous_ph_value) > 2:
        log_message("CSC: pH changed more than 2 values in one hour.")

    if not (50 <= new_ppm_value <= 1800):  # Adjust the PPM range based on your system's requirements
        log_message("CSC: PPM out of range (50-1800).")
    if abs(new_ppm_value - previous_ppm_value) > 300:  # Example threshold for significant PPM change
        log_message("CSC: PPM changed more than 300 in one hour.")

    if not (50 <= new_temperature_value <= 85):  # Example temperature range in Fahrenheit
        log_message("CSC: Temperature out of range (50-85 F).")
    if abs(new_temperature_value - previous_temperature_value) > 15:  # Example threshold for significant temperature
        # change
        log_message("CSC: Temperature changed more than 15 F in one hour.")

    if not (0.5 <= new_water_level <= 7):  # Example water level range in inches
        log_message("CSC: Water level out of range (0.5-7 in).")
    if abs(new_water_level - previous_water_level) > 1.5:  # Example threshold for significant water level change
        log_message("CSC: Water level changed more than 1.5 inches in one hour.")

    # Update previous values
    previous_ph_value = new_ph_value
    previous_ppm_value = new_ppm_value
    previous_temperature_value = new_temperature_value
    previous_water_level = new_water_level


def monitor_hydroponic_system():
    """
    Continuously monitors the hydroponic system, including water level, PPM level, and pH level.
    Adjusts water level and nutrients or balances pH as needed based on target values.
    """
    # Configure the system and get the plant and pH pump list
    plant, ph_pump_list = configure_system()

    while True:
        try:
            # Read new values from sensors
            new_ph_value = get_ph()
            new_water_level = get_water_level()
            new_ppm_value = get_ppm()
            new_temperature_value = get_temp_f()
            print(f"pH: {new_ph_value:.2f}, Water Level: {new_water_level:.2f} in, PPM: {new_ppm_value:.2f}, "
                  f"Temperature: {new_temperature_value:.2f} F")

            common_sense_checks(new_ph_value, new_ppm_value, new_temperature_value, new_water_level)

            # Update global variables with new sensor values
            with ph_value_lock:
                ph_value = new_ph_value
                write_to_website_file(ph_value_file, ph_value)

            with water_level_lock:
                water_level = new_water_level
                write_to_website_file(water_level_file, water_level)
            with ppm_value_lock:
                ppm_value = new_ppm_value
                write_to_website_file(ppm_value_file, ppm_value)

            with temperature_value_lock:
                temperature_value = new_temperature_value
                write_to_website_file(temperature_value_file, temperature_value)

            # Log the data from each hour into a file or so
            log_sensor_data()

            # Read target PPM and water level from the settings file
            target_ppm, target_water_level = read_from_file()

            # Check if the water level is below the target threshold
            if target_water_level - water_level > WATER_THRESHOLD:
                # Adjust water level and nutrients if below threshold
                adjust_water_level_and_nutrients(plant, ph_pump_list)
            else:
                # Balance the pH in a range if water level is within the acceptable range
                balance_ph(ph_dosing_time, plant, ph_pump_list)

            # Wait for a specified time before the next check
            sleep(WAIT_TIME_BETWEEN_CHECKS)

        except (TypeError, ValueError, KeyError) as ex:
            # Log any specific errors and wait before the next check
            print(f"A specific error occurred in monitor_hydroponic_system: {ex}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)

        except Exception as ex:
            # Log any unexpected errors that occur and wait before the next check
            print(f"An unexpected error occurred in monitor_hydroponic_system: {ex}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    """
    Main function to set up and monitor the hydroponic system.
    """
    try:
        # Initial setup of the hydroponic system
        setup_hydroponic_system()
        monitor_hydroponic_system()

    except TypeError as e2:
        raise TypeError("Type error occurred in main: {}".format(e2))

    except ValueError as e3:
        raise ValueError("Value error occurred in main: {}".format(e3))

    except KeyError as e4:
        raise KeyError("Key error occurred in main: {}".format(e4))

    except Exception as e5:
        raise Exception("An unexpected error occurred in main: {}".format(e5))


def ensure_pumps_off():
    try:
        # Configure the system and get the plant and pH pump list
        plant, ph_pump_list = configure_system()
        stop_pumps_list([pump for pump, _ in plant.nutrient_pump_time_list] + ph_pump_list)
    except Exception as g:
        print(f"An error occurred in ensure_pumps_off function in main: {g}")


if __name__ == "__main__":
    ph_value_lock = threading.Lock()
    water_level_lock = threading.Lock()
    ppm_value_lock = threading.Lock()
    temperature_value_lock = threading.Lock()

    monitor_thread = threading.Thread(target=monitor_hydroponic_system)
    monitor_thread.start()

    try:
        main()
        ensure_pumps_off()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        ensure_pumps_off()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred in the main function: {e}")
        ensure_pumps_off()
        sys.exit(0)
