import math
import os
import Adafruit_ADS1x15
import numpy as np
import json
from scipy.optimize import curve_fit
import time
import threading

from ph_ppm_pump_sensor.pumps import start_fresh_water_pump, end_fresh_water_pump
from file_operations.clear_terminal import clear_terminal
# Initialize the ADC using the Adafruit_ADS1x15 library
from user_config.user_configurator import ADC_BUSNUM, ADC_I2C_ADDRESS, FRESH_WATER_PUMP_PIN, \
    fresh_water_pump_time_off, fresh_water_pump_time_on
from water_level_sensor.Water_Level_ETAPE import load_coefficients

adc = Adafruit_ADS1x15.ADS1115(busnum=ADC_BUSNUM, address=ADC_I2C_ADDRESS)
global counter

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
        print(f"\nCalibration coefficients saved to {file_path} \n")
        time.sleep(3)
        clear_terminal()

    except IOError as e:
        print(f"Error saving calibration coefficients: {e}")
        raise


def get_average_sensor_value(num_samples=5):
    """Get the RAW average sensor value over a number of samples for the E-tape."""
    total = 0
    successful_reads = 0
    time.sleep(6)

    for i in range(num_samples):
        attempts = 5
        for attempt in range(attempts):
            try:
                # Read raw eTape sensor values from the ADC
                raw_val = adc.read_adc(0, gain=GAIN)
                time.sleep(3)
                if raw_val is not None:
                    total += raw_val
                    successful_reads += 1
                    break
                else:
                    time.sleep(1)  # Small delay before retrying
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


pump_times = {}  # Dictionary to store pump times for each half-inch increment


def pump_control(pin, water_level):
    """
    Control the pump intermittently.

    Args:
        pin (int): Pin num to control the pump.

    Raises:
        Exception: If there is an unexpected error during pump control.

    Notes:
        This function controls the pump by starting and stopping it in intervals.
        It checks a global threading.Event (`stop_event`) to know when to stop the pump.
        Uses functions `start_fresh_water_pump()` and `end_fresh_water_pump()` from external modules.
    """

    global counter
    try:
        while not stop_event.is_set():
            start_fresh_water_pump(pin)
            time.sleep(fresh_water_pump_time_on)
            counter += fresh_water_pump_time_on
            end_fresh_water_pump(pin)
            if stop_event.is_set():
                pump_times[water_level] = counter
                break
            time.sleep(fresh_water_pump_time_off)
    except Exception as e:
        raise Exception(f"Unexpected error during pump control: {e}")


def initialize_water_sensor():
    """
    Main function to initialize the water sensor calibration process.

    Raises:
        IOError: If there is an error reading or writing calibration coefficients.
        ValueError: If insufficient calibration data is collected.
        Exception: For any unexpected errors during calibration.

    Notes:
        - Checks if calibration coefficients already exist using `load_coefficients()`.
        - If coefficients don't exist, initiates the calibration process using `calibrate_water_sensor()`.
        - Performs curve fitting and saves coefficients if enough calibration data is collected.
        - Uses functions `curve_fit()`, `save_coefficients()`, and `calibrate_water_sensor()` from this module.
    """
    try:
        # Check if calibration coefficients already exist
        if load_coefficients() is not None:
            return

        print("\nStarting water sensor calibration...\n")
        calibration_data = calibrate_water_sensor()

        # Check if enough calibration data was collected
        if len(calibration_data) >= 3:
            try:
                # Curve fitting using collected calibration data
                levels, sensor_values = zip(*calibration_data)
                popt, _ = curve_fit(quadratic_model, sensor_values, levels)
                coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
                print(f"\nCalibration complete. Coefficients: {coefficients}\n")
                save_coefficients(coefficients)
            except Exception as e:
                raise Exception(f"Error during curve fitting: {e}")
        else:
            raise ValueError("Insufficient calibration data collected. Calibration requires at least 3 data points.")

    except IOError as e:
        print(f"Error reading or writing calibration coefficients: {e}")
        raise
    except ValueError as e:
        print(f"ValueError: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during water sensor initialization: {e}")
        raise


