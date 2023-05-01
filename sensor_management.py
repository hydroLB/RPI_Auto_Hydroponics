from WaterSensor import *
from time import sleep
from pump_control import *


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


