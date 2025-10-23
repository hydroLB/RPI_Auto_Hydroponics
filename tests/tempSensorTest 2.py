from user_controlled_constants import W1_TEMP_PATH

while True:
    # Open the temperature file for reading
    temp_file = open(W1_TEMP_PATH, 'r')

    # Read the temperature value in Celsius
    temp_c = int(temp_file.readline()) / 1000.0

    # Close the temperature file
    temp_file.close()

    # Convert the temperature to Fahrenheit
    temp_f = temp_c * 9 / 5 + 32

    # Print the temperature values in Celsius and Fahrenheit
    print('Temp C: %f Temp F: %f' % (temp_c, temp_f))