def user_input_thread(target_level, pump_thread, calibration_data):
    """
    Thread function to handle user input for calibration.
    """
    while True:
        try:
            user_input = input(
                f"Type '{target_level}' when the water is at {target_level} inches: ").strip().lower()
            if user_input == f"{target_level}":
                stop_event.set()
                pump_thread.join(timeout=10)
                if pump_thread.is_alive():
                    print("Warning: Pump control thread did not terminate correctly.")
                print("getting sensor value, this will take 20 seconds, please wait...")
                average_sensor_value = get_average_sensor_value()
                calibration_data.append((target_level, average_sensor_value))
                print(f"Averaged sensor value at {target_level} inches: {average_sensor_value}")
                time.sleep(4)
                clear_terminal()
                time.sleep(1)
                break
            else:
                print(f"Invalid input. Please type '{target_level}' to proceed.")
        except Exception as e:
            print(f"Unexpected error during user interaction: {e}")
            stop_event.set()
            pump_thread.join(timeout=10)
            if pump_thread.is_alive():
                print("Critical error: Unable to properly stop pump control thread.")
            return


directory = "created_saved_values"
filename = os.path.join(directory, "pump_times.txt")


def calibrate_water_sensor():
    """
    Performs the calibration process for the water sensor.
    Returns a list of (water level, sensor value) tuples.

    Raises:
        Exception: If there is an unexpected error during the calibration process.

    Notes:
        - Iterates through target water levels and prompts user confirmation.
        - Uses threading to control pump operation asynchronously.
        - Handles user input validation and error conditions during calibration.
        - Calls `get_average_sensor_value()`, `clear_terminal()`, and `pump_control()` functions.
    """
    calibration_data = []

    try:
        for target_level in np.arange(1.5, 6.5, 0.5):
            stop_event.clear()
            pump_thread = threading.Thread(target=pump_control, args=(FRESH_WATER_PUMP_PIN, target_level))
            pump_thread.start()

            input_thread = threading.Thread(target=user_input_thread,
                                            args=(target_level, pump_thread, calibration_data))
            input_thread.start()
            input_thread.join()

            stop_event.set()
            if pump_thread.is_alive():
                pump_thread.join()

        try:
            # Save the pump times to a file
            with open(filename, "w", encoding="utf-8") as file:
                for level, time in pump_times.items():
                    file.write(f"{level}:{time}\n")
            print(f"Pump times successfully saved to {filename}")
        except Exception as e:
            print(f"An error occurred while saving pump times: {e}")

    except Exception as e:
        print(f"Error during calibration process: {e}")
        raise

    return calibration_data


def load_pump_times(filename):
    """
    Loads the pump times from a file.

    Args:
        filename (str): The path to the file containing the pump times.

    Returns:
        dict: A dictionary with half-inch increments as keys and pump times as values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid data.
    """
    loadpump_times = {}

    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file {filename} does not exist.")

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    # Split by colon and filter out empty strings
                    parts = list(filter(None, line.strip().split(":")))
                    if len(parts) != 2:
                        raise ValueError(f"Invalid data format in file: {line}")
                    level, time = parts
                    loadpump_times[float(level)] = float(time)
                except ValueError as e:
                    raise ValueError(f"Invalid data format in file: {line}. Error: {e}")

    except Exception as e:
        raise Exception(f"Unexpected error while loading pump times: {e}")

    return loadpump_times


def time_to_reach(current_level, target_level):

    time_to_reach_pump_time = load_pump_times()

    if time_to_reach_pump_time is None:
        return None

    """
    Calculates the estimated time to pump water from the current level to the target level.

    Args:
        current_level (float): The current water level.
        target_level (float): The target water level.
        pump_times (dict): A dictionary with half-inch increments as keys and pump times as values.

    Returns:
        float: The estimated pump time in seconds.
    """
    if current_level >= target_level:
        return 0

    total_time = 0
    level = current_level

    while level < target_level:
        next_level = math.ceil(level * 10) / 10
        if next_level in time_to_reach_pump_time:
            total_time += time_to_reach_pump_time[next_level]
        else:
            raise ValueError(f"No pump time recorded for level {next_level}")
        level = next_level

    return total_time
