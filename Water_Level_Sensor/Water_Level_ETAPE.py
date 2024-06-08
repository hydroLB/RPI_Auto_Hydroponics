import json
import os

from Water_Level_Sensor.ETAPE_Calibration import quadratic_model, get_average_sensor_value

# Set the gain value for the ADC
GAIN = 1

# File to store calibration coefficients
coefficients_file = 'calibration_coefficients.txt'


def load_coefficients():
    """
    Loads the coefficients for the quadratic model from a file.

    Returns:
        dict: A dictionary of coefficients if the file is found and loaded successfully.
        None: If the file is not found or an error occurs during loading.
    """
    try:
        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, "calibration_coefficients.txt")

        # Open the file in read mode and load the coefficients
        with open(file_path, 'r') as file:
            coefficients = json.load(file)

            if not isinstance(coefficients, dict):
                raise TypeError(
                    "Expected coefficients to be a dictionary, but got type {}. Error in load_coefficients.".format(
                        type(coefficients).__name__))

            return coefficients

    except FileNotFoundError:
        print("Calibration file for water sensor not found in load_coefficients.")
        return None

    except json.JSONDecodeError as e:
        print("Error decoding JSON from calibration file: {}. Error in load_coefficients.".format(e))
        return None

    except Exception as e:
        print("An unexpected error occurred in load_coefficients: {}".format(e))
        return None


def get_water_level():
    """
    Calculates the water level using sensor data and preloaded coefficients.

    Returns:
        float: The calculated water level rounded to two decimal places.
        None: If coefficients cannot be loaded.
    """
    try:
        # Load the coefficients for the quadratic model
        coefficients = load_coefficients()
        if coefficients is None:
            return None

        # Get the average sensor value
        sensor_value = get_average_sensor_value()

        # Ensure sensor_value is a number
        if not isinstance(sensor_value, (int, float)):
            raise TypeError(
                "Expected sensor_value to be an int or float, but got type {}. Error in get_water_level.".format(
                    type(sensor_value).__name__))

        # Calculate the water level using the quadratic model
        water_level = quadratic_model(sensor_value, **coefficients)

        # Ensure water_level is a number
        if not isinstance(water_level, (int, float)):
            raise TypeError(
                "Expected water_level to be an int or float, but got type {}. Error in get_water_level.".format(
                    type(water_level).__name__))

        return float(round(water_level, 2))

    except TypeError as e:
        raise TypeError("Type error occurred in get_water_level: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in get_water_level: {}".format(e))

    except KeyError as e:
        raise KeyError("Key error occurred in get_water_level: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in get_water_level: {}".format(e))
