import threading
from time import sleep
from WaterSensor import *
from tempAtlas import *
from pumps import *
import sys

#Prime a pump with the users help
def prime(pumpName,pump):
	print("Press enter to start priming "+ pumpName + ", then press enter to stop when liquid level reaches pump")
	sys.stdin.readline() #Wait for user to hit enter
	pump.start()
	sys.stdin.readline() #Wait for user to hit enter
	pump.stop()

def fillWater(target_level):
	while(getWaterLevel() < target_level):
		print("Adding water... level %f"%(getWaterLevel()))
		waterPump.start()
		sleep(1)
	waterPump.stop()

nutrient1Time = 2
nutrient2Time = 2
nutrient3Time = 2
nutrient4Time = 2
def doseNutrients(target_ppm):
	while(get_ppm() < target_ppm):
		print("Adding nutrients... PPM %f" % (get_ppm()))
		nutrientPump1.start()
		sleep(nutrient1Time)
		nutrientPump1.stop()
		nutrientPump2.start()
		sleep(nutrient2Time)
		nutrientPump2.stop()
		nutrientPump3.start()
		sleep(nutrient3Time)
		nutrientPump3.stop()
		nutrientPump4.start()
		sleep(nutrient4Time)
		nutrientPump4.stop()
		sleep(10)
targetPH = 5.8
minPH=5.6
maxPH = 6.2
def balancePH():
	if(get_ph() < minPH):
		while(get_ph() < targetPH):
			print("Increasing PH, PH: %f" %(get_ph()))
			pHUpPump.start()
			sleep(.1)
			pHUpPump.stop()
			sleep(10)
		pHUpPump.stop()
	elif(get_ph() > maxPH):
		while(get_ph() > targetPH):
			print("Reducing PH, PH: %f" %(get_ph()))
			pHDownPump.start()
			sleep(.1)
			pHDownPump.stop()
			sleep(10)
		pHDownPump.stop()
	
def balancePHExact():
	if(get_ph() < targetPH):
		while(get_ph() < targetPH):
			print("Increasing PH, PH: %f"%(get_ph()))
			pHUpPump.start()
			sleep(.1)
			pHUpPump.stop()
			sleep(10)
		pHUpPump.stop()
	elif(get_ph() > targetPH):
		while(get_ph() > targetPH):
			print("Reducing PH, PH: %f" %(get_ph()))
			pHDownPump.start()
			sleep(.1)
			pHDownPump.stop()
			sleep(10)
		pHDownPump.stop()

#Program startup
#Prime pumps:
print("RPI Hydroponic System Startup")
print("To start, pumps must be primed")

prime("Nutrient Pump 1", nutrientPump1)
prime("Nutrient Pump 2", nutrientPump2)
prime("Nutrient Pump 3", nutrientPump3)
prime("Nutrient Pump 4", nutrientPump4)
prime("PH Up Pump", pHUpPump)
prime("PH Down Pump", pHDownPump)

print("\n input target plant ppm value: ")
targetPPM = int(input())
print("input target water level")
targetWaterLevel = int(input())
waterThreshold = 3
fillWater(targetWaterLevel)
doseNutrients(targetPPM)
balancePHExact()
print("Startup completed")


#Update target ppm, as the PH liquid can affect ppm readings
sleep(30)
targetPPM = get_ppm()

while True:
	if (getWaterLevel() - targetWaterLevel > waterThreshold):
		preFillupPPM = get_ppm()
		fillWater(targetWaterLevel)
		sleep(30) #allows ppm readings to settle
		#Change target ppm based on plant's rate of nutrient consumption
		#the goal is to have the plant consume nutrients at the same rate that it consumes water
		#meaning that the ppm would stay constant over time
		ppmDiff = targetPPM - preFillupPPM 
		targetPPM += ppmDiff
		#Dose most of the nutrients. As the PH balancing will alter the ppm we leave a margin 
		#to prevent overshoot
		doseNutrients(targetPPM - 20)
		balancePH()
		#Now dose the remaining small proportion of nutrients
		doseNutrients(targetPPM)
	else:
		balancePH()
	sleep(10)

