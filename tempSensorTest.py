import os

w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'

w1_temp_path = w1_device_path + w1_device_name + '/temperature'

while True:
	temp_file = open(w1_temp_path, 'r')
	temp_c = int(temp_file.readline())/1000.0
	temp_f = temp_c * 9/5 + 32
	print('Temp C: %f Temp F: %f' % (temp_c,temp_f))

