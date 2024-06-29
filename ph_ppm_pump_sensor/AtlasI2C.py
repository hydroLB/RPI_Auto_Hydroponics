#!/usr/bin/python

import io
import sys
import fcntl
import time
import copy

from ph_ppm_pump_sensor.pumps import start_fresh_water_pump, end_fresh_water_pump
from file_operations.clear_terminal import clear_terminal


def read_temp_file():
    from user_config.user_configurator import W1_TEMP_PATH  # Import the temperature file path
    """Read temperature file and return its content."""
    try:
        # Attempt to open the temperature file in read mode
        with open(W1_TEMP_PATH, 'r') as temp_file:
            first_line = temp_file.readline().strip()  # Read the first line and strip any leading/trailing whitespace

            if not first_line:
                # If the first line is empty, try to read the next line
                return temp_file.readline().strip()
            else:
                # If the first line is not empty, return it
                return first_line

    except FileNotFoundError:
        # Handle the case where the temperature file is not found
        print("Error: Temperature file not found in read_temp_file.")
        return None

    except PermissionError:
        # Handle the case where there are permission issues accessing the file
        print("Error: Permission denied when accessing the temperature file in read_temp_file.")
        return None

    except IOError as e:
        # Handle any other I/O errors that may occur
        print(f"IOError occurred: {e}")
        return None

    except Exception as e:
        # Handle any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        return None


def get_temp_c():
    """Return temperature in Celsius."""
    attempts = 5  # Number of attempts to read the temperature data

    for attempt in range(attempts):
        try:
            temp_data = read_temp_file()  # Read the temperature data from the file

            if temp_data is not None:
                try:
                    # Convert the temperature data to Celsius
                    return int(temp_data) / 1000

                except ValueError as e:
                    # Handle the case where the temperature data cannot be converted to an integer
                    print(f"ValueError occurred: {e}")
                    return None

                except TypeError as e:
                    # Handle the case where the temperature data is of an unexpected type
                    print(f"TypeError occurred: {e}")
                    return None

            else:
                # If the temperature reading fails, wait for 1 second before retrying
                time.sleep(1)

        except IOError as e:
            # Handle any I/O errors that occur while reading the temperature file
            print(f"IOError occurred: {e}")
            return None

        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
            return None

    # If all attempts fail to get a valid temperature value, print a warning message
    print("Warning: Failed to read temperature data after 5 attempts.")
    return None


def get_temp_f():
    """Return temperature in Fahrenheit."""
    temp_c = get_temp_c()  # Get the temperature in Celsius

    if temp_c is not None:
        try:
            # Convert the temperature from Celsius to Fahrenheit
            return temp_c * 9 / 5 + 32

        except TypeError as e:
            # Handle the case where the temperature data is not a number
            print(f"TypeError occurred: {e}")
            return None

        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
            return None

    else:
        # If the temperature reading in Celsius fails, return None
        return None


########################################
class AtlasI2C:
    # the timeout needed to query readings and calibrations
    LONG_TIMEOUT = 1.5
    # timeout for regular commands
    SHORT_TIMEOUT = .3
    # the default bus for I2C on the newer Raspberry Pis,
    # certain older boards use bus 0
    DEFAULT_BUS = 1
    # the default address for the sensor
    DEFAULT_ADDRESS = 98
    LONG_TIMEOUT_COMMANDS = ("R", "CAL")
    SLEEP_COMMANDS = ("SLEEP",)

    def __init__(self, address=None, moduletype="", name="", bus=None):
        """
        open two file streams, one for reading and one for writing
        the specific I2C channel is selected with bus
        it is usually 1, except for older revisions where its 0
        wb and rb indicate binary read and write
        """
        self._address = address or self.DEFAULT_ADDRESS
        self.bus = bus or self.DEFAULT_BUS
        self._long_timeout = self.LONG_TIMEOUT
        self._short_timeout = self.SHORT_TIMEOUT
        self.file_read = io.open(file="/dev/i2c-{}".format(self.bus),
                                 mode="rb",
                                 buffering=0)
        self.file_write = io.open(file="/dev/i2c-{}".format(self.bus),
                                  mode="wb",
                                  buffering=0)
        self.set_i2c_address(self._address)
        self._name = name
        self._module = moduletype

    @property
    def long_timeout(self):
        return self._long_timeout

    @property
    def short_timeout(self):
        return self._short_timeout

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address

    @property
    def moduletype(self):
        return self._module

    def set_i2c_address(self, addr):
        """
        set the I2C communications to the slave specified by the address
        the commands for I2C dev using the ioctl functions are specified in
        the i2c-dev.h file from i2c-tools
        """
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self._address = addr

    def write(self, cmd):
        """
        appends the null character and sends the string over I2C
        """
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    def handle_raspi_glitch(self, response):

        """
        Change MSB to 0 for all received characters except the first
        and get a list of characters
        NOTE: having to change the MSB to 0 is a glitch in the raspberry pi,
        and you shouldn't have to do this!
        """

        if self.app_using_python_two():
            return list(map(lambda x: chr(ord(x) & ~0x80), list(response)))
        else:
            return list(map(lambda x: chr(x & ~0x80), list(response)))

    @staticmethod
    def app_using_python_two():
        return sys.version_info[0] < 3

    def get_response(self, raw_data):
        if self.app_using_python_two():
            response = [i for i in raw_data if i != '\x00']
        else:
            response = raw_data

        return response

    def response_valid(self, response):
        valid = True
        error_code = None
        if len(response) > 0:

            if self.app_using_python_two():
                error_code = str(ord(response[0]))
            else:
                error_code = str(response[0])

            if error_code != '1':  # 1:
                valid = False

        return valid, error_code

    def get_device_info(self):
        if self._name == "":
            return self._module + " " + str(self.address)
        else:
            return self._module + " " + str(self.address) + " " + self._name

    def read(self, num_of_bytes=31):
        raw_data = self.file_read.read(num_of_bytes)
        response = [x for x in raw_data if x != 0]
        if response[0] == 1:
            return ''.join([chr(x & ~0x80) for x in response[1:]])
        else:
            return f"Error: {response[0]}"

    def get_command_timeout(self, command):
        timeout = None
        if command.upper().startswith(self.LONG_TIMEOUT_COMMANDS):
            timeout = self._long_timeout
        elif not command.upper().startswith(self.SLEEP_COMMANDS):
            timeout = self.short_timeout

        return timeout

    def query(self, command):
        self.write(command)
        if command.upper().startswith(("R", "CAL")):
            time.sleep(self.LONG_TIMEOUT)
        elif not command.upper().startswith("SLEEP"):
            time.sleep(self.SHORT_TIMEOUT)
        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()

    def list_i2c_devices(self):
        """
        save the current address so we can restore it after
        """
        prev_addr = copy.deepcopy(self._address)
        i2c_devices = []
        for i in range(0, 128):
            try:
                self.set_i2c_address(i)
                self.read(1)
                i2c_devices.append(i)
            except IOError:
                pass
        # restore the address we were using
        self.set_i2c_address(prev_addr)

        return i2c_devices


