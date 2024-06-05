import logging

# Configure the logging settings here
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to write target_ppm and target_water_level to a file
def write_to_file(target_ppm, target_water_level):
    """
    Writes the target PPM and target water level to a file.

    Args:
        target_ppm (int): The target parts per million (PPM) value to be saved.
        target_water_level (int): The target water level to be saved.
    """
    # Open the file in write mode and write the values separated by a comma
    with open("settings.txt", "w") as file:
        file.write(f"{target_ppm},{target_water_level}")


# Function to read target_ppm and target_water_level from a file
def read_from_file():
    """
    Reads the target PPM and target water level from a file.

    Returns:
        tuple: A tuple containing the target PPM (int) and target water level (int).
    """
    # Open the file in read mode and read the values
    with open("settings.txt", "r") as file:
        data = file.read().split(',')
        # Parse the values as integers
        target_ppm = int(data[0])
        target_water_level = int(data[1])

    return target_ppm, target_water_level
