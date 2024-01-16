from pumps import *
from adafruit_motorkit import MotorKit
from AtlasI2C import *
import RPi.GPIO as GPIO

###########################################################
# Initialize EC and pH sensors with I2C addresses
ECSensor = AtlasI2C(100)
PHSensor = AtlasI2C(99)

# Set the GPIO numbering mode
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD

# Initialize motor drivers with I2C addresses
driver0 = MotorKit(0x60)
driver1 = MotorKit(0x61)

# Initialize pump objects with corresponding motor and direction

# direction value of each (-1 or 1) is due to the direction of the peristaltic pump, in our case we had some pumps that
# were moving in the opposite direction of what we expected
# position of each pump (driver0/driver1) dependent on how its setup physically
waterPump = Pump(driver0.motor4, -1)
nutrientPump1 = Pump(driver0.motor3, 1)
nutrientPump2 = Pump(driver1.motor3, 1)
nutrientPump3 = Pump(driver1.motor2, 1)
nutrientPump4 = Pump(driver1.motor1, -1)
pHDownPump = Pump(driver1.motor4, -1)
pHUpPump = Pump(driver0.motor1, 1)

# times each pump should be on, represents the ratio of each nutrient
nutrient1Time = 5
nutrient2Time = 5
nutrient3Time = 5
nutrient4Time = 5

#   - name: A string representing the name or identifier of the plant.
#   - target_ph: The ideal pH level for the plant's water/nutrient solution.
#   - min_ph: The minimum acceptable pH level for the plant, defining the lower pH tolerance limit.
#   - max_ph: The maximum acceptable pH level for the plant, setting the upper pH tolerance limit.
#   - target_ppm: The target concentration of nutrients (measured in parts-per-million) in the water.
#   - target_water_level: The optimal water level for the plant, typically measured in inches.
# List of pumps and their time
nutrient_pump_time_list = [(nutrientPump1, nutrient1Time), (nutrientPump2, nutrient2Time),
                           (nutrientPump3, nutrient3Time), (nutrientPump4, nutrient4Time)]

class Plant:
    def __init__(self, name, target_ph, min_ph, max_ph, target_ppm, target_water_level, nutrient_pump_time_list):
        self.name = name
        self.target_ph = target_ph
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.target_ppm = target_ppm
        self.target_water_level = target_water_level
        self.nutrient_pump_time_list = nutrient_pump_time_list


plants = [
    Plant("Plant1", 5.8, 5.6, 6.2, 800, 5, nutrient_pump_time_list),
    Plant("Plant2", 6.0, 5.8, 6.4, 900, 6, nutrient_pump_time_list),
    # Add more plants as needed
]

selected_plant = plants[0]  # Select the first plant

# pin used to turn on a pump to pull fresh water in
fresh_water_pump_pin = 20

# Water level change threshold (in inches) (acts as the plants 'dry-back' function and time between checks (in seconds)
WATER_THRESHOLD, WAIT_TIME_BETWEEN_CHECKS = 3, 1000

# Margin (in ppm) between the actual target PPM and the first nutrient dosing cycle
# to avoid overloading the nutrients when the pH is finally balanced (which always raises it to some degree).
NUTRIENT_PPM_SAFETY_MARGIN = 30

PH_UP_SLEEP_TIME = 0.1  # Sleep time for pH up pump (how long is it on)
PH_DOWN_SLEEP_TIME = 0.1  # Sleep time for pH down pump (how long is it on)
LOOP_SLEEP_TIME = 10  # Sleep time for the loop ((how long to wait between each increment dosing)

############################################################################################