def get_ph():
    from user_config.user_configurator import PHSensor
    """Return pH value."""
    total_measurements = 8  # Total number of measurements to take (3 to discard + 5 to average)
    discard_count = 3  # Number of initial measurements to discard
    valid_measurements = []  # List to store the valid measurements

    for attempt in range(total_measurements):
        temp_c = get_temp_c()  # Get the temperature in Celsius

        if temp_c is not None:
            try:
                # Send the read command to the pH sensor with temperature compensation
                response = PHSensor.query(f'RT,{temp_c:.2f}').rstrip('\0')
                ph_value = float(response)  # Convert the response to a float

                # Only store the measurement if it is one of the 5 valid measurements to average
                if attempt >= discard_count:
                    valid_measurements.append(ph_value)

            except ValueError:
                # Handle the case where the response cannot be converted to a float
                print("Error: Unable to parse pH value.")
                return None

            except IOError as e:
                # Handle any I/O errors that occur during communication with the sensor
                print(f"IOError occurred: {e}")
                return None

            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred: {e}")
                return None

        else:
            # If the temperature reading fails, wait for 5 second before retrying
            time.sleep(5)

        # Wait for 4 seconds before taking the next measurement
        time.sleep(4)

    # If there are not enough valid measurements, print a warning message
    if len(valid_measurements) < 5:
        print("Warning: Not enough valid measurements to calculate average pH value.")
        return None

    # Calculate and return the average of the valid measurements
    average_ph = sum(valid_measurements) / len(valid_measurements)
    return average_ph


def get_ec():
    from user_config.user_configurator import ECSensor
    """Return EC value."""
    temp_c = get_temp_c()  # Get the temperature in Celsius

    if temp_c is not None:
        try:
            # Send the read command to the EC sensor with temperature compensation
            response = ECSensor.query(f'RT,{temp_c:.2f}').rstrip('\0')
            return float(response)  # Convert the response to a float and return it

        except ValueError:
            # Handle the case where the response cannot be converted to a float
            print("Error: Unable to parse EC value.")
            return None

        except IOError as e:
            # Handle any I/O errors that occur during communication with the sensor
            print(f"IOError occurred: {e}")
            return None

        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
            return None

    else:
        # If the temperature reading fails, return None
        return None


def get_ppm():
    """Return PPM value."""
    total_measurements = 8  # Total number of measurements to take (3 to discard + 5 to average)
    discard_count = 3  # Number of initial measurements to discard
    valid_measurements = []  # List to store the valid measurements

    for attempt in range(total_measurements):
        ec = get_ec()  # Get the EC value

        if ec is not None:
            try:
                # Convert the EC value to PPM (Parts Per Million)
                ppm = ec * 0.5

                # Store the measurement if it is beyond the discard count
                if attempt >= discard_count:
                    valid_measurements.append(ppm)

            except TypeError as e:
                # Handle the case where the EC value is not a number
                print(f"TypeError occurred: {e}")
                return None

            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred: {e}")
                return None

        else:
            print("Warning: Failed to read EC value.")

        # Wait for 5 seconds before taking the next measurement
        time.sleep(4)

    # If there are not enough valid measurements, print a warning message
    if len(valid_measurements) < 5:
        print("Warning: Not enough valid measurements to calculate average PPM value.")
        return None

    # Calculate and return the average of the valid measurements
    average_ppm = sum(valid_measurements) / len(valid_measurements)
    return average_ppm


