import logging
import os

# Configure the logging settings here
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to write target_ppm and target_water_level to a file
def write_to_file(target_ppm, target_water_level):
    """
    Writes the target PPM and target water level to a file.

    Args:
        target_ppm (float): The target parts per million (PPM) value to be saved.
        target_water_level (float): The target water level to be saved.
    """
    try:
        # Ensure target_ppm and target_water_level are integers or floats
        if not isinstance(target_ppm, (int, float)):
            raise ValueError("target_ppm must be an integer or float")
        if not isinstance(target_water_level, (int, float)):
            raise ValueError("target_water_level must be an integer or float")

        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, "settings.txt")

        # Ensure the directory exists
        if not os.path.exists(directory):
            # Ensure the directory exists
            os.makedirs(directory, exist_ok=True)

        # Open the file in write mode and write the values separated by a comma
        with open(file_path, "w") as file:
            file.write(f"{target_ppm},{target_water_level}")

    except ValueError as e:
        raise ValueError("Value error occurred in write_to_file: {}".format(e))

    except IOError as ioe:
        # Handle I/O errors (e.g., file not found, permission issues)
        print(f"IOError in write_to_file: {ioe}")

    except Exception as e:
        raise Exception("An unexpected error occurred in write_to_file: {}".format(e))


# Function to read target_ppm and target_water_level from a file
def read_from_file():
    """
    Reads the target PPM and target water level from a file.

    Returns:
        tuple: A tuple containing the target PPM (int) and target water level (float).
    """
    try:
        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, "settings.txt")

        # Open the file in read mode and read the values
        with open(file_path, "r") as file:
            data = file.read().split(',')

            # Ensure the file has the correct number of values
            if len(data) != 2:
                raise ValueError("File does not contain exactly two values")

            # Parse the values as integers and floats
            target_ppm = int(data[0])
            target_water_level = float(data[1])

        return target_ppm, target_water_level

    except FileNotFoundError as fnfe:
        # Handle file not found errors specifically
        print(f"FileNotFoundError in read_from_file: {fnfe}")

    except ValueError as ve:
        # Handle value errors specifically (e.g., conversion issues)
        print(f"ValueError in read_from_file: {ve}")

    except IOError as ioe:
        # Handle I/O errors (e.g., file not found, permission issues)
        print(f"IOError in read_from_file: {ioe}")

    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred in read_from_file: {e}")

