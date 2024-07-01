import os
import pickle
from time import sleep

import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit

from ph_ppm_pump_sensor.AtlasI2C import AtlasI2C
from ph_ppm_pump_sensor.pumps import Pump, prime, clear_lines
from file_operations.clear_terminal import clear_terminal
from file_operations.logging_water_and_ppm import read_from_file


########################################################################################################################

class Plant:
    def __init__(self, name, target_ph, min_ph, max_ph, target_ppm, target_water_level, nutrient_pump_time_list):
        self.name = name
        self.target_ph = target_ph
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.target_ppm = target_ppm
        self.target_water_level = target_water_level
        self.nutrient_pump_time_list = nutrient_pump_time_list


########################################################################################################################

# Initialize EC and pH sensors with I2C addresses
PHSensor = AtlasI2C(address=99)  # Initialize the pH sensor with the specified I2C address
ECSensor = AtlasI2C(address=100)  # Initialize the EC sensor with the specified I2C address

# ADC configuration
ADC_I2C_ADDRESS = 0x48
ADC_BUSNUM = 1
ADC_GAIN = 1

# Set the GPIO numbering mode
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD

########################################################################################################################

# Vars for 1-wire temp sensor receiving data
W1_DEVICE_PATH = '/sys/bus/w1/devices/'
W1_DEVICE_NAME = '28-3c09f6495e17'
W1_TEMP_PATH = W1_DEVICE_PATH + W1_DEVICE_NAME + '/temperature'

########################################################################################################################

SKIP_SYSTEM_SETUP_WATER_LEVEL = 1.5

########################################################################################################################

# pin used to turn on a pump to pull fresh water in
FRESH_WATER_PUMP_PIN = 21
GPIO.setup(FRESH_WATER_PUMP_PIN, GPIO.OUT)  # Set pin as an output
# how long is the pump on at a time, this is to control how much water comes out at a time to not overwhelm speed of
# the etape capturing the change
fresh_water_pump_time_on = 1.5

# how long is the pump off at a time
fresh_water_pump_time_off = 3.5

########################################################################################################################

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
# Example: Bucket will be filled to 6 inches, threshold is 2, so at 4 inches, the bucket will refill
WATER_THRESHOLD = 2
# TIME TO WAIT BETWEEN SYSTEM WATER LEVEL CHECK -> PPM ADJUST, PH CHECK
# 60 SECONDS AND 60 MINUTES = 60*60=3600 = 1 hour
WAIT_TIME_BETWEEN_CHECKS = 3600

########################################################################################################################

# How long system waits between each dosing (all nute pumps cycle on/off) until target amount of nutrients is reached
PPM_LOOP_SLEEP_TIME = 30

########################################################################################################################

# Margin (in ppm) between the actual target PPM in the nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced at the end (which always raises it to some degree).
PH_PPM_SAFETY_MARGIN = 50
PH_UP_SLEEP_TIME = 8  # Sleep time for pH up pump (how long is it on aka how much of it per cycle)
PH_DOWN_SLEEP_TIME = 8  # time for pH down pump (how long is it on aka how much of it per cycle)
LOOP_SLEEP_TIME = 30  # Sleep time for the loop ((how long to wait between each increment dosing)

ph_dosing_time = PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME

########################################################################################################################

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


########################################################################################################################

