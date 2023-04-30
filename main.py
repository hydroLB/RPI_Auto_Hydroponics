import threading
from time import sleep
from WaterSensor import *
from tempAtlas import *
from pumps import *
import sys
from pump_config import *


# Prime pumps with the user's help
def prime(pumps_list):
    for pump in pumps_list:
        counter = 1
        print("Press enter to start priming pump" + str(
            counter) + ", then press enter to stop when liquid level reaches the end of the pumps tubing")
        counter += 1
        sys.stdin.readline()  # Wait for user to hit enter
        pump.start()
        sys.stdin.readline()  # Wait for user to hit enter
        pump.stop()


def fillWater(target_level):
    while getWaterLevel() < target_level:
        print("Adding water... level %f" % (getWaterLevel()))
        waterPump.start()
        sleep(5)
    waterPump.stop()


def doseNutrients(target_ppm, pump_info):
    # Keep dosing nutrients until the target PPM is reached
    while get_ppm() < target_ppm:
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
        sleep(10)


def balancePH():
    if (get_ph() < minPH):
        while (get_ph() < targetPH):
            print("Increasing PH, PH: %f" % (get_ph()))
            pHUpPump.start()
            sleep(.1)
            pHUpPump.stop()
            sleep(10)
        pHUpPump.stop()
    elif (get_ph() > maxPH):
        while (get_ph() > targetPH):
            print("Reducing PH, PH: %f" % (get_ph()))
            pHDownPump.start()
            sleep(.1)
            pHDownPump.stop()
            sleep(10)
        pHDownPump.stop()


def balancePHExact():
    if (get_ph() < targetPH):
        while (get_ph() < targetPH):
            print("Increasing PH, PH: %f" % (get_ph()))
            pHUpPump.start()
            sleep(.1)
            pHUpPump.stop()
            sleep(10)
        pHUpPump.stop()
    elif (get_ph() > targetPH):
        while (get_ph() > targetPH):
            print("Reducing PH, PH: %f" % (get_ph()))
            pHDownPump.start()
            sleep(.1)
            pHDownPump.stop()
            sleep(10)
        pHDownPump.stop()


# Target pH values and limits
targetPH, minPH, maxPH = 5.8, 5.6, 6.2

# Water level change threshold (in inches) and time between checks (in seconds)
waterThreshold, wait_time_between_checks = 3, 1000

# Initialize default values
targetPPM, targetWaterLevel = 100, 4

# Program startup
if getWaterLevel() < 2.0:
    print("RPI Hydroponic System Startup\nTo start, pumps must be primed")
    prime(all_pumps)

    targetPPM = int(input("\nInput starting target plant ppm value (it will adapt): "))
    targetWaterLevel = int(input("Input target water level (in inches): "))

    fillWater(targetWaterLevel)
    doseNutrients(targetPPM, nutrient_pump_time_list)
    balancePHExact()
    print("Startup completed")

    sleep(30)  # Wait for PPM to settle
    targetPPM = get_ppm()  # Update target PPM based on plant behavior
else:
    while True:
        if getWaterLevel() - targetWaterLevel > waterThreshold:
            prefillupPPM = get_ppm()
            fillWater(targetWaterLevel)
            sleep(30)  # Wait for PPM readings to settle

            # Update target PPM based on plant's nutrient consumption rate
            targetPPM += (targetPPM - prefillupPPM)

            # Dose nutrients and balance pH
            doseNutrients(targetPPM - 20)
            balancePH()
            doseNutrients(targetPPM)
        else:
            balancePH()  # keep within range

        sleep(wait_time_between_checks)  # Wait before checking water level and pH
