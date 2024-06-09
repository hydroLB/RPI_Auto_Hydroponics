import os
import Adafruit_ADS1x15
import numpy as np
import json
from scipy.optimize import curve_fit
import time

# Initialize the ADC using the Adafruit_ADS1x15 library
from user_config.user_configurator import ADC_BUSNUM, ADC_I2C_ADDRESS

adc = Adafruit_ADS1x15.ADS1115(busnum=ADC_BUSNUM, address=ADC_I2C_ADDRESS)

# Set the gain value for the ADC
GAIN = 1


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
            print(f"Warning: Failed to read sensor value after 5 attempts for sample {i+1}.")
            return None

    if successful_reads == 0:
        return None

    average_value = total / successful_reads
    return average_value


def initialize_water_sensor():
    # File to store calibration coefficients
    coefficients_file = 'calibration_coefficients.txt'
    """Calibrate the water sensor."""
    print("\n Starting water sensor calibration...")

    # Enhanced directory writability check
    try:
        dir_name = os.path.dirname(coefficients_file)
        if dir_name and not os.access(dir_name, os.W_OK):
            print(f"Warning: Directory {dir_name} is not writable in initialize_water_sensor.")
            return
    except Exception as e:
        print(f"Error checking directory write access in initialize_water_sensor: {e}")
        return

    print("Please adjust the water to the specified levels.")
    calibration_data = []
    for target_level in np.arange(1.5, 7, 0.5):  # 1.5, 2, ..., 6.5 inches
        while True:
            user_input = input(
                f"Type 'confirm {target_level}' when the water is at {target_level} inches: ").strip().lower()
            if user_input == f"confirm {target_level}":
                try:
                    average_sensor_value = get_average_sensor_value()
                    calibration_data.append((target_level, average_sensor_value))
                    print(f"Averaged sensor value at {target_level} inches: {average_sensor_value}")
                except Exception as e:
                    print(f"Error during calibration at {target_level} inches in initialize_water_sensor: {e}")
                    return
                break
            else:
                print("Invalid input. Please follow the format 'confirm <level>'.")
                print(f"Example: Type 'confirm {target_level}' to confirm the water level.")

    if len(calibration_data) < 3:
        print("Insufficient calibration data collected. Calibration requires at "
              "least 3 data points in initialize_water_sensor")
        return

    levels, sensor_values = zip(*calibration_data)

    # Perform curve fitting
    try:
        popt, _ = curve_fit(quadratic_model, sensor_values, levels)
    except Exception as e:
        print(f"Error during curve fitting in initialize_water_sensor: {e}")
        return

    coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
    print(f" \n Calibration complete. Coefficients: {coefficients} \n ")

    try:
        save_coefficients(coefficients)
    except Exception as e:
        print(f"Error saving coefficients in initialize_water_sensor: {e}")
