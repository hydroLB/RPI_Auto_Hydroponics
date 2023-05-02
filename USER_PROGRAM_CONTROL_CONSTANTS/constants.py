# Pump directions
from utilities.pumps import Pump

# What direction a pump will go in for forward, if pump was placed  in backwards direction (positive, negative on the
# pump) will most likely be -1
WATER_PUMP_DIRECTION = -1
NUTRIENT_PUMP1_DIRECTION = 1
NUTRIENT_PUMP2_DIRECTION = 1
NUTRIENT_PUMP3_DIRECTION = 1
NUTRIENT_PUMP4_DIRECTION = -1
PH_DOWN_PUMP_DIRECTION = -1
PH_UP_PUMP_DIRECTION = 1

# Pump positions (driver0/driver1)
WATER_PUMP_POSITION = 'driver0.motor4'
NUTRIENT_PUMP1_POSITION = 'driver0.motor3'
NUTRIENT_PUMP2_POSITION = 'driver1.motor3'
NUTRIENT_PUMP3_POSITION = 'driver1.motor2'
NUTRIENT_PUMP4_POSITION = 'driver1.motor1'
PH_DOWN_PUMP_POSITION = 'driver1.motor4'
PH_UP_PUMP_POSITION = 'driver0.motor1'

# Vars for 1-wire temp sensor
W1_DEVICE_PATH = '/sys/bus/w1/devices/'
W1_DEVICE_NAME = '28-3c09f6495e17'
W1_TEMP_PATH = W1_DEVICE_PATH + W1_DEVICE_NAME + '/temperature'

# I2C addresses for ECSensor and PHSensor
EC_SENSOR_I2C_ADDRESS = 100
PH_SENSOR_I2C_ADDRESS = 99

# ADC configuration
ADC_I2C_ADDRESS = 0x48
ADC_BUSNUM = 1
ADC_GAIN = 1

# Coefficients for quadratic equation to convert reading to water level (a, b, c)
QUADRATIC_COEFFICIENTS = [-0.0034, -0.0103, 0.9816]

# Motor driver I2C addresses
DRIVER0_I2C_ADDRESS = 0x60
DRIVER1_I2C_ADDRESS = 0x61

# Indicates the minimum water level for the system to recognize a completed setup
SKIP_SYSTEM_SETUP_WATER_LEVEL = 1.5

PLANTS = {

    'plant_1': {
        'ph_settings': {
            # FLOAT
            'target_min_ph': 5.8,  # MODIFY THE VALUES HERE
            # FLOAT
            'target_max_ph': 6.2,  # MODIFY THE VALUES HERE
            # FLOAT, FLOAT, int
            'dosing_time': [0.1, 0.1, 10]  # [PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME]
        },
        'nutrient_settings': {
            # INT, INT, INT, INT
            # Time in seconds for each nute pump to run
            'nutrient_pump_times': [5, 5, 5, 5],  # MODIFY THE VALUES HERE
            # Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
            # to avoid overloading the nutrients when the pH is balanced after (which always raises it to some degree).
            # INT
            'ppm_safety_margin': 30,  # MODIFY THE VALUES HERE
            # how long should the RPI wait in between dosing nutrients to reach the target PPM
            # INT
            'wait_time_loop': 10,  # MODIFY THE VALUES HERE
        },
        'water_settings': {
            # water_level_change_threshold (in inches) (acts as the plants 'dry-back' function and time between
            # checks (in seconds) wait_time_between_checks = how long should the raspberry pi wait to check the water
            # level and then if the ph is within soft range
            # FLOAT
            'level_change_threshold': 3.0,  # MODIFY THE VALUES HERE
            # INT
            # wait_time_between_checks = how long should the raspberry pi wait to
            # check the water level and then if the ph is within soft range
            'wait_time_between_checks': 1000  # MODIFY THE VALUES HERE
        }
    },

    'plant_2': {
        'ph_settings': {
            # FLOAT
            'target_min_ph': 5.8,  # MODIFY THE VALUES HERE
            # FLOAT
            'target_max_ph': 6.2,  # MODIFY THE VALUES HERE
            # FLOAT, FLOAT, int
            'dosing_time': [0.1, 0.1, 10]  # [PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME]
        },
        'nutrient_settings': {
            # INT, INT, INT, INT
            # Time in seconds for each nute pump to run
            'nutrient_pump_times': [5, 5, 5, 5],  # MODIFY THE VALUES HERE
            # Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
            # to avoid overloading the nutrients when the pH is balanced after (which always raises it to some degree).
            # INT
            'ppm_safety_margin': 30,  # MODIFY THE VALUES HERE
            # how long should the RPI wait in between dosing nutrients to reach the target PPM
            # INT
            'wait_time_loop': 10,  # MODIFY THE VALUES HERE
        },
        'water_settings': {
            # water_level_change_threshold (in inches) (acts as the plants 'dry-back' function and time between
            # checks (in seconds) wait_time_between_checks = how long should the raspberry pi wait to check the water
            # level and then if the ph is within soft range
            # FLOAT
            'level_change_threshold': 3.0,  # MODIFY THE VALUES HERE
            # INT
            # wait_time_between_checks = how long should the raspberry pi wait to
            # check the water level and then if the ph is within soft range
            'wait_time_between_checks': 1000  # MODIFY THE VALUES HERE
        }
    },
}

# position of each pump (driver0/driver1) dependent on how its setup physically

# Setup fresh water pump object using constants above
fresh_waterPump = Pump(WATER_PUMP_POSITION, WATER_PUMP_DIRECTION)
# Setup nutrient pump objects using constants above
nutrientPump1 = Pump(NUTRIENT_PUMP1_POSITION, NUTRIENT_PUMP1_DIRECTION)
nutrientPump2 = Pump(NUTRIENT_PUMP2_POSITION, NUTRIENT_PUMP2_DIRECTION)
nutrientPump3 = Pump(NUTRIENT_PUMP3_POSITION, NUTRIENT_PUMP3_POSITION)
nutrientPump4 = Pump(NUTRIENT_PUMP4_POSITION, NUTRIENT_PUMP4_POSITION)
# pH pump objects using constants above
pHDownPump = Pump(PH_DOWN_PUMP_POSITION, PH_DOWN_PUMP_POSITION)
pHUpPump = Pump(PH_UP_PUMP_POSITION, PH_UP_PUMP_POSITION)

NUTRIENT_PUMP_LIST = [nutrientPump1, nutrientPump2, nutrientPump3, nutrientPump4]  # add the nutrient pumps to the list

# List containing the pH Up and pH Down pump objects.
PH_PUMP_LIST = [pHUpPump, pHDownPump]  # add the pH pumps to the list

# Global list of all pump objects: water, nutrient, and pH pumps.
ALL_PUMPS = [fresh_waterPump] + [pump for pump in NUTRIENT_PUMP_LIST] + PH_PUMP_LIST