#######################################################
# SENSOR TESTS FOR MAIN INITIALIZATION

def test_temp_sensor():
    """Continuously read and display temperature values until interrupted or user types 'done'."""
    try:
        print("\n Starting temperature sensor test. \n")
        while True:
            # Get the temperature in Celsius
            temp_c = get_temp_c()
            # Get the temperature in Fahrenheit
            temp_f = get_temp_f()
            if temp_c is not None and temp_f is not None:
                # Print the temperature in both Celsius and Fahrenheit
                print(f"Temperature: {temp_c:.2f} °C / {temp_f:.2f} °F")
            else:
                print("Failed to read temperature.")

            # Prompt the user for input and check if they type 'done'
            user_input = input("Press enter to continue or type 'done' to stop: ").strip().lower()
            if user_input == 'done':
                clear_terminal()
                break

            # Wait for 2 seconds before the next reading
            time.sleep(5)
    except KeyboardInterrupt:
        # Handle the interruption to stop the test
        print("Stopping temperature sensor test.")

    print("Temperature sensor test stopped.")


def test_ec_sensor():
    from user_config.user_configurator import ECSensor
    """Continuously read and display EC values (in PPM) until interrupted."""
    try:
        print("\nStarting EC sensor test\n")
        while True:
            ec_value = get_ppm()
            print(f"PPM Value: {ec_value:.2f}")
            # Prompt the user for input and check if they type 'done'
            user_input = input("Press enter to continue or type 'done' to stop: ").strip().lower()
            if user_input == 'done':
                clear_terminal()
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping EC sensor test.")
    calibrate_ec = input("Would you like to calibrate the EC sensor? (yes/no): ").strip().lower()
    if calibrate_ec == 'yes':
        calibrate_sensor(ECSensor, 'ec')


def test_ph_sensor():
    from user_config.user_configurator import PHSensor
    """Continuously read and display pH values until interrupted."""
    try:
        print("\nStarting PH Sensor Test\n")
        while True:
            ph_value = get_ph()
            print(f"pH Value: {ph_value:.2f}")
            # Prompt the user for input and check if they type 'done'
            user_input = input("Press enter to continue or type 'done' to stop: ").strip().lower()
            if user_input == 'done':
                clear_terminal()
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping pH sensor test.")
    calibrate_ph = input("Would you like to calibrate the pH sensor? (yes/no): ").strip().lower()
    if calibrate_ph == 'yes':
        calibrate_sensor(PHSensor, 'ph')


def calibrate_sensor(sensor, sensor_type):
    """Guide the user through the calibration process for the specified sensor type."""
    print(f"Starting {sensor_type.upper()} sensor calibration...")
    if sensor_type == 'ph':
        points = ['mid', 'low',  'high']
    elif sensor_type == 'ec':
        points = ['dry', 'single', 'dual']
    else:
        print("Unknown sensor type for calibration.")
        return
    for point in points:
        while True:
            user_input = input(
                f"Place the sensor in the {point} calibration solution and type 'confirm {point}', or type "
                f"'cancel' to stop: ").strip().lower()
            if user_input == f"confirm {point}":
                response = sensor.query(f'Cal,{point}')
                print(response)
                break
            elif user_input == 'cancel':
                print("Calibration process canceled.")
                return
            else:
                print("Invalid input. Please follow the format 'confirm <point>' or type 'cancel' to stop.")


def test_fresh_water_pump():
    from user_config.user_configurator import FRESH_WATER_PUMP_PIN
    """Guide the user through testing the fresh water pump using GPIO pins and IoT relay."""
    print("\n\nStarting fresh water pump test...\n")

    while True:
        # Prompt the user to start the pump or quit
        user_input = input(
            "Type 'start' to begin a fresh water pump test or 'quit' to cancel and exit: ").strip().lower()

        if user_input == 'start':
            # Start the fresh water pump
            start_fresh_water_pump(FRESH_WATER_PUMP_PIN)
            print("\nFresh water pump started.")

            # Wait for 5 seconds to allow the water pump to operate
            time.sleep(5)
            print("\nWater pump operation for 5 seconds complete.")

            # Stop the fresh water pump
            end_fresh_water_pump(FRESH_WATER_PUMP_PIN)
            print("\nFresh water pump stopped.\n")
            break
        elif user_input in ['stop', 'cancel', 'end', 'done', 'exit', 'quit', 'halt', 'terminate', 'q', 'finish',
                            'abort', 'close', 'suspend', 'shutdown', 'discontinue', 'leave']:
            print("\nFresh water pump test canceled.\n")
            clear_terminal()
            return  # Exit the function
        else:
            print("\nInvalid input. Please type 'start' to begin or 'quit' to cancel.")
