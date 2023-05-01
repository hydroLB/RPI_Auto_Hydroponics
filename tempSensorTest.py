# Variables for 1-wire temperature sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'

while True:
    # Open the temperature file for reading
    temp_file = open(w1_temp_path, 'r')

    # Read the temperature value in Celsius
    temp_c = int(temp_file.readline()) / 1000.0

    # Close the temperature file
    temp_file.close()

    # Convert the temperature to Fahrenheit
    temp_f = temp_c * 9 / 5 + 32

    # Print the temperature values in Celsius and Fahrenheit
    print('Temp C: %f Temp F: %f' % (temp_c, temp_f))
