# Two functions: balance_ph keeps it in range, the exact version reaches a precise measurement

from time import sleep

# Target pH values and limits
from Atlas_and_pump_utilities.AtlasI2C import get_ph


#  keeps ph in the range provided in the user_config
def balance_ph(ph_dosing_time, plant, ph_pump_list):
    # get ph values for range and target
    target_min_max_ph = plant.target_ph, plant.min_ph, plant.max_ph

    TARGET_PH = target_min_max_ph[0]
    MIN_PH = target_min_max_ph[1]
    MAX_PH = target_min_max_ph[2]

    pHUpPump = ph_pump_list[0]
    pHDownPump = ph_pump_list[1]

    # get the amount each pump is on
    ph_up_sleep_time = ph_dosing_time[0]
    ph_down_sleep_time = ph_dosing_time[1]
    loop_sleep_time = ph_dosing_time[2]

    if get_ph() < MIN_PH:  # Check if the current pH value is less than the minimum pH value
        while get_ph() < TARGET_PH:  # Keep running the loop while the pH value is less than the target pH value
            print("Increasing PH, PH: %f" % (
                get_ph()))  # Print the current pH value and indicate that it's being increased
            pHUpPump.start()  # Start the pH up pump
            sleep(ph_up_sleep_time)  # Pause the program for 0.1 seconds
            pHUpPump.stop()  # Stop the pH up pump
            sleep(loop_sleep_time)  # Pause the program for 10 seconds
        pHUpPump.stop()  # Stop the pH up pump when the pH value reaches the target value
    elif get_ph() > MAX_PH:  # Check if the current pH value is greater than the maximum pH value
        while get_ph() > TARGET_PH:  # Keep running the loop while the pH value is greater than the target pH value
            print("Reducing PH, PH: %f" % (get_ph()))  # Print the current pH value and indicate that it's being reduced
            pHDownPump.start()  # Start the pH down pump
            sleep(ph_down_sleep_time)  # Pause the program for 0.1 seconds
            pHDownPump.stop()  # Stop the pH down pump
            sleep(loop_sleep_time)  # Pause the program for 10 seconds
        pHDownPump.stop()  # Stop the pH down pump when the pH value reaches the target value


def balance_PH_exact(ph_dosing_time, plant, ph_pump_list):
    # get the amount each pump is on
    ph_up_sleep_time = ph_dosing_time[0]
    ph_down_sleep_time = ph_dosing_time[1]
    loop_sleep_time = ph_dosing_time[2]

    pHUpPump = ph_pump_list[0]
    pHDownPump = ph_pump_list[1]

    if get_ph() < plant.target_ph:  # Check if the current pH value is less than the target pH value
        while get_ph() < plant.target_ph:  # Keep running the loop while the pH value is less than the target pH value
            print("Increasing PH, PH: %f" % (
                get_ph()))  # Print the current pH value and indicate that it's being increased
            pHUpPump.start()  # Start the pH up pump
            sleep(ph_up_sleep_time)  # Pause the program for PH_UP_SLEEP_TIME
            pHUpPump.stop()  # Stop the pH up pump
            sleep(loop_sleep_time)  # Pause the program for LOOP_SLEEP_TIME
        pHUpPump.stop()  # Stop the pH up pump when the pH value reaches the target value
    elif get_ph() > plant.target_ph:  # Check if the current pH value is greater than the target pH value
        while get_ph() > plant.target_ph:  # Keep running the loop while pH value is greater than the target pH value
            print("Reducing PH, PH: %f" % (get_ph()))  # Print the current pH value and indicate that it's being reduced
            pHDownPump.start()  # Start the pH down pump
            sleep(ph_down_sleep_time)  # Pause the program for PH_DOWN_SLEEP_TIME
            pHDownPump.stop()  # Stop the pH down pump
            sleep(loop_sleep_time)  # Pause the program for LOOP_SLEEP_TIME
        pHDownPump.stop()  # Stop the pH down pump when the pH value reaches the target value
