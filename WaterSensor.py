import math
import time
import Adafruit_ADS1x15

# Initialize the ADC (Analog-to-Digital Converter) with I2C address and bus number
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

# Set the gain value for the ADC
GAIN = 1

print('Reading ADS1x15 Values')


def get_water_level():
    """
    Calculate the water level using a liquid eTape sensor and the ADC.

    Returns:
        float: Water level value.
    """
    # Read baseline and raw eTape sensor values from the ADC
    baseLine = adc.read_adc(1, gain=GAIN)
    rawVal = adc.read_adc(0, gain=GAIN)

    # Calculate the reading ratio
    reading = rawVal / baseLine

    # Coefficients for quadratic equation to convert reading to water level
    a = -.0034
    b = -.0103
    c = .9816 - reading

    # Solve the quadratic equation to get the water level
    waterLevel = ((-b) - math.sqrt(b * b - 4 * a * c)) / (2 * a)

    return waterLevel
