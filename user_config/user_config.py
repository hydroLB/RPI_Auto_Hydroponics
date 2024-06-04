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

# Pump positions (driver0/driver1, etc. on the raspberry pi)
NUTRIENT_PUMP1_POSITION = driver0.motor3
NUTRIENT_PUMP2_POSITION = driver1.motor3
NUTRIENT_PUMP3_POSITION = driver1.motor2
NUTRIENT_PUMP4_POSITION = driver1.motor1
BACTERIAL_PUMP_POSITION = driver0.motor4
PH_DOWN_PUMP_POSITION = driver1.motor4
PH_UP_PUMP_POSITION = driver0.motor1


# Vars for 1-wire temp sensor receiving data
W1_DEVICE_PATH = '/sys/bus/w1/devices/'
W1_DEVICE_NAME = '28-3c09f6495e17'
W1_TEMP_PATH = W1_DEVICE_PATH + W1_DEVICE_NAME + '/temperature'

SKIP_SYSTEM_SETUP_WATER_LEVEL = 2.0

# direction value of each (-1 or 1) is due to the direction of the peristaltic pump, in our case we had some pumps that
# were moving in the opposite direction of what we expected
# position of each pump (driver0/driver1) dependent on how its setup physically
nutrientPump1 = Pump(NUTRIENT_PUMP1_POSITION, 1)
nutrientPump2 = Pump(NUTRIENT_PUMP2_POSITION, 1)
nutrientPump3 = Pump(NUTRIENT_PUMP3_POSITION, 1)
nutrientPump4 = Pump(NUTRIENT_PUMP4_POSITION, -1)

BacterialPump = Pump(BACTERIAL_PUMP_POSITION, 1)

pHDownPump = Pump(PH_DOWN_PUMP_POSITION, -1)
pHUpPump = Pump(PH_UP_PUMP_POSITION, 1)

# times each pump should be on, represents the ratio of each nutrient
NUTRIENT1_TIME = 5
NUTRIENT2_TIME = 5
NUTRIENT3_TIME = 5
NUTRIENT4_TIME = 5

BACTERIAL_TIME = 5

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

nutrient_pump_list = [(nutrientPump1, NUTRIENT1_TIME), (nutrientPump2, NUTRIENT2_TIME),
                      (nutrientPump3, NUTRIENT3_TIME), (nutrientPump4, NUTRIENT4_TIME), (BacterialPump, BACTERIAL_TIME)]

#   - name: A string representing the name or identifier of the plant.
#   - target_ph: The ideal pH level for the plant's water/nutrient solution.
#   - min_ph: The minimum acceptable pH level for the plant, defining the lower pH tolerance limit.
#   - max_ph: The maximum acceptable pH level for the plant, setting the upper pH tolerance limit.
#   - target_ppm: The target concentration of nutrients (measured in parts-per-million) in the water.
#   - target_water_level: The optimal water level for the plant, typically measured in inches.
# List of pumps and their time
plants = [
    Plant("Raspberry plant", 5.7, 5.6, 5.8, 800, 5, nutrient_pump_list),
    # Plant("Plant2", 6.0, 5.8, 6.4, 900, 6, nutrient_pump_time_list),
    # Add more plants as needed
]

plant = plants[0]  # Select a plant

############################################################################################
