from pumps import run_pumps_list, stop_pumps_list, prime
from water_management import *
from nutrient_management import *
from ph_management import *
from file_operations import *
from logging_config import *
from constants import *

# Use constants in code from constants.py

ECSensor = AtlasI2C(EC_SENSOR_I2C_ADDRESS)
PHSensor = AtlasI2C(PH_SENSOR_I2C_ADDRESS)
adc = Adafruit_ADS1x15.ADS1115(address=ADC_I2C_ADDRESS, busnum=ADC_BUSNUM)
GAIN = ADC_GAIN
a, b, c = QUADRATIC_COEFFICIENTS
driver0 = MotorKit(DRIVER0_I2C_ADDRESS)
driver1 = MotorKit(DRIVER1_I2C_ADDRESS)


def setup_hydroponic_system(NUTRIENT_PUMP_TIME_LIST, NUTRIENT_WAIT_TIME_LOOP, target_min_max_ph, ph_dosing_time):
    """
    Set up the hydroponic system by priming pumps, filling water, dosing nutrients, and balancing pH.
    """
    # Check if the water level is below the threshold for system setup
    if get_water_level(a, b, c) < SKIP_SYSTEM_SETUP_WATER_LEVEL:

        # Log the system startup message
        logging.info("RPI Hydroponic System Startup\nTo start, pumps must be primed")

        # Reverse all pumps to ensure consistent starting state
        logging.info("Reversing all pumps for 25 seconds")
        run_pumps_list(ALL_PUMPS, reverse=True)
        sleep(25)  # Wait for pumps to reset

        # Stop all pumps after reversing
        stop_pumps_list(ALL_PUMPS)

        # Prime all pumps to prepare for nutrient dosing
        prime(ALL_PUMPS)

        # Get user input for target PPM and water level
        target_ppm = int(input("\nInput starting target plant ppm value (it will adapt): "))
        target_water_level = int(input("Input target water level (in inches): "))

        # Save target PPM and water level to the file
        write_to_file(FILENAME, target_ppm, target_water_level)

        # Fill water to the target level in the reservoir
        fill_water(target_water_level)

        # Dose nutrients based on the target PPM
        dose_nutrients(target_ppm, NUTRIENT_PUMP_TIME_LIST, NUTRIENT_WAIT_TIME_LOOP)

        # Balance pH levels to the desired range
        balance_PH_exact(target_min_max_ph, ph_dosing_time)

        # Log the completion of the system setup
        logging.info("Startup completed")

        # Wait for 30 seconds to allow PPM to settle
        sleep(30)

        # Update target PPM after ph was balanced
        target_ppm = get_ppm()
        write_to_file(FILENAME, target_ppm, target_water_level)
    else:
        # If the water level is above the threshold, log that the system is already set up
        logging.info("Hydroponic system already set up")


def monitor_hydroponic_system(WATER_LEVEL_CHANGE_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS, target_min_max_ph,
                              ph_dosing_time, NUTRIENT_PPM_SAFETY_MARGIN, NUTRIENT_PUMP_TIME_LIST,
                              NUTRIENT_WAIT_TIME_LOOP):
    """
    Continuously monitor the hydroponic system, adjusting water level, dosing nutrients, and balancing pH as needed.
    """
    while True:
        try:
            # Read the target PPM and water level values from the file
            target_ppm, target_water_level = read_from_file(FILENAME)
            # Check if the difference between the current water level and the target water level
            # is greater than the defined threshold
            if get_water_level(a, b, c) - target_water_level > WATER_LEVEL_CHANGE_THRESHOLD:
                # Adjust water level and nutrients if the difference is greater than the threshold
                adjust_water_level_and_nutrients(NUTRIENT_PPM_SAFETY_MARGIN, NUTRIENT_PUMP_TIME_LIST,
                                                 NUTRIENT_WAIT_TIME_LOOP, target_min_max_ph, ph_dosing_time)
            else:
                # If the difference is within the threshold, balance the pH levels
                balance_ph(target_min_max_ph, ph_dosing_time)  # Keep within range
                # update the values of ppm and water level
                write_to_file(FILENAME, get_ppm(), get_water_level(a, b, c))
                # Sleep for a defined time before checking water level and pH again
                sleep(WAIT_TIME_BETWEEN_CHECKS)
        except Exception as eeee:
            # Log any errors that occur during the monitoring process
            logging.error(f"An error occurred: {eeee}")

            # Sleep for a defined time before attempting to monitor the hydroponic system again
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    # Get the user's plant selection
    logging.info("Please enter the plant species (e.g., plant_A, plant_B): ")
    plant_selection = input().strip()

    # Check if the plant selection exists in the plants dictionary
    while plant_selection not in PLANTS:
        logging.error("Invalid plant selection. Please enter a valid plant species (e.g., plant_A, plant_B): ")
        plant_selection = input().strip()

    # Update the parameters based on the selected plant
    plant_params = PLANTS[plant_selection]

    target_min_max_ph = plant_params['ph_settings']['target_min_ph'], plant_params['ph_settings']['target_max_ph']
    NUTRIENT_PUMP_TIME_LIST = plant_params['nutrient_settings']['nutrient_pump_times']
    WATER_LEVEL_CHANGE_THRESHOLD = plant_params['water_settings']['level_change_threshold']
    WAIT_TIME_BETWEEN_CHECKS = plant_params['water_settings']['wait_time_between_checks']
    NUTRIENT_PPM_SAFETY_MARGIN = plant_params['nutrient_settings']['ppm_safety_margin']
    NUTRIENT_WAIT_TIME_LOOP = plant_params['nutrient_settings']['wait_time_loop']
    ph_dosing_time = plant_params['ph_settings']['dosing_time']

    # Set up the hydroponic system
    setup_hydroponic_system(NUTRIENT_PUMP_TIME_LIST, NUTRIENT_WAIT_TIME_LOOP, target_min_max_ph, ph_dosing_time)
    # Continuously monitor the hydroponic system
    monitor_hydroponic_system(WATER_LEVEL_CHANGE_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS, target_min_max_ph,
                              ph_dosing_time, NUTRIENT_PPM_SAFETY_MARGIN, NUTRIENT_PUMP_TIME_LIST,
                              NUTRIENT_WAIT_TIME_LOOP)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        stop_pumps_list(ALL_PUMPS)
