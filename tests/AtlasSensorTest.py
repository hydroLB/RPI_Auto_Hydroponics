from utilities.AtlasI2C import AtlasI2C
import time

# Initialize EC and pH sensors with I2C addresses
ECSensor = AtlasI2C(100)
PHSensor = AtlasI2C(99)

# Variables for 1-wire temperature sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'


def get_temp_c():
    """
    Read the temperature from the 1-wire sensor in Celsius.

    Returns:
        float: Temperature in Celsius.
    """
    temp_file = open(w1_temp_path, 'r')
    temp_c = int(temp_file.readline()) / 1000
    temp_file.close()
    return temp_c


while True:
    # Get temperature in Celsius and Fahrenheit
    temp_c_2 = get_temp_c()
    temp_f = temp_c_2 * 9 / 5 + 32

    # Get EC value with temperature compensation
    ec = ECSensor.query('RT,' + str(get_temp_c()))
    ppm = float(ec.rstrip('\0')) * .49

    # Get pH value with temperature compensation
    ph = PHSensor.query('RT,' + str(get_temp_c()))

    # Print temperature, PPM, and pH values
    print('Temp: %s PPM: %f PH: %s' % (temp_f, ppm, ph))

    # Wait for 1 second before the next iteration
    time.sleep(1)
