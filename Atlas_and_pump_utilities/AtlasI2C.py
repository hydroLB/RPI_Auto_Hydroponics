#!/usr/bin/python

import io
import sys
import fcntl
import time
import copy


def read_temp_file():
    from user_config.user_configurator import W1_TEMP_PATH
    """Read temperature file and return its content."""
    try:
        with open(W1_TEMP_PATH, 'r') as temp_file:
            first_line = temp_file.readline().strip()
            if not first_line:
                return temp_file.readline().strip()
            else:
                return first_line
    except FileNotFoundError:
        print("Error: Temperature file not found in read_temp_file.")
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
        """
        reads a specified number of bytes from I2C, then parses and displays the result
        """

        raw_data = self.file_read.read(num_of_bytes)
        response = self.get_response(raw_data=raw_data)
        # print(response)
        is_valid, error_code = self.response_valid(response=response)

        if is_valid:
            char_list = self.handle_raspi_glitch(response[1:])
            result = str(''.join(char_list))
            # result = "Success: " +  str(''.join(char_list))
        else:
            result = "Error " + self.get_device_info() + ": " + error_code

        return result

    def get_command_timeout(self, command):
        timeout = None
        if command.upper().startswith(self.LONG_TIMEOUT_COMMANDS):
            timeout = self._long_timeout
        elif not command.upper().startswith(self.SLEEP_COMMANDS):
            timeout = self.short_timeout

        return timeout

    def query(self, command):
        """
        write a command to the board, wait the correct timeout,
        and read the response
        """
        self.write(command)
        current_timeout = self.get_command_timeout(command=command)
        if not current_timeout:
            return "sleep mode"
        else:
            time.sleep(current_timeout)
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
    from main.main import PHSensor
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
    from main.main import ECSensor
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


#######################################################
# SENSOR TESTS FOR MAIN INITIALIZATION

def test_temp_sensor():
    """Continuously read and display temperature values until interrupted or user types 'done'."""
    try:
        print("Type 'done' to stop the test.")
        while True:
            # Get the temperature in Celsius
            temp_c = get_temp_c()
            # Get the temperature in Fahrenheit
            temp_f = get_temp_f()
            print("Temperature Sensor Test for PH and EC compensation")
            if temp_c is not None and temp_f is not None:
                # Print the temperature in both Celsius and Fahrenheit
                print(f"Temperature: {temp_c:.2f} °C / {temp_f:.2f} °F")
            else:
                print("Failed to read temperature.")

            # Prompt the user for input and check if they type 'done'
            print("Press enter to continue or type 'done' to stop.")
            user_input = input().strip().lower()
            if user_input == 'done':
                break

            # Wait for 2 seconds before the next reading
            time.sleep(2)
    except KeyboardInterrupt:
        # Handle the interruption to stop the test
        print("Stopping temperature sensor test.")

    print("Temperature sensor test stopped.")


def test_ph_sensor(sensor):
    """Continuously read and display pH values until interrupted."""
    try:
        print("Type 'done' to stop the test.")
        while True:
            # Get the pH value with temperature compensation
            ph_value = get_ph()
            # Print the pH value
            print(f"pH Value: {ph_value:.2f}, press enter to continue or type 'done' to exit")

            # Prompt the user for input and check if they type 'done'
            user_input = input().strip().lower()
            if user_input == 'done':
                break

            # Wait for 0.5 seconds before the next reading
            time.sleep(0.5)
    except KeyboardInterrupt:
        # Handle the interruption to stop the test
        print("Stopping pH sensor test.")

    # Ask the user if they want to calibrate the pH sensor
    calibrate_ph = input("Would you like to calibrate the pH sensor? (yes/no): ").strip().lower()
    if calibrate_ph == 'yes':
        calibrate_sensor(sensor, 'ph')


def test_ec_sensor(sensor):
    """Continuously read and display EC values (in PPM) until interrupted."""
    try:
        print("Type 'done' to stop the test.")
        while True:
            # Get the EC value and convert it to PPM
            ec_value = get_ppm()
            # Print the EC value in PPM
            print(f"PPM Value: {ec_value:.2f}, press enter to continue or type 'done' to exit")

            # Prompt the user for input and check if they type 'done'
            user_input = input().strip().lower()
            if user_input == 'done':
                break

            # Wait for 0.5 seconds before the next reading
            time.sleep(0.5)
    except KeyboardInterrupt:
        # Handle the interruption to stop the test
        print("Stopping EC sensor test.")

    # Ask the user if they want to calibrate the EC sensor
    calibrate_ec = input("Would you like to calibrate the EC sensor? (yes/no): ").strip().lower()
    if calibrate_ec == 'yes':
        calibrate_sensor(sensor, 'ec')



def calibrate_sensor(sensor, sensor_type):
    """Guide the user through the calibration process for the specified sensor type."""
    print(f"Starting {sensor_type.upper()} sensor calibration...")

    # Determine the calibration points based on the sensor type
    if sensor_type == 'ph':
        points = ['low', 'mid', 'high']
    elif sensor_type == 'ec':
        points = ['dry', 'single', 'dual']
    else:
        print("Unknown sensor type for calibration.")
        return

    # Loop through each calibration point
    for point in points:
        while True:
            # Prompt the user to place the sensor in the appropriate calibration solution
            user_input = input(
                f"Place the sensor in the {point} calibration solution and type 'confirm {point}', or type 'cancel' to stop: ").strip().lower()
            if user_input == f"confirm {point}":
                # Send the calibration command to the sensor
                response = sensor.query(f'Cal,{point}')
                # Print the response from the sensor
                print(response)
                break
            elif user_input == 'cancel':
                print("Calibration process canceled.")
                return
            else:
                print("Invalid input. Please follow the format 'confirm <point>' or type 'cancel' to stop.")


