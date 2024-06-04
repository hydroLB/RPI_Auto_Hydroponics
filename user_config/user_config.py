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

# ADC configuration
ADC_I2C_ADDRESS = 0x48
ADC_BUSNUM = 1
ADC_GAIN = 1

# Set the GPIO numbering mode
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD

# Initialize motor drivers with I2C addresses
driver0 = MotorKit(address=0x60)
driver1 = MotorKit(address=0x61)

# Dictionary to map motor numbers to motor objects
motor_map = {
    (0x60, 1): driver0.motor1,
    (0x60, 2): driver0.motor2,
    (0x60, 3): driver0.motor3,
    (0x60, 4): driver0.motor4,
    (0x61, 1): driver1.motor1,
    (0x61, 2): driver1.motor2,
    (0x61, 3): driver1.motor3,
    (0x61, 4): driver1.motor4
}

# Define the motors with their respective driver addresses
motors = [
    (0x60, 3), (0x61, 3), (0x61, 2), (0x61, 1),
    (0x60, 4), (0x61, 4), (0x60, 1)
]


def find_motor_name_and_direction():
    pump_names = ["nutrientPump1", "nutrientPump2", "nutrientPump3", "nutrientPump4", "BacterialPump", "pHUpPump",
                  "pHDownPump"]
    pump_objects = {}

    for address, motor_num in motor_map:
        motor = motor_map[(address, motor_num)]
        temp_pump = Pump(motor, 1)  # Temporary pump with default direction
        print(f"Testing motor {motor_num} on driver with address {hex(address)}")

        temp_pump.start()
        feedback = input("Is the direction correct? (yes/no): ").strip().lower()
        temp_pump.stop()

        if feedback in ['no', 'n']:
            confirmation = input("Are you sure you want to reverse the direction? (yes to confirm): ").strip().lower()
            if confirmation in ['yes', 'y']:
                direction = -1
                print("Direction reversed.")
            else:
                direction = 1
                print("Direction confirmed as forward.")
        else:
            direction = 1
            print("Direction confirmed as forward.")

        for idx, name in enumerate(pump_names):
            print(f"{idx + 1}: {name}")

        while True:
            name_choice = input(
                "Enter the number for selected pump name (1,2,3...) (or type 'none' for no pump): ").strip().lower()
            if name_choice == "none":
                chosen_name = None
                break
            try:
                name_choice = int(name_choice)
                if 1 <= name_choice <= len(pump_names):
                    chosen_name = pump_names.pop(name_choice - 1)
                    break
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        if chosen_name:
            # Create a new Pump object with the correct direction and assign it to the chosen name
            new_pump = Pump(motor, direction)
            pump_objects[chosen_name] = new_pump
            print(f"Pump {chosen_name} mapped to motor {motor_num} on driver with address {hex(address)}.")
        else:
            print(f"No pump assigned to motor {motor_num} on driver with address {hex(address)}.")

    print("All motors have been named and tested for correct direction.")

    # Assign variables to each pump based on their names
    nutrientPump1 = pump_objects.get("nutrientPump1")
    nutrientPump2 = pump_objects.get("nutrientPump2")
    nutrientPump3 = pump_objects.get("nutrientPump3")
    nutrientPump4 = pump_objects.get("nutrientPump4")
    BacterialPump = pump_objects.get("BacterialPump")
    pHUpPump = pump_objects.get("pHUpPump")
    pHDownPump = pump_objects.get("pHDownPump")

    return nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump, pHUpPump, pHDownPump


# Configuration function that initializes the pumps and sets up the environment
def configure_system():
    nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump, pHUpPump, pHDownPump \
        = find_motor_name_and_direction()

    # Times each pump should be on, representing the ratio of each nutrient
    NUTRIENT1_TIME = 5
    NUTRIENT2_TIME = 5
    NUTRIENT3_TIME = 5
    NUTRIENT4_TIME = 5
    BACTERIAL_TIME = 5

    nutrient_pump_list = [(pump, time) for pump, time in
                          zip([nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump],
                              [NUTRIENT1_TIME, NUTRIENT2_TIME, NUTRIENT3_TIME,
                               NUTRIENT4_TIME, BACTERIAL_TIME])]
    ph_pump_list = [pHUpPump, pHDownPump]

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
