from pump_config import PHSensor, ECSensor

# Vars for 1-wire temp sensor
w1_device_path = '/sys/bus/w1/devices/'
w1_device_name = '28-3c09f6495e17'
w1_temp_path = w1_device_path + w1_device_name + '/temperature'




def read_temp_file():
    """Read temperature file and return its content."""
    try:
        with open(w1_temp_path, 'r') as temp_file:
            return temp_file.readline()
    except FileNotFoundError:
        print("Error: Temperature file not found.")
        return None


def get_temp_c():
    """Return temperature in Celsius."""
    temp_data = read_temp_file()
    if temp_data is not None:
        return int(temp_data) / 1000
    else:
        return None


def get_temp_f():
    """Return temperature in Fahrenheit."""
    temp_c = get_temp_c()
    if temp_c is not None:
        return temp_c * 9 / 5 + 32
    else:
        return None


def get_ph():
    """Return pH value."""
    temp_c = get_temp_c()
    if temp_c is not None:
        try:
            return float(PHSensor.query('RT,' + str(temp_c)).rstrip('\0'))
        except ValueError:
            print("Error: Unable to parse pH value.")
            return None
    else:
        return None


def get_ec():
    """Return EC value."""
    temp_c = get_temp_c()
    if temp_c is not None:
        try:
            return float(ECSensor.query('RT,' + str(temp_c)).rstrip('\0'))
        except ValueError:
            print("Error: Unable to parse EC value.")
            return None
    else:
        return None


def get_ppm():
    """Return PPM value."""
    ec = get_ec()
    if ec is not None:
        return ec * 0.5
    else:
        return None
