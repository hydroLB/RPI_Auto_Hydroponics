# Two functions: balance_ph keeps it in range, the exact version reaches a precise measurement

from time import sleep

# Target pH values and limits
from Atlas_and_pump_utilities.AtlasI2C import get_ph
from user_config.user_configurator import Plant


def balance_ph(ph_dosing_time, plant, ph_pump_list):
    """
    Keeps pH in the range provided in the user_config.

    Args:
        ph_dosing_time (tuple): A tuple containing the sleep times for pH up, pH down, and loop sleep times.
        plant (Plant): A Plant object containing target and range pH values.
        ph_pump_list (list): A list of pH pump objects.
    """
    try:
        if not isinstance(ph_dosing_time, (list, tuple)) or len(ph_dosing_time) != 3:
            raise TypeError("Expected ph_dosing_time to be a list or tuple with 3 elements, but got type {}. "
                            "Error in balance_ph.".format(type(ph_dosing_time).__name__))
        if not isinstance(plant, Plant):
            raise TypeError("Expected plant to be a Plant object, but got type {}. "
                            "Error in balance_ph.".format(type(plant).__name__))
        if not isinstance(ph_pump_list, list) or len(ph_pump_list) != 2:
            raise TypeError("Expected ph_pump_list to be a list with 2 elements, but got type {}. "
                            "Error in balance_ph.".format(type(ph_pump_list).__name__))

        # Get pH values for range and target
        target_min_max_ph = plant.target_ph, plant.min_ph, plant.max_ph

        TARGET_PH = target_min_max_ph[0]
        MIN_PH = target_min_max_ph[1]
        MAX_PH = target_min_max_ph[2]

        pHUpPump = ph_pump_list[0]
        pHDownPump = ph_pump_list[1]

        # Get the amount each pump is on
        ph_up_sleep_time = ph_dosing_time[0]
        ph_down_sleep_time = ph_dosing_time[1]
        loop_sleep_time = ph_dosing_time[2]

        if get_ph() < MIN_PH:  # Check if the current pH value is less than the minimum pH value
            while get_ph() < TARGET_PH:  # Keep running the loop while the pH value is less than the target pH value
                print("Increasing PH, PH: %f" % (get_ph()))  # Print current pH val and indicate it's being increased
                pHUpPump.start()  # Start the pH up pump
                sleep(ph_up_sleep_time)  # Pause the program for the specified time
                pHUpPump.stop()  # Stop the pH up pump
                sleep(loop_sleep_time)  # Pause the program for the specified time
            pHUpPump.stop()  # Ensure the pH up pump is stopped when the pH value reaches the target value
        elif get_ph() > MAX_PH:  # Check if the current pH value is greater than the maximum pH value
            while get_ph() > TARGET_PH:  # Keep running the loop while the pH value is greater than the target pH value
                print("Reducing PH, PH: %f" % (get_ph()))  # Print current pH val and indicate that it's being reduced
                pHDownPump.start()  # Start the pH down pump
                sleep(ph_down_sleep_time)  # Pause the program for the specified time
                pHDownPump.stop()  # Stop the pH down pump
                sleep(loop_sleep_time)  # Pause the program for the specified time
            pHDownPump.stop()  # Ensure the pH down pump is stopped when the pH value reaches the target value

    except TypeError as e:
        raise TypeError("Type error occurred in balance_ph: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in balance_ph: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in balance_ph: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in balance_ph: {}".format(e))


def balance_PH_exact(ph_dosing_time, plant, ph_pump_list):
    """
    Adjusts the pH to the exact target pH value provided in the plant configuration.

    Args:
        ph_dosing_time (tuple): A tuple containing the sleep times for pH up, pH down, and loop sleep times.
        plant (Plant): A Plant object containing target pH value.
        ph_pump_list (list): A list of pH pump objects.
    """
    try:
        if not isinstance(ph_dosing_time, (list, tuple)) or len(ph_dosing_time) != 3:
            raise TypeError(
                "Expected ph_dosing_time to be a list or tuple with 3 elements, "
                "but got type {}. Error in balance_PH_exact.".format(
                    type(ph_dosing_time).__name__))
        if not isinstance(plant, Plant):
            raise TypeError("Expected plant to be a Plant object, but got type {}. Error in balance_PH_exact.".format(
                type(plant).__name__))
        if not isinstance(ph_pump_list, list) or len(ph_pump_list) != 2:
            raise TypeError(
                "Expected ph_pump_list to be a list with 2 elements, "
                "but got type {}. Error in balance_PH_exact.".format(
                    type(ph_pump_list).__name__))

        # Get the amount each pump is on
        ph_up_sleep_time = ph_dosing_time[0]
        ph_down_sleep_time = ph_dosing_time[1]
        loop_sleep_time = ph_dosing_time[2]

        pHUpPump = ph_pump_list[0]
        pHDownPump = ph_pump_list[1]

        current_ph = get_ph()

        if current_ph < plant.target_ph:  # Check if the current pH value is less than the target pH value
            while get_ph() < plant.target_ph:  # Keep running loop while  pH value is less than the target pH value
                print(
                    "Increasing PH, PH: %f" % get_ph())  # Print current pH val and indicate  it's being increased
                pHUpPump.start()  # Start the pH up pump
                sleep(ph_up_sleep_time)  # Pause the program for the specified time
                pHUpPump.stop()  # Stop the pH up pump
                sleep(loop_sleep_time)  # Pause the program for the specified time
            pHUpPump.stop()  # Ensure the pH up pump is stopped when the pH value reaches the target value
        elif current_ph > plant.target_ph:  # Check if the current pH value is greater than the target pH value
            while get_ph() > plant.target_ph:  # Keep running loop while pH value is greater than  target pH value
                print(
                    "Reducing PH, PH: %f" % get_ph())  # Print the current pH value and indicate that it's being reduced
                pHDownPump.start()  # Start the pH down pump
                sleep(ph_down_sleep_time)  # Pause the program for the specified time
                pHDownPump.stop()  # Stop the pH down pump
                sleep(loop_sleep_time)  # Pause the program for the specified time
            pHDownPump.stop()  # Ensure the pH down pump is stopped when the pH value reaches the target value

    except TypeError as e:
        raise TypeError("Type error occurred in balance_PH_exact: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in balance_PH_exact: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in balance_PH_exact: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in balance_PH_exact: {}".format(e))
