
from AtlasI2C import AtlasI2C
import time

#Vars for 1wire temp sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'

ECSensor = AtlasI2C(100)
PHSensor = AtlasI2C(99)

def get_temp_c():
        temp_file = open(w1_temp_path, 'r')
        temp_c = int(temp_file.readline())/1000
        temp_file.close()
        return temp_c

def get_temp_f():
	return get_temp_c() * 9/5 + 32

def get_ph():
	return float(PHSensor.query('RT,'+str(get_temp_c())).rstrip('\0'))
def get_ec():
	return float(ECSensor.query('RT,'+str(get_temp_c())).rstrip('\0'))
def get_ppm():
	return get_ec()*.5
