import os
from datetime import datetime

from Atlas_and_pump_utilities.AtlasI2C import get_ppm, get_ph
from Water_Level_Sensor.Water_Level_ETAPE import get_water_level


def log_sensor_data():
    filename = "sensor_data.log"

    # Check if file exists, if not, create it with headers
    try:
        if not os.path.exists(filename):
            with open(filename, "w") as file:
                file.write("Timestamp,Water Level,PPM,pH\n")
    except Exception as e:
        print(f"Error checking or creating the file: {e}")
        return

    try:
        # Get current time and sensor values
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        water_level = get_water_level()
        ppm = get_ppm()
        ph = get_ph()

        # Validate sensor values
        if water_level is None or ppm is None or ph is None:
            print("Error: One or more sensor values could not be retrieved. Skipping logging for this hour.")
            return

        # Append the data to the file
        with open(filename, "a") as file:
            file.write(f"{current_time},{water_level},{ppm},{ph}\n")

        print("Time, Water level, PPM, and pH logged successfully.")

    except Exception as e:
        print(f"Error logging sensor data: {e}")
