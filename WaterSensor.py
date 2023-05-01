import math

from main import adc, GAIN

print('Reading ADS1x15 Values')


def get_water_level():
    """
    Calculate the water level using a liquid eTape sensor and the ADC.

    Returns:
        float: Water level value.
    """
    # Read baseline and raw eTape sensor values from the ADC
    baseline = adc.read_adc(1, gain=GAIN)
    raw_val = adc.read_adc(0, gain=GAIN)

    # Calculate the reading ratio
    reading = raw_val / baseline

    # Coefficients for quadratic equation to convert reading to water level
    a = -.0034
    b = -.0103
    c = .9816 - reading

    # Solve the quadratic equation to get the water level
    water_level = ((-b) - math.sqrt(b * b - 4 * a * c)) / (2 * a)

    return water_level
