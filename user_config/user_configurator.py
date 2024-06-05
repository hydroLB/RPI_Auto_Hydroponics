import pickle
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
###########################################################

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

        for address, motor_num in motor_map:
            motor = motor_map[(address, motor_num)]

            # Ensure motor is a valid object (replace with appropriate checks if necessary)
            if motor is None:
                raise ValueError(
                    "Motor at address {} and motor number {} is invalid. "
                    "Error in find_motor_name_and_direction.".format(
                        address, motor_num))

            temp_pump = Pump(motor, 1)  # Temporary pump with default direction
            print(f"Testing motor # {motor_num} on driver with address: {hex(address)}")

            temp_pump.start()
            feedback = input("Is the direction correct, water is flowing towards bucket? (yes/no): ").strip().lower()
            temp_pump.stop()

            if feedback in ['no', 'n']:
                direction = temp_pump.direction * -1
                print("Direction reversed.")
            else:
                direction = 1
                print("Direction confirmed as forward.")

            for idx, name in enumerate(pump_names):
                print(f"{idx + 1}: {name}")

            while True:
                name_choice = input(
                    "Enter the number for selected pump name (1,2,3...) (or type 'none' for no pump): ").strip().lower()
                if name_choice == "none" or name_choice == "n":
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

            if chosen_name is not None:
                pump_objects[chosen_name] = {
                    'motor': (address, motor_num),
                    'direction': direction
                }
                print(f"Pump {chosen_name} mapped to motor {motor_num} on driver with address {hex(address)}. \n")
            else:
                print(f"No pump assigned to motor {motor_num} on driver with address {hex(address)}.")

        # Save pump objects to a file
        with open('pump_configurations.pkl', 'wb') as file:
            pickle.dump(pump_objects, file)

        print("All motors have been named and tested for correct direction.")

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

            if not isinstance(config['direction'], str):
                raise ValueError("create_pump: config['direction'] must be a string")

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
        # Check if the file exists and is readable
        with open('pump_configurations.pkl', 'rb') as file:
            pump_objects = pickle.load(file)

        # Ensure pump_objects is the correct type (assuming it should be a list or dict)
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
        # Load motor names and directions
        motor_data = load_motor_name_and_direction()

        # Ensure motor_data is a tuple and has the correct number of elements
        if not isinstance(motor_data, tuple):
            raise ValueError("Expected a tuple with 7 elements from load_motor_name_and_direction, "
                             "but got type {} with length {}. "
                             "Error in configure_system.".format(type(motor_data).__name__, len(motor_data)))

        nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump, pHUpPump, pHDownPump = motor_data

        # Set nutrient pump times
        NUTRIENT1_TIME = 5
        NUTRIENT2_TIME = 5
        NUTRIENT3_TIME = 5
        NUTRIENT4_TIME = 5
        BACTERIAL_TIME = 5

        # Create lists of pumps and their respective times
        nutrient_pump_list = [(pump, time) for pump, time in
                              zip([nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4, BacterialPump],
                                  [NUTRIENT1_TIME, NUTRIENT2_TIME, NUTRIENT3_TIME, NUTRIENT4_TIME, BACTERIAL_TIME])]

        ph_pump_list = [pHUpPump, pHDownPump]

        # Create a Plant object
        plant = Plant("Raspberry plant", 5.7, 5.6, 5.8, 800, 6, nutrient_pump_list)

        return plant, ph_pump_list

    except TypeError as e:
        raise TypeError("Type error occurred in configure_system: {}".format(e))

    except ValueError as e:
        raise ValueError("Value error occurred in configure_system: {}".format(e))

    except KeyError as e:
        raise KeyError("Key error occurred in configure_system: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in configure_system: {}".format(e))


###########################################################

# Vars for 1-wire temp sensor receiving data
W1_DEVICE_PATH = '/sys/bus/w1/devices/'
W1_DEVICE_NAME = '28-3c09f6495e17'
W1_TEMP_PATH = W1_DEVICE_PATH + W1_DEVICE_NAME + '/temperature'
###########################################################

SKIP_SYSTEM_SETUP_WATER_LEVEL = 1.5
###########################################################

# pin used to turn on a pump to pull fresh water in
FRESH_WATER_PUMP_PIN = 20
GPIO.setup(FRESH_WATER_PUMP_PIN, GPIO.OUT)  # Set pin as an output

###########################################################

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
WATER_THRESHOLD = 2
# TIME TO WAIT BETWEEN SYSTEM WATER LEVEL CHECK -> PPM ADJUST, PH CHECK
# 60 SECONDS AND 60 MINUTES = 60*60=3600 = 1 hour
WAIT_TIME_BETWEEN_CHECKS = 3600
###########################################################

# Margin (in ppm) between the actual target PPM in the nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced at the end (which always raises it to some degree).
PH_PPM_SAFETY_MARGIN = 50
PH_UP_SLEEP_TIME = 0.3  # Sleep time for pH up pump (how long is it on aka how much of it per cycle)
PH_DOWN_SLEEP_TIME = 0.3  # time for pH down pump (how long is it on aka how much of it per cycle)
LOOP_SLEEP_TIME = 7  # Sleep time for the loop ((how long to wait between each increment dosing)

ph_dosing_time = PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME
############################################################################################
