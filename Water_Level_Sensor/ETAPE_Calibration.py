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
    """
    Calibrates the water sensor by collecting sensor data at specified levels. If calibration data already exists,
    it skips recalibration. The function manages the pump with threading for real-time user interaction.

    Variables:
        coefficients_file (str): Path to the calibration coefficients file.
        calibration_data (list): List of (water level, sensor value) tuples.
        stop_event (threading.Event): Controls the stopping of the pump thread.
        pump_thread (threading.Thread): Manages the water pump operations.

    Returns:
        None: Writes calibration coefficients to a file or exits if coefficients are valid or errors occur.
    """

    coefficients_file = 'calibration_coefficients.txt'

    # Check if a file containing previously calculated coefficients exists
    if os.path.exists(coefficients_file):
        try:
            # Open and read the coefficients from the file
            with open(coefficients_file, 'r') as f:
                coefficients = eval(f.read())  # Using eval; consider JSON for safer parsing
            # Check if all necessary coefficients are present in the file
            if all(key in coefficients for key in ['a', 'b', 'c']):
                print("Calibration coefficients for water sensor already exist.")
                return  # Skip calibration if coefficients already exist
        except Exception as e:
            print(f"Error reading or validating coefficients: {e}")  # Handle errors during file read

    # Begin the calibration process
    print("\nStarting water sensor calibration...")
    calibration_data = []
    # Iterate through a range of target water levels from 1.5 to 6.0 inches
    for target_level in np.arange(1.5, 6.5, 0.5):
        stop_event.clear()  # Clear any previous stop signals for the pump control thread
        # Start a thread to control the pump operation asynchronously
        pump_thread = threading.Thread(target=pump_control, args=(FRESH_WATER_PUMP_PIN,))
        pump_thread.start()

        # Loop to handle user input during calibration
        while True:
            try:
                # Prompt user to confirm when water level reaches the target level
                user_input = input(
                    f"Type 'confirm {target_level}' when the water is at {target_level} inches: ").strip().lower()
                if user_input == f"confirm {target_level}":
                    stop_event.set()  # Signal the pump thread to stop pumping
                    # Wait up to 10 seconds for the pump thread to finish
                    pump_thread.join(timeout=10)
                    if pump_thread.is_alive():
                        print("Warning: Pump control thread did not terminate correctly.")
                    # Measure the average sensor value at this water level
                    average_sensor_value = get_average_sensor_value()
                    calibration_data.append((target_level, average_sensor_value))
                    print(f"Averaged sensor value at {target_level} inches: {average_sensor_value}")
                    time.sleep(5)  # Pause to stabilize water level before moving to the next
                    break
                else:
                    print("Invalid input. Please follow the format 'confirm <level>'.")
            except Exception as e:
                print(f"Unexpected error during user interaction: {e}")
                stop_event.set()  # Ensure the pump stops in case of error
                pump_thread.join(timeout=10)  # Attempt to safely terminate the thread
                if pump_thread.is_alive():
                    print("Critical error: Unable to properly stop pump control thread.")
                return  # Exit the function on critical error

        # Prepare for the next calibration point
        stop_event.set()
        if pump_thread.is_alive():
            pump_thread.join()  # Ensure the pump control thread has terminated

    # Check if enough calibration data was collected
    if len(calibration_data) < 3:
        print("Insufficient calibration data collected. Calibration requires at least 3 data points.")
        return

    # Curve fitting using collected calibration data
    try:
        levels, sensor_values = zip(*calibration_data)  # Unpack level and sensor value data
        # Fit the sensor values to a quadratic model to find calibration coefficients
        popt, _ = curve_fit(quadratic_model, sensor_values, levels)
        coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
        print(f"\nCalibration complete. Coefficients: {coefficients}\n")
        # Save the new coefficients back to the file
        save_coefficients(coefficients)
    except Exception as e:
        print(f"Error during curve fitting: {e}")  # Handle errors in curve fitting
