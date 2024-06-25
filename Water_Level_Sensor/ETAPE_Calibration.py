import os
import Adafruit_ADS1x15
import numpy as np
import json
from scipy.optimize import curve_fit
import time
import threading

from Atlas_and_pump_utilities.pumps import start_fresh_water_pump, end_fresh_water_pump
# Initialize the ADC using the Adafruit_ADS1x15 library
from user_config.user_configurator import ADC_BUSNUM, ADC_I2C_ADDRESS, FRESH_WATER_PUMP_PIN

adc = Adafruit_ADS1x15.ADS1115(busnum=ADC_BUSNUM, address=ADC_I2C_ADDRESS)

# Set the gain value for the ADC
GAIN = 1

# Define stop_event at the module level
stop_event = threading.Event()


def quadratic_model(x, a, b, c):
    """
    Quadratic model for curve fitting.

    Args:
        x (float): The input value for the model.
        a (float): The quadratic coefficient.
        b (float): The linear coefficient.
        c (float): The constant term.

    Returns:
        float: The calculated value of the quadratic model.
    """
    try:
        if not isinstance(x, (int, float, np.ndarray)):
            raise TypeError(
                "Expected x to be an int or float, but got type {}. Error in quadratic_model.".format(type(x).__name__))
        if not isinstance(a, (int, float)):
            raise TypeError(
                "Expected a to be an int or float, but got type {}. Error in quadratic_model.".format(type(a).__name__))
        if not isinstance(b, (int, float)):
            raise TypeError(
                "Expected b to be an int or float, but got type {}. Error in quadratic_model.".format(type(b).__name__))
        if not isinstance(c, (int, float)):
            raise TypeError(
                "Expected c to be an int or float, but got type {}. Error in quadratic_model.".format(type(c).__name__))

        return a * x ** 2 + b * x + c

    except TypeError as e:
        raise TypeError("Type error occurred in quadratic_model: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in quadratic_model: {}".format(e))


def save_coefficients(coefficients):
    """
    Save calibration coefficients to a file.

    Args:
        coefficients (dict): The calibration coefficients to be saved.
    """
    try:
        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, "calibration_coefficients.txt")

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Open the file in write mode and save the coefficients
        with open(file_path, 'w') as file:
            json.dump(coefficients, file)
        print(f"\n Calibration coefficients saved to {file_path} \n")

    except IOError as e:
        print(f"Error saving calibration coefficients: {e}")
        raise


def get_average_sensor_value(num_samples=5):
    """Get the RAW average sensor value over a number of samples for the E-tape."""
    total = 0
    successful_reads = 0

    for i in range(num_samples):
        attempts = 5
        for attempt in range(attempts):
            try:
                # Read raw eTape sensor values from the ADC
                raw_val = adc.read_adc(0, gain=GAIN)
                if raw_val is not None:
                    total += raw_val
                    successful_reads += 1
                    break
                else:
                    time.sleep(0.1)  # Small delay before retrying
            except Exception as e:
                print(f"Error reading sensor values in get_average_sensor_value: {e}")
                raise
        else:
            print(f"Warning: Failed to read sensor value after 5 attempts for sample {i + 1}.")
            return None

    if successful_reads == 0:
        return None

    average_value = total / successful_reads
    return average_value


def pump_control(pin):
    """Control the pump intermittently."""
    while not stop_event.is_set():
        start_fresh_water_pump(pin)
        time.sleep(2)
        end_fresh_water_pump(pin)
        if stop_event.is_set():
            break
        time.sleep(2)


def initialize_water_sensor():
    coefficients_file = 'calibration_coefficients.txt'
    if os.path.exists(coefficients_file):
        try:
            with open(coefficients_file, 'r') as f:
                coefficients = eval(f.read())  # Using eval is risky; consider using json for parsing
            if all(key in coefficients for key in ['a', 'b', 'c']):
                print("Calibration coefficients already exist. Initialization aborted.")
                return
        except Exception as e:
            print(f"Error reading or validating coefficients: {e}")

    print("\nStarting water sensor calibration...")
    calibration_data = []
    for target_level in np.arange(1.5, 6.5, 0.5):  # 1.5, 2, ..., 6.0 inches
        stop_event.clear()
        pump_thread = threading.Thread(target=pump_control, args=(FRESH_WATER_PUMP_PIN,))
        pump_thread.start()

        while True:
            user_input = input(
                f"Type 'confirm {target_level}' when the water is at {target_level} inches: ").strip().lower()
            if user_input == f"confirm {target_level}":
                stop_event.set()
                pump_thread.join()  # Ensure the thread finishes before continuing
                try:
                    average_sensor_value = get_average_sensor_value()
                    calibration_data.append((target_level, average_sensor_value))
                    print(f"Averaged sensor value at {target_level} inches: {average_sensor_value}")
                    time.sleep(5)
                except Exception as e:
                    print(f"Error during calibration at {target_level} inches: {e}")
                    return
                break
            else:
                print("Invalid input. Please follow the format 'confirm <level>'.")
                time.sleep(5)

        stop_event.set()
        if pump_thread.is_alive():
            pump_thread.join()

    if len(calibration_data) < 3:
        print("Insufficient calibration data collected. Calibration requires at least 3 data points.")
        return

    levels, sensor_values = zip(*calibration_data)
    try:
        popt, _ = curve_fit(quadratic_model, sensor_values, levels)
        coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
        print(f"\nCalibration complete. Coefficients: {coefficients}\n")
        save_coefficients(coefficients)
    except Exception as e:
        print(f"Error during curve fitting: {e}")
