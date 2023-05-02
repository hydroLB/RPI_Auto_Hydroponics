# Function to write target_ppm, target_water_level, current_ppm, and current_water_level to a file
def write_to_file(filename, target_ppm, target_water_level, current_ppm, current_water_level):
    with open(filename, "w") as file:
        file.write(f"{target_ppm},{target_water_level},{current_ppm},{current_water_level}")


# Function to read target_ppm, target_water_level, current_ppm, and current_water_level from a file
def read_from_file(filename):
    with open(filename, "r") as file:
        data = file.read().split(',')
        target_ppm = int(data[0])
        target_water_level = int(data[1])
        current_ppm = int(data[2])
        current_water_level = int(data[3])

    return target_ppm, target_water_level, current_ppm, current_water_level
