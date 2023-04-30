from pumps import *

# times each pump should be on
nutrient1Time = 5
nutrient2Time = 5
nutrient3Time = 5
nutrient4Time = 5

fresh_water_pump = waterPump

# List of pumps and their time
nutrient_pump_time_list = [(nutrientPump1, nutrient1Time), (nutrientPump2, nutrient2Time),
                           (nutrientPump3, nutrient3Time), (nutrientPump4, nutrient4Time)]

ph_pump_list = [pHUpPump, pHDownPump]

# Global list of all pumps
all_pumps = [fresh_water_pump] + [pump for pump, _ in nutrient_pump_time_list] + ph_pump_list
