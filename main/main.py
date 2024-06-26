import sys
from time import sleep
from file_operations.log_sensor_data import log_sensor_data
from Atlas_and_pump_utilities.AtlasI2C import test_temp_sensor, test_ph_sensor, test_ec_sensor, get_ppm, get_ph, \
    test_fresh_water_pump
from Water_Level_Sensor.Water_Level_ETAPE import get_water_level
from Atlas_and_pump_utilities.pumps import stop_pumps_list
from Water_Level_Sensor.adjust_water_level_and_nutrients import fill_water, dose_nutrients, \
    adjust_water_level_and_nutrients
from Water_Level_Sensor.ETAPE_Calibration import initialize_water_sensor
from Water_level_nutrients_ph_manager.ph_manager import balance_PH_exact, balance_ph
from user_config.user_configurator import SKIP_SYSTEM_SETUP_WATER_LEVEL, configure_system, \
    ph_dosing_time, WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS, FRESH_WATER_PUMP_PIN
from file_operations.logging_water_and_ppm import read_from_file, write_to_file


def setup_hydroponic_system():
    """
    Sets up the hydroponic system, including configuring pumps, priming pumps,
    initializing sensors, and dosing nutrients, only if water level is below threshold to skip this step.
    """

    try:
        # Check the water level to determine if setup is needed
        water_level = get_water_level()
        if water_level is None or water_level < SKIP_SYSTEM_SETUP_WATER_LEVEL:
            print("Welcome to RPI Auto Hydroponics, aka RAH, press enter to begin configuring the pumps")
            sys.stdin.readline()  # Wait for user to hit enter to start configuration

            # Configure the system and get the plant and pH pump list
            plant, ph_pump_list = configure_system()

            # Write initial target levels from user config file to settings.txt
            write_to_file(plant.target_ppm, plant.target_water_level)

            # test the pump control over bringing in fresh water during a refill
            test_fresh_water_pump()

            # Initialize water sensor to get the water level
            initialize_water_sensor()

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
        else:
            # water is above the skip_system water level
            print("Hydroponic system already set up, moving to monitoring")

    except (TypeError, ValueError, KeyError) as ex:
        raise Exception(f"Specific error occurred in setup_hydroponic_system: {ex}")

    except IOError as ex:
        raise Exception(f"I/O error occurred in setup_hydroponic_system: {ex}")

    except Exception as ex:
        raise Exception(f"An unexpected error occurred in setup_hydroponic_system: {ex}")


def monitor_hydroponic_system():
    """
    Continuously monitors the hydroponic system, including water level, PPM level, and pH level.
    Adjusts water level and nutrients or balances pH as needed based on target values.
    """
    # Configure the system and get the plant and pH pump list
    plant, ph_pump_list = configure_system()

    while True:
        try:
            # Print the current water level
            water_level = get_water_level()
            print("Current Water level:", water_level)

            # Print the current PPM level
            ppm_level = get_ppm()
            print("Current PPM level:", ppm_level)

            # Print the current pH level
            ph_level = get_ph()
            print("Current PH level:", ph_level)

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
    """
        Entry point for the script. This block ensures that the script runs
        the main function when executed directly.
    """
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
