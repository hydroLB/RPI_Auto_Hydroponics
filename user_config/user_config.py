import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit

from Atlas_and_pump_utilities.AtlasI2C import AtlasI2C
from Atlas_and_pump_utilities.pumps import Pump


class Plant:
    def __init__(self, name, target_ph, min_ph, max_ph, target_ppm, target_water_level, nutrient_pump_time_list):
        self.name = name
        self.target_ph = target_ph
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.target_ppm = target_ppm
        self.target_water_level = target_water_level
        self.nutrient_pump_time_list = nutrient_pump_time_list


###########################################################
# Initialize EC and pH sensors with I2C addresses
PHSensor = AtlasI2C(63)
ECSensor = AtlasI2C(64)

# Initialize motor drivers with I2C addresses
driver0 = MotorKit(0x60)
driver1 = MotorKit(0x61)

# ADC configuration
ADC_I2C_ADDRESS = 0x48
ADC_BUSNUM = 1
ADC_GAIN = 1

# Set the GPIO numbering mode
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD


# Initialize pump objects with corresponding motor and direction
def find_motor_name_and_direction():
    pump_names = ["nutrientPump1", "nutrientPump2", "nutrientPump3", "nutrientPump4", "BacterialPump", "pHUpPump",
                  "pHDownPump"]
    pumps = []

    motors = [
        (driver0, 3), (driver1, 3), (driver1, 2), (driver1, 1),
        (driver0, 4), (driver1, 4), (driver0, 1)
    ]

    for driver, motor_num in motors:
        motor = getattr(driver, f'motor{motor_num}')
        temp_pump = Pump(motor, 1)  # Temporary pump with default direction
        print(f"Testing motor {motor_num} on driver {driver.address}")

        temp_pump.start()
        feedback = input("Is the direction correct? (yes/no): ").strip().lower()
        temp_pump.stop()

        if feedback == 'no' or feedback == 'n':
            direction = -1
            print("Direction reversed.")
        else:
            direction = 1
            print("Direction confirmed as forward.")

        print("Choose a name for this pump from the following options:")
        for idx, name in enumerate(pump_names):
            print(f"{idx + 1}: {name}")

        name_choice = int(input("Enter the number corresponding to the chosen name: ").strip())
        chosen_name = pump_names[name_choice - 1]
        pump_names.remove(chosen_name)

        # Create a new Pump object with the correct direction and assign it to the chosen name
        new_pump = Pump(motor, direction)
        pumps.append((chosen_name, new_pump))
        print(f"Pump {chosen_name} mapped to motor {motor_num} on driver {driver.address}.")

    print("All motors have been named and tested for correct direction.")

    # Sort pumps by specified order
    order = ["nutrientPump1", "nutrientPump2", "nutrientPump3", "nutrientPump4", "BacterialPump", "pHUpPump",
             "pHDownPump"]
    sorted_pumps = sorted(pumps, key=lambda x: order.index(x[0]))

    return sorted_pumps


# Configuration function that initializes the pumps and sets up the environment
def configure_system():
    pumps = find_motor_name_and_direction()

    # Times each pump should be on, representing the ratio of each nutrient
    NUTRIENT1_TIME = 5
    NUTRIENT2_TIME = 5
    NUTRIENT3_TIME = 5
    NUTRIENT4_TIME = 5
    BACTERIAL_TIME = 5

    nutrient_pump_list = [(pump, time) for pump, time in zip([p for _, p in pumps],
                                                             [NUTRIENT1_TIME, NUTRIENT2_TIME, NUTRIENT3_TIME,
                                                              NUTRIENT4_TIME, BACTERIAL_TIME])]
    ph_pump_list = [pump for name, pump in pumps if name in ["pHUpPump", "pHDownPump"]]

    plant = Plant("Raspberry plant", 5.7, 5.6, 5.8, 800, 5, nutrient_pump_list)

    return plant, ph_pump_list


# Vars for 1-wire temp sensor receiving data
W1_DEVICE_PATH = '/sys/bus/w1/devices/'
W1_DEVICE_NAME = '28-3c09f6495e17'
W1_TEMP_PATH = W1_DEVICE_PATH + W1_DEVICE_NAME + '/temperature'

SKIP_SYSTEM_SETUP_WATER_LEVEL = 2.0

# pin used to turn on a pump to pull fresh water in
FRESH_WATER_PUMP_PIN = 20

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 2, 10000

# Margin (in ppm) between the actual target PPM in the nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced at the end (which always raises it to some degree).
PH_PPM_SAFETY_MARGIN = 50

PH_UP_SLEEP_TIME = 0.3  # Sleep time for pH up pump (how long is it on aka how much of it per cycle)
PH_DOWN_SLEEP_TIME = 0.3  # time for pH down pump (how long is it on aka how much of it per cycle)
LOOP_SLEEP_TIME = 7  # Sleep time for the loop ((how long to wait between each increment dosing)

ph_dosing_time = PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME
############################################################################################
