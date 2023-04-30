import math
import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
GAIN = 1
print('Reading ADS1x15 Values')
def getWaterLevel():
	baseLine = adc.read_adc(1, gain=GAIN)
	rawVal = adc.read_adc(0, gain=GAIN)
	reading = rawVal/baseLine
	a = -.0034
	b = -.0103
	c = .9816-reading
	waterLevel = ((-b)-math.sqrt(b*b-4*a*c))/(2*a)
	return waterLevel
