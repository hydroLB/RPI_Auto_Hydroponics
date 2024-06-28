import os
from datetime import datetime

from ph_ppm_pump_sensor.AtlasI2C import get_ppm, get_ph, get_temp_f
from water_level_sensor.Water_Level_ETAPE import get_water_level


def log_sensor_data():
    filename = "sensor_data.log"

    # Check if file exists, if not, create it with headers
    try:
        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            with open(filename, "w") as file:
                file.write("Timestamp,Water Level,PPM,pH\n")
    except Exception as e:
        print(f"Error checking or creating the file in log_sensor_data: {e}")
        return
    try:
        # Get current time and sensor values
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        water_level = get_water_level()
        ppm = get_ppm()
        ph = get_ph()
        temperature = get_temp_f()

        # Validate sensor values
        if water_level is None or ppm is None or ph is None or temperature is None:
            print("Error in log_sensor_data: One or more sensor values could not be retrieved. "
                  "Skipping logging for this hour.")
            return

        # Append the data to the file
        with open(file_path, "a") as file:
            file.write(f"{current_time},{water_level},{ppm},{ph},{temperature}\n")

        print("Time, Water level, PPM, pH, and Temperature logged successfully.")

    except Exception as e:
        print(f"Error in log_sensor_data: logging sensor data: {e}")
