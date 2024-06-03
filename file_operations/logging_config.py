# Reads and writes target_ppm and water_level to a file, which saves it in case of system restart

import logging

# Configure the logging settings here
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to write target_ppm and target_water_level to a file
def write_to_file(target_ppm, target_water_level):
    with open("settings.txt", "w") as file:
        file.write(f"{target_ppm},{target_water_level}")


# Function to read target_ppm and target_water_level from a file
def read_from_file():
    with open("settings.txt", "r") as file:
        data = file.read().split(',')
        target_ppm = int(data[0])
        target_water_level = int(data[1])

    return target_ppm, target_water_level
