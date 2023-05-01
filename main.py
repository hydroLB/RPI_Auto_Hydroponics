from pump_config import *
from pump_control import prime, stop_pumps_list, run_pumps_list
from water_management import *
from nutrient_management import *
from ph_management import *
from file_operations import *
from logging_config import *
from adafruit_motorkit import MotorKit
from AtlasI2C import AtlasI2C
import Adafruit_ADS1x15

# VARIABLE CONFIGURATION

filename = "settings.txt"  # where idea water level and last fillup ppm is stored

# Vars for 1-wire temp sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'

# Initialize ECSensor and PHSensor
ECSensor = AtlasI2C(100)
PHSensor = AtlasI2C(99)

# Initialize the ADC (Analog-to-Digital Converter) with I2C address and bus number
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
# Set the gain value for the ADC
GAIN = 1
# Coefficients for quadratic equation to convert reading to water level
a = -.0034
b = -.0103
c = .9816

# Initialize motor drivers with I2C addresses
driver0 = MotorKit(0x60)
driver1 = MotorKit(0x61)

skip_system_setup_water_level = 1.5 # Indicates the minimum water level for the system to recognize a completed setup
# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in
# seconds) WAIT_TIME_BETWEEN_CHECKS = how long should the raspberry pi wait to check the water level and then if the
# ph is within soft range
WATER_LEVEL_CHANGE_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 3.0, 1000

nutrient_pump_times = [5, 5, 5, 5]  # Time in seconds for each nute pump to run
# Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
# to avoid overloading the nutrients when the pH is balanced after (which always raises it to some degree).
NUTRIENT_PPM_SAFETY_MARGIN = 30
# how long should the RPI wait in between dosing nutrients to reach the target PPM
NUTRIENT_WAIT_TIME_LOOP = 10

target_min_max_ph = [5.8, 5.6, 6.2]  # [TARGET_PH, MIN_PH, MAX_PH]
# 1.  Sleep time for pH up pump (how long is it on)
# 2.  Sleep time for pH down pump (how long is it on)
# 3.  Sleep time for the loop (how long to wait between each increment dosing)
ph_dosing_time = [0.1, 0.1, 10]  # [PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME]


def setup_hydroponic_system():
    """
    Set up the hydroponic system by priming pumps, filling water, dosing nutrients, and balancing pH.
    """
    # Check if the water level is below the threshold for system setup
    if get_water_level(a, b, c) < skip_system_setup_water_level:

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
        write_to_file(filename, target_ppm, target_water_level)

        # Fill water to the target level in the reservoir
        fill_water(target_water_level)

        # Dose nutrients based on the target PPM
        dose_nutrients(target_ppm, nutrient_pump_time_list, NUTRIENT_WAIT_TIME_LOOP)

        # Balance pH levels to the desired range
        balance_PH_exact(target_min_max_ph, ph_dosing_time)

        # Log the completion of the system setup
        logging.info("Startup completed")

        # Wait for 30 seconds to allow PPM to settle
        sleep(30)

        # Update target PPM after ph was balanced
        target_ppm = get_ppm()
        write_to_file(filename, target_ppm, target_water_level)
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
            target_ppm, target_water_level = read_from_file(filename)
            # Check if the difference between the current water level and the target water level
            # is greater than the defined threshold
            if get_water_level(a, b, c) - target_water_level > WATER_LEVEL_CHANGE_THRESHOLD:
                # Adjust water level and nutrients if the difference is greater than the threshold
                adjust_water_level_and_nutrients()
            else:
                # If the difference is within the threshold, balance the pH levels
                balance_ph(target_min_max_ph, ph_dosing_time)  # Keep within range
                # update the values of ppm and water level
                write_to_file(filename, get_ppm(), get_water_level(a, b, c))
                # Sleep for a defined time before checking water level and pH again
                sleep(WAIT_TIME_BETWEEN_CHECKS)
        except Exception as eeee:
            # Log any errors that occur during the monitoring process
            logging.error(f"An error occurred: {eeee}")

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
