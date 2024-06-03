# SAVE ANOTHER PLANTS SETTINGS, TO ENSURE THIS IS USED BY THE HYDROPONICS SYSTEM, CHANGE THE NAME OF THE DICTIONARY
# IN MAIN.PY MAIN FUNCTION TO CHOOSEN PLANT VAR NAME (EX: "RASPBERRY_PLANT")
RASPBERRY_PLANT = {
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
             # Time in seconds for each nute pump to run
             # 'nutrient_pump_times' specifies the run duration in seconds for each nutrient pump. 
             # This acts as a 'ratio' selector, influencing the concentration of each nutrient solution.
             # Values represent the interval each pump is on between each ppm sensor check, not total pump operation time, 
             # which is dynamically checked using the ppm sensor.
             # Select a value between 2-5 seconds per pump for optimal dosing. Note that too short a duration may yield only a few drops.
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

# ANOTHER PLANTS SETTINGS (#2), TO ENSURE THIS IS USED BY THE HYDROPONICS SYSTEM, CHANGE THE NAME OF THE DICTIONARY
# IN MAIN.PY MAIN FUNCTION
BLUEBERRY_PLANT = {
    'plant': 
        'ph_settings': {
            # FLOAT
            'target_min_ph': 5.8,  # MODIFY THE VALUES HERE
            # FLOAT
            'target_max_ph': 6.2,  # MODIFY THE VALUES HERE
            # FLOAT, FLOAT, int
            'dosing_time': [0.1, 0.1, 10]  # [PH_UP_SLEEP_TIME, PH_DOWN_SLEEP_TIME, LOOP_SLEEP_TIME]
        },
        'nutrient_settings': {
             # Time in seconds for each nute pump to run
             # 'nutrient_pump_times' specifies the run duration in seconds for each nutrient pump. 
             # This acts as a 'ratio' selector, influencing the concentration of each nutrient solution.
             # Values represent the interval each pump is on between each ppm sensor check, not total pump operation time, 
             # which is dynamically checked using the ppm sensor.
             # Select a value between 2-5 seconds per pump for optimal dosing. Note that too short a duration may yield only a few drops.
                               # INT, INT, INT, INT
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
