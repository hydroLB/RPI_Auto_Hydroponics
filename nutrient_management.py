from time import sleep
from tempAtlas import get_ppm


def dose_nutrients(target_ppm_local, pump_info, NUTRIENT_WAIT_TIME_LOOP):
    # Keep dosing nutrients until the target PPM is reached
    while get_ppm() < target_ppm_local:
        # Iterate through each pump and its corresponding dosing time in the pump_info list
        for pump, dosing_time in pump_info:
            # Print the current PPM
            print("Adding nutrients... PPM %f" % (get_ppm()))

            # Start the pump
            pump.start()

            # Sleep for the specified dosing time
            sleep(dosing_time)

            # Stop the pump
            pump.stop()

        # Sleep for 10 seconds before checking the PPM again
        sleep(NUTRIENT_WAIT_TIME_LOOP)