def find_motor_name_and_direction():
    try:
        # Ensure motor_map is defined and is a dictionary
        if not isinstance(motor_map, dict):
            raise TypeError(
                "Expected motor_map to be a dictionary, but got type {}. "
                "Error in find_motor_name_and_direction.".format(
                    type(motor_map).__name__))

        pump_names = ["nutrientPump1", "nutrientPump2", "nutrientPump3", "nutrientPump4", "BacterialPump", "pHUpPump",
                      "pHDownPump"]
        pump_objects = {}

        # Ask user if they want to clear lines and reverse pumps or skip
        user_choice = input("Do you want to clear lines and reverse pumps or skip this step? (enter 'yes' to clear "
                            "lines or no to skip: ").strip().lower()

        if user_choice not in ['yes', 'no']:
            print("Invalid choice. Defaulting to 'yes'.")
            user_choice = 'yes'

        if user_choice == 'yes':
            print("Grab a glass to grab any fluid that comes out of pump before it reaches the bucket .")

        sleep(1)

        clear_terminal()

        for address, motor_num in motor_map:
            motor = motor_map[(address, motor_num)]
            if motor is None:
                raise ValueError(
                    "Motor at address {} and motor number {} is invalid. "
                    "Error in find_motor_name_and_direction.".format(
                        address, motor_num))

            temp_pump = Pump(motor, 1)  # Temporary pump with default direction
            print(f"\n\nTesting motor # {motor_num} on driver with address: {hex(address)}")
            sleep(1)

            temp_pump.start()
            sleep(1)
            feedback = input("Is the direction correct, liquid is flowing towards bucket? (yes/no): ").strip().lower()
            temp_pump.stop()
            sleep(2)

            if feedback in ['no', 'n']:
                direction = temp_pump.direction * -1
                print("\n Direction reversed. \n")
            else:
                direction = 1
                print("\nDirection confirmed as forward.\n")

            for idx, name in enumerate(pump_names):
                print(f"{idx + 1}: {name}")

                while True:
                    name_choice = input(
                        "\nEnter the number or name for the selected pump (1,2,3... or pump name) (or 'none' for no "
                        "pump): ").strip().lower()
                    if name_choice == "none" or name_choice == "n":
                        chosen_name = None
                        break
                    try:
                        # Check if input is a number
                        name_choice_num = int(name_choice)
                        if 1 <= name_choice_num <= len(pump_names):
                            chosen_name = pump_names.pop(name_choice_num - 1)
                            break
                        else:
                            print("Invalid choice. Please enter a number from the list.")
                    except ValueError:
                        # Check if input is a valid pump name
                        if name_choice in [name.lower() for name in pump_names]:
                            chosen_name = next(name for name in pump_names if name.lower() == name_choice)
                            pump_names.remove(chosen_name)
                            break
                        else:
                            print("Invalid input. Please enter a valid pump name or number.")

                if chosen_name is not None:
                    pump_objects[chosen_name] = {
                        'motor': (address, motor_num),
                        'direction': direction
                    }
                    print(f"Pump {chosen_name} mapped to motor {motor_num} on driver with address {hex(address)}.\n")

                    if user_choice == 'yes':
                        clear_lines(Pump(motor, direction))

                        # Prime the pump to fill it completely
                        prime(Pump(motor, direction))

                else:
                    print(f"No pump assigned to motor {motor_num} on driver with address {hex(address)}.")

                clear_terminal()

        try:
            # Define the directory and file path
            directory = "created_saved_values"
            file_path = os.path.join(directory, "pump_configurations.pkl")

            # Ensure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Open the file in write binary mode and save the pump objects
            with open(file_path, 'wb') as file:
                pickle.dump(pump_objects, file)

        except IOError as ioe:
            print(f"IOError in save_pump_objects: {ioe}")

        except Exception as e:
            print(f"An unexpected error occurred in save_pump_objects: {e}")

        print("\n All motors have been named, tested for correct direction, reversed, and primed \n ")
        clear_terminal()

        # Assign variables to each pump based on their names
        return assign_pumps(pump_objects)

    except TypeError as e:
        raise TypeError("Type error occurred in find_motor_name_and_direction: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in find_motor_name_and_direction: {}".format(e))

    except KeyError as e:
        raise KeyError("Key error occurred in find_motor_name_and_direction: {}".format(e))

    except (IOError, OSError) as e:
        raise IOError("I/O error occurred in find_motor_name_and_direction: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in find_motor_name_and_direction: {}".format(e))


def assign_pumps(pump_objects):
    try:
        # Ensure pump_objects is a dictionary
        if not isinstance(pump_objects, dict):
            raise TypeError("Expected pump_objects to be a dictionary, but got type {}. Error in assign_pumps.".format(
                type(pump_objects).__name__))

        # List of expected pump keys
        expected_keys = ["nutrientPump1", "nutrientPump2", "nutrientPump3", "nutrientPump4", "BacterialPump",
                         "pHUpPump", "pHDownPump"]

        # Check for missing keys
        for key in expected_keys:
            if key not in pump_objects:
                raise KeyError("Missing key '{}' in pump_objects. Error in assign_pumps.".format(key))

        # Create pump objects
        nutrientPump1 = create_pump(pump_objects.get("nutrientPump1"))
        nutrientPump2 = create_pump(pump_objects.get("nutrientPump2"))
        nutrientPump3 = create_pump(pump_objects.get("nutrientPump3"))
        nutrientPump4 = create_pump(pump_objects.get("nutrientPump4"))
        BacterialPump = create_pump(pump_objects.get("BacterialPump"))
        pHUpPump = create_pump(pump_objects.get("pHUpPump"))
        pHDownPump = create_pump(pump_objects.get("pHDownPump"))

        return nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump, pHUpPump, pHDownPump

    except TypeError as e:
        raise TypeError("Type error occurred in assign_pumps: {}".format(e))

    except KeyError as e:
        raise KeyError("Key error occurred in assign_pumps: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in assign_pumps: {}".format(e))


