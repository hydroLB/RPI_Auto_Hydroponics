import json
from Water_Level_Sensor.watersensor_calibration import quadratic_model, get_average_sensor_value

# Set the gain value for the ADC
GAIN = 1

# File to store calibration coefficients
coefficients_file = 'calibration_coefficients.txt'


def load_coefficients():
    try:
        with open(coefficients_file, 'r') as file:
            coefficients = json.load(file)
            return coefficients
    except FileNotFoundError:
        print("Calibration file for water sensor not found.")
        return None


def get_water_level():
    # Main execution
    coefficients = load_coefficients()
    if coefficients is None:
        return None

    sensor_value = get_average_sensor_value()
    water_level = quadratic_model(sensor_value, **coefficients)
    return round(water_level, 2)
