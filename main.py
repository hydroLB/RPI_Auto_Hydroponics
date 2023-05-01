from time import sleep
from WaterSensor import *
from stopmotors import stop_pumps_list
from tempAtlas import *
import sys
from pump_config import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to write target_ppm and target_water_level to a file
def write_to_file(target_ppm, target_water_level):
    with open("settings.txt", "w") as file:
        file.write(f"{target_ppm},{target_water_level}")


# Function to read target_ppm and target_water_level from a file
def read_from_file():
    with open("settings.txt", "r") as file:
        data = file.read().split(',')
        target_ppm = int(data[0])
        target_water_level = int(data[1])

    return target_ppm, target_water_level


# Target pH values and limits
TARGET_PH, MIN_PH, MAX_PH = 5.8, 5.6, 6.2

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 3, 1000

# Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced (which always raises it to some degree).
NUTRIENT_PPM_SAFETY_MARGIN = 30

PH_UP_SLEEP_TIME = 0.1  # Sleep time for pH up pump (how long is it on)
PH_DOWN_SLEEP_TIME = 0.1  # Sleep time for pH down pump (how long is it on)
LOOP_SLEEP_TIME = 10  # Sleep time for the loop ((how long to wait between each increment dosing)


# Prime pumps with the user's help
def prime(pumps_list):
    for pump in pumps_list:
        counter = 1
        print("Press enter to start priming pump" + str(
            counter) + ", then press enter to stop when liquid level reaches the end of the pumps tubing")
        counter += 1
        sys.stdin.readline()  # Wait for user to hit enter
        pump.start()
        sys.stdin.readline()  # Wait for user to hit enter
        pump.stop()
    print("All pumps primed")


def fill_water(target_level):
    """
    Fill the water reservoir until the target water level is reached.

    :param target_level: The desired water level to be reached in the reservoir.
    """
    try:
        # Continuously check the current water level in the reservoir
        while get_water_level() < target_level:
            # Display the current water level while adding water
            print("Adding water... level %f" % (get_water_level()))
            # Start the water pump to fill the reservoir
            waterPump.start()
            # Wait for 5 seconds to allow the water pump to operate
            sleep(5)
        # Stop the water pump once the target water level is reached
        waterPump.stop()
    except Exception as ee:
        # Log the error message and stop the water pump in case of an exception
        logging.error(f"An error occurred while filling water: {ee}")
        waterPump.stop()


def dose_nutrients(target_ppm_local, pump_info):
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
        sleep(10)


def balance_ph():
    if get_ph() < MIN_PH:  # Check if the current pH value is less than the minimum pH value
        while get_ph() < TARGET_PH:  # Keep running the loop while the pH value is less than the target pH value
            print("Increasing PH, PH: %f" % (
                get_ph()))  # Print the current pH value and indicate that it's being increased
            pHUpPump.start()  # Start the pH up pump
            sleep(PH_UP_SLEEP_TIME)  # Pause the program for 0.1 seconds
            pHUpPump.stop()  # Stop the pH up pump
            sleep(LOOP_SLEEP_TIME)  # Pause the program for 10 seconds
        pHUpPump.stop()  # Stop the pH up pump when the pH value reaches the target value
    elif get_ph() > MAX_PH:  # Check if the current pH value is greater than the maximum pH value
        while get_ph() > TARGET_PH:  # Keep running the loop while the pH value is greater than the target pH value
            print("Reducing PH, PH: %f" % (get_ph()))  # Print the current pH value and indicate that it's being reduced
            pHDownPump.start()  # Start the pH down pump
            sleep(PH_DOWN_SLEEP_TIME)  # Pause the program for 0.1 seconds
            pHDownPump.stop()  # Stop the pH down pump
            sleep(LOOP_SLEEP_TIME)  # Pause the program for 10 seconds
        pHDownPump.stop()  # Stop the pH down pump when the pH value reaches the target value


def balance_PH_exact():
    if get_ph() < TARGET_PH:  # Check if the current pH value is less than the target pH value
        while get_ph() < TARGET_PH:  # Keep running the loop while the pH value is less than the target pH value
            print("Increasing PH, PH: %f" % (
                get_ph()))  # Print the current pH value and indicate that it's being increased
            pHUpPump.start()  # Start the pH up pump
            sleep(PH_UP_SLEEP_TIME)  # Pause the program for PH_UP_SLEEP_TIME
            pHUpPump.stop()  # Stop the pH up pump
            sleep(LOOP_SLEEP_TIME)  # Pause the program for LOOP_SLEEP_TIME
        pHUpPump.stop()  # Stop the pH up pump when the pH value reaches the target value
    elif get_ph() > TARGET_PH:  # Check if the current pH value is greater than the target pH value
        while get_ph() > TARGET_PH:  # Keep running the loop while the pH value is greater than the target pH value
            print("Reducing PH, PH: %f" % (get_ph()))  # Print the current pH value and indicate that it's being reduced
            pHDownPump.start()  # Start the pH down pump
            sleep(PH_DOWN_SLEEP_TIME)  # Pause the program for PH_DOWN_SLEEP_TIME
            pHDownPump.stop()  # Stop the pH down pump
            sleep(LOOP_SLEEP_TIME)  # Pause the program for LOOP_SLEEP_TIME
        pHDownPump.stop()  # Stop the pH down pump when the pH value reaches the target value


# This is needed to get all the pumps to the same point and ensure any liquid left
# over in the tubes is removed, priming it
def run_pumps_list(pumps_list, reverse=False):
    """
    Start all pumps in the given list in forward or reverse mode.
    Args:
        pumps_list: List of pump objects to be run.
        reverse: Boolean indicating whether pumps should run in reverse mode (default: False).
    """
    for pump in pumps_list:
        if reverse:
            pump.startReverse()
        else:
            pump.start()


def adjust_water_level_and_nutrients():
    target_ppm, target_water_level = read_from_file()

    pre_fillup_ppm = get_ppm()
    fill_water(target_water_level)
    sleep(30)  # Wait for PPM readings to settle

    # Update target PPM based on plant's nutrient consumption rate
    target_ppm += (target_ppm - pre_fillup_ppm)

    write_to_file(target_ppm, target_water_level)

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(target_ppm - NUTRIENT_PPM_SAFETY_MARGIN, nutrient_pump_time_list)
    balance_PH_exact()
    dose_nutrients(target_ppm, nutrient_pump_time_list)


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
    setup_hydroponic_system()
    monitor_hydroponic_system()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
