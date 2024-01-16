import Adafruit_ADS1x15
import numpy as np
import json
from scipy.optimize import curve_fit
import time

# Initialize the ADC using the Adafruit_ADS1x15 library
adc = Adafruit_ADS1x15.ADS1115()

# Set the gain value for the ADC
GAIN = 1

# File to store calibration coefficients
coefficients_file = 'calibration_coefficients.txt'


def quadratic_model(x, a, b, c):
    return a * x ** 2 + b * x + c


def save_coefficients(coefficients):
    with open(coefficients_file, 'w') as file:
        json.dump(coefficients, file)


def get_average_sensor_value(num_samples=5):
    total = 0
    for _ in range(num_samples):
        total += adc.read_adc(0, gain=GAIN)
        time.sleep(0.1)  # Small delay between readings for sensor stability
    average_value = total / num_samples
    return average_value


def initialize_water_sensor():
    print("Please adjust the water to the specified levels.")
    calibration_data = []
    for target_level in np.arange(1, 8.5, 0.5):  # 1, 1.5, 2, ..., 8 inches
        while True:
            user_input = input(
                f"Type 'confirm {target_level}' when the water is at {target_level} inches: ").strip().lower()
            if user_input == f"confirm {target_level}":
                average_sensor_value = get_average_sensor_value()
                calibration_data.append((target_level, average_sensor_value))
                print(f"Averaged sensor value at {target_level} inches: {average_sensor_value}")
                break
            else:
                print("Invalid input. Please follow the format 'confirm <level>'.")
    levels, sensor_values = zip(*calibration_data)
    popt, _ = curve_fit(quadratic_model, sensor_values, levels)
    coefficients = {'a': popt[0], 'b': popt[1], 'c': popt[2]}
    print("Calibration complete.")
    save_coefficients(coefficients)
