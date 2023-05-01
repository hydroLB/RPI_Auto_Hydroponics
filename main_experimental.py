from time import sleep
from WaterSensor import *
from stopmotors import stop_pumps_list
from tempAtlas import *
import sys
from pump_config import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Plant:
    def __init__(self, name, target_ph, min_ph, max_ph, target_ppm, target_water_level, nutrient_pump_time_list):
        self.name = name
        self.target_ph = target_ph
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.target_ppm = target_ppm
        self.target_water_level = target_water_level
        self.nutrient_pump_time_list = nutrient_pump_time_list

# times each pump should be on
nutrient1Time = 5
nutrient2Time = 5
nutrient3Time = 5
nutrient4Time = 5

fresh_water_pump = waterPump

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




# List of pumps and their time
nutrient_pump_time_list = [(nutrientPump1, nutrient1Time), (nutrientPump2, nutrient2Time),
                           (nutrientPump3, nutrient3Time), (nutrientPump4, nutrient4Time)]



plants = [
    Plant("Plant1", 5.8, 5.6, 6.2, 800, 5, nutrient_pump_time_list),
    Plant("Plant2", 6.0, 5.8, 6.4, 900, 6, nutrient_pump_time_list),
    # Add more plants as needed
]

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 3, 1000

# Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced (which always raises it to some degree).
NUTRIENT_PPM_SAFETY_MARGIN = 30

PH_UP_SLEEP_TIME = 0.1  # Sleep time for pH up pump (how long is it on)
PH_DOWN_SLEEP_TIME = 0.1  # Sleep time for pH down pump (how long is it on)
LOOP_SLEEP_TIME = 10  # Sleep time for the loop ((how long to wait between each increment dosing)


def prime(pumps_list):
    for pump in pumps_list:
        counter = 1
        print("Press enter to start priming pump" + str(
            counter) + ", then press enter to stop when liquid level reaches the end of the pumps tubing")
        counter += 1
        sys.stdin.readline()  # Wait for user to hit enter
        pump.start()
        sys.stdin.readline()  # Wait for user to hit enter
        pump.stop()
    print("All pumps primed")


def fill_water(plant):
    try:
        while get_water_level() < plant.target_water_level:
            print("Adding water... level %f" % (get_water_level()))
            waterPump.start()
            sleep(5)
        waterPump.stop()
    except Exception as ee:
        logging.error(f"An error occurred while filling water: {ee}")
        waterPump.stop()


def dose_nutrients(target_ppm_local, pump_info):
    while get_ppm() < target_ppm_local:
        for pump, dosing_time in pump_info:
            print("Adding nutrients... PPM %f" % (get_ppm()))
            pump.start()
            sleep(dosing_time)
            pump.stop()
        sleep(10)


def balance_ph(plant):
    if get_ph() < plant.min_ph:
        while get_ph() < plant.target_ph:
            print("Increasing PH, PH: %f" % (get_ph()))
            pHUpPump.start()
            sleep(PH_UP_SLEEP_TIME)
            pHUpPump.stop()
            sleep(LOOP_SLEEP_TIME)
        pHUpPump.stop()
    elif get_ph() > plant.max_ph:
        while get_ph() > plant.target_ph:
            print("Reducing PH, PH: %f" % (get_ph()))
            pHDownPump.start()
            sleep(PH_DOWN_SLEEP_TIME)
            pHDownPump.stop()
            sleep(LOOP_SLEEP_TIME)
        pHDownPump.stop()


def balance_PH_exact(plant):
    if get_ph() < plant.target_ph:
        while get_ph() < plant.target_ph:
            print("Increasing PH, PH: %f" % (get_ph()))
            pHUpPump.start()
            sleep(PH_UP_SLEEP_TIME)
            pHUpPump.stop()
            sleep(LOOP_SLEEP_TIME)
        pHUpPump.stop()
    elif get_ph() > plant.target_ph:
        while get_ph() > plant.target_ph:
            print("Reducing PH, PH: %f" % (get_ph()))
            pHDownPump.start()
            sleep(PH_DOWN_SLEEP_TIME)
            pHDownPump.stop()
            sleep(LOOP_SLEEP_TIME)
        pHDownPump.stop()


def run_pumps_list(pumps_list, reverse=False):
    for pump in pumps_list:
        if reverse:
            pump.startReverse()
        else:
            pump.start()


def setup_hydroponic_system(plants):
    for plant in plants:
        if get_water_level() < 2.0:
            logging.info("RPI Hydroponic System Startup\nTo start, pumps must be primed")
            print("Reversing all pumps for 25 seconds")
            run_pumps_list(all_pumps, reverse=True)
            sleep(25)
            stop_pumps_list(all_pumps)
            prime(all_pumps)
            fill_water(plant)
            dose_nutrients(plant.target_ppm, plant.nutrient_pump_time_list)
            balance_PH_exact(plant)
            logging.info("Startup completed")
            sleep(30)
        else:
            logging.info("Hydroponic system already set up")


def monitor_hydroponic_system(plants):
    while True:
        try:
            for plant in plants:
                if get_water_level() - plant.target_water_level > WATER_THRESHOLD:
                    adjust_water_level_and_nutrients(plant)
                else:
                    balance_ph(plant)
            sleep(WAIT_TIME_BETWEEN_CHECKS)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            sleep(WAIT_TIME_BETWEEN_CHECKS)


def main():
    setup_hydroponic_system(plants)
    monitor_hydroponic_system(plants)

def adjust_water_level_and_nutrients(plant):
    pre_fillup_ppm = get_ppm()
    fill_water(plant)
    sleep(30)  # Wait for PPM readings to settle

    # Update target PPM based on plant's nutrient consumption rate
    plant.target_ppm += (plant.target_ppm - pre_fillup_ppm)

    # Dose nutrients, first making sure it's under the amount needed, then balance pH, increasing it,
    # then finally ensure it's exactly at the target PPM
    dose_nutrients(plant.target_ppm - NUTRIENT_PPM_SAFETY_MARGIN, plant.nutrient_pump_time_list)
    balance_PH_exact(plant)
    dose_nutrients(plant.target_ppm, plant.nutrient_pump_time_list)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")