def create_pump(config):
    """
    Creates a Pump object based on the provided configuration.

    Args:
        config (dict): A dictionary containing the motor configuration.

    Returns:
        Pump: A Pump object configured with the specified motor and direction, or None if config is None.

    Raises:
        KeyError: If required keys are missing in the config dictionary.
        TypeError: If config is not a dictionary or if values have incorrect types.
        ValueError: If values in the config dictionary are not valid.
    """
    try:
        if config:
            if not isinstance(config, dict):
                raise TypeError("create_pump: config must be a dictionary")

            if 'motor' not in config or 'direction' not in config:
                raise KeyError("create_pump: config dictionary must contain 'motor' and 'direction' keys")

            if not isinstance(config['motor'], (list, tuple)) or len(config['motor']) != 2:
                raise ValueError("create_pump: config['motor'] must be a list or tuple with two elements")

            address, motor_num = config['motor']
            direction = config['direction']

            if not isinstance(address, int) or not isinstance(motor_num, int):
                raise ValueError("create_pump: config['motor'] elements must be integers")

            if (address, motor_num) not in motor_map:
                raise ValueError(
                    f"create_pump: Motor with address {address} and motor_num {motor_num} not found in motor_map")

            motor = motor_map[(address, motor_num)]
            return Pump(motor, direction)

        return None

    except KeyError as ke:
        # Handle missing key errors specifically
        print(f"KeyError in create_pump: {ke}")

    except TypeError as te:
        # Handle type errors specifically
        print(f"TypeError in create_pump: {te}")

    except ValueError as ve:
        # Handle value errors specifically
        print(f"ValueError in create_pump: {ve}")

    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred in create_pump: {e}")


def load_motor_name_and_direction():
    try:
        # Define the directory and file path
        directory = "created_saved_values"
        file_path = os.path.join(directory, "pump_configurations.pkl")

        # Open the file in read binary mode and load the pump objects
        with open(file_path, 'rb') as file:
            pump_objects = pickle.load(file)

        # Ensure pump_objects is the correct type
        if not isinstance(pump_objects, (list, dict)):
            raise TypeError(
                "Expected pump_objects to be a list or dict, but got type {}. "
                "Error in load_motor_name_and_direction.".format(
                    type(pump_objects).__name__))

        return assign_pumps(pump_objects)

    except FileNotFoundError:
        return find_motor_name_and_direction()

    except (IOError, OSError) as e:
        raise IOError("I/O error occurred in load_motor_name_and_direction: {}".format(e))

    except pickle.UnpicklingError:
        raise pickle.UnpicklingError("Unpickling error occurred in load_motor_name_and_direction.")

    except Exception as e:
        raise Exception("An unexpected error occurred in load_motor_name_and_direction: {}".format(e))


def configure_system():
    try:
########################################################################################################################
        # Configuration Section
        # User can modify these values directly
        PLANT_NAME = "Raspberry plant"
        PH_TARGET = 5.7
        PH_MIN = 5.6
        PH_MAX = 5.8
        DEFAULT_TARGET_PPM = 800
        DEFAULT_TARGET_WATER_LEVEL = 5.6
        NUTRIENT1_TIME = 10
        NUTRIENT2_TIME = 10
        NUTRIENT3_TIME = 10
        NUTRIENT4_TIME = 10
        BACTERIAL_TIME = 10

########################################################################################################################

        # Load motor names and directions
        motor_data = load_motor_name_and_direction()

        # Ensure motor_data is a tuple and has the correct number of elements
        if not isinstance(motor_data, tuple):
            raise ValueError("Expected a tuple with 7 elements from load_motor_name_and_direction, "
                             "but got type {} with length {}. "
                             "Error in configure_system.".format(type(motor_data).__name__, len(motor_data)))

        nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump, pHUpPump, pHDownPump = motor_data

        # Create lists of pumps and their respective times
        nutrient_pump_list = [(pump, time) for pump, time in
                              zip([nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump],
                                  [NUTRIENT1_TIME, NUTRIENT2_TIME, NUTRIENT3_TIME, NUTRIENT4_TIME, BACTERIAL_TIME])]

        ph_pump_list = [pHUpPump, pHDownPump]

        # Read target_ppm and target_water_level from file
        try:
            target_ppm, target_water_level = read_from_file()
            if target_ppm is None:
                target_ppm = DEFAULT_TARGET_PPM
            if target_water_level is None:
                target_water_level = DEFAULT_TARGET_WATER_LEVEL
        except Exception:
            target_ppm = DEFAULT_TARGET_PPM
            target_water_level = DEFAULT_TARGET_WATER_LEVEL

        # Create a Plant object
        plant = Plant(PLANT_NAME, PH_TARGET, PH_MIN, PH_MAX, target_ppm, target_water_level, nutrient_pump_list)

        return plant, ph_pump_list

    except TypeError as e:
        raise TypeError("Type error occurred in configure_system: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in configure_system: {}".format(e))

    except KeyError as e:
        raise KeyError("Key error occurred in configure_system: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in configure_system: {}".format(e))
