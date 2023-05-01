from main import nutrient_pump_times
from pumps import *


fresh_water_pump = waterPump

# List of pumps and their time
nutrient_pump_time_list = [(nutrientPump1, nutrient_pump_times[0]), (nutrientPump2, nutrient_pump_times[1]),
                           (nutrientPump3, nutrient_pump_times[2]), (nutrientPump4, nutrient_pump_times[3])]

ph_pump_list = [pHUpPump, pHDownPump]

# Global list of all pumps
all_pumps = [fresh_water_pump] + [pump for pump, _ in nutrient_pump_time_list] + ph_pump_list
