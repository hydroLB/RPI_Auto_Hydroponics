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
    """Quadratic model for curve fitting."""
    return a * x ** 2 + b * x + c


def save_coefficients(coefficients):
    # File to store calibration coefficients
    coefficients_file = 'calibration_coefficients.txt'
    """Save calibration coefficients to a file."""
    try:
        with open(coefficients_file, 'w') as file:
            json.dump(coefficients, file)
        print(f"Calibration coefficients saved to {coefficients_file}")
    except IOError as e:
        print(f"Error saving calibration coefficients: {e}")
        raise


def get_average_sensor_value(num_samples=5):
    """Get the RAW average sensor value over a number of samples."""
    total = 0
    for i in range(num_samples):
        try:
            # Read baseline and raw eTape sensor values from the ADC
            baseline = adc.read_adc(1, gain=GAIN)
            raw_val = adc.read_adc(0, gain=GAIN)
            print(f"Sample {i + 1}: Baseline = {baseline}, Raw value = {raw_val}")

            if baseline == 0:
                raise ValueError("Baseline reading is zero, which can lead to division by zero.")

            # Calculate the reading ratio
            reading = raw_val / baseline
            total += reading
            time.sleep(0.1)  # Small delay between readings for sensor stability
        except Exception as e:
            print(f"Error reading sensor values: {e}")
            raise
    average_value = total / num_samples
    print(f"Average sensor value: {average_value}")
    return average_value


def initialize_water_sensor():
    # File to store calibration coefficients
    coefficients_file = 'calibration_coefficients.txt'
    """Calibrate the water sensor."""
    print("Starting water sensor calibration...")

    # Enhanced directory writability check
    try:
        dir_name = os.path.dirname(coefficients_file)
        if dir_name and not os.access(dir_name, os.W_OK):
            print(f"Warning: Directory {dir_name} is not writable.")
            return
    except Exception as e:
        print(f"Error checking directory write access: {e}")
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
                    print(f"Error during calibration at {target_level} inches: {e}")
                    return
                break
            else:
                print("Invalid input. Please follow the format 'confirm <level>'.")
                print(f"Example: Type 'confirm {target_level}' to confirm the water level.")

    if len(calibration_data) < 3:
        print("Insufficient calibration data collected. Calibration requires at least 3 data points.")
        return

    levels, sensor_values = zip(*calibration_data)

    # Perform curve fitting
    try:
        popt, popv = curve_fit(quadratic_model, sensor_values, levels)
        print("Curve fitting successful.")
    except Exception as e:
        print(f"Error during curve fitting: {e}")
        return

    coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
    print(f"Calibration complete. Coefficients: {coefficients}")

    try:
        save_coefficients(coefficients)
    except Exception as e:
        print(f"Error saving coefficients: {e}")
