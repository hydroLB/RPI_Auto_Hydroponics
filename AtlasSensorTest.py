from AtlasI2C import AtlasI2C
import time

ECSensor = AtlasI2C(100)
PHSensor = AtlasI2C(99)

#Vars for 1wire temp sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'


def get_temp_c():
	temp_file = open(w1_temp_path, 'r')
	temp_c = int(temp_file.readline())/1000
	temp_file.close()
	return temp_c



while True:
	temp_c = get_temp_c()
	temp_f = temp_c * 9/5 + 32
	ec = ECSensor.query('RT,'+ str(get_temp_c()))
	ppm  = float(ec.rstrip('\0'))*.49
	ph = PHSensor.query('RT,'+ str(get_temp_c()))
	print('Temp: %s PPM: %f PH: %s' %(temp_f,ppm,ph))
	time.sleep(1)

