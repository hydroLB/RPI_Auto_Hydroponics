# Handles pumps start, stop, reverse, the list of all the pumps,  and priming using list
# Also handles fresh water pump on and off using GPIO high/low

# Import the MotorKit class from the Adafruit Motor HAT library.
import RPi.GPIO as GPIO


class Pump:
    def __init__(self, motor, direction):
        """
        Initialize a new Pump object.

        Args:
            motor: Motor object from the MotorKit.
            direction: Integer representing the motor direction (1 or -1).
        """
        if not isinstance(direction, int):
            direction = int(direction)  # Ensure direction is an integer
        if direction not in [1, -1]:
            raise ValueError("Expected direction to be 1 or -1, but got {}. "
                             "Error in Pump.__init__.".format(direction))
        if not hasattr(motor, 'throttle'):
            raise AttributeError("Motor object missing 'throttle' attribute. Error in Pump.__init__.")

        self.motor = motor
        self.direction = direction
        self.speed = 1.0  # Set default speed to 1.0

    def start(self):
        """Start the pump by setting the motor throttle to its direction."""
        try:
            self.motor.throttle = self.direction * self.speed
        except Exception as e:
            raise Exception("An error occurred in Pump.start: {}".format(e))

    def stop(self):
        """Stop the pump by setting the motor throttle to zero."""
        try:
            self.motor.throttle = 0
        except Exception as e:
            raise Exception("An error occurred in Pump.stop: {}".format(e))

    def startReverse(self):
        """Start the pump in reverse by setting the motor throttle to the opposite of its direction."""
        try:
            self.motor.throttle = -self.direction * self.speed
        except Exception as e:
            raise Exception("An error occurred in Pump.startReverse: {}".format(e))


def prime(pump: Pump):
    """
    Primes the provided pump with user assistance.

    Args:
        pump (object): A pump object with 'start' and 'stop' methods.
    """
    try:
        # Check if the pump object has the necessary 'start' and 'stop' methods
        if not hasattr(pump, 'start') or not hasattr(pump, 'stop'):
            raise AttributeError(
                "Pump object must have 'start' and 'stop' methods. Error in prime.")

        # Ask the user if they want to prime the pump
        response = input("[HIGHLY RECOMMENDED] Do you want to prime the pump? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Pump priming skipped.")
            return

        # Interact with the user to prime the pump
        print("Press enter to start priming the pump, then press enter to stop when liquid level reaches the end of "
              "the pump's tubing.")
        input()  # Wait for user to hit enter to start priming
        pump.start()  # Start the pump
        input()  # Wait for user to hit enter to stop priming
        pump.stop()  # Stop the pump

        print("Pump primed successfully.\n")

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in prime: {}".format(e))
    except Exception as e:
        raise Exception("An unexpected error occurred in prime: {}".format(e))


def clear_lines(pump: Pump):
    """
    Clears the lines of the provided pump with user assistance.

    Args:
        pump (object): A pump object with 'start', 'stop', and 'startReverse' methods.
    """
    try:
        # Check if the pump object has the necessary 'start', 'stop', and 'startReverse' methods
        if not hasattr(pump, 'start') or not hasattr(pump, 'stop') or not hasattr(pump, 'startReverse'):
            raise AttributeError(
                "Pump object must have 'start', 'stop', and 'startReverse' methods. Error in clear_lines.")

        # Ask the user if they want to clear the pump lines
        response = input("Do you want to clear the pump lines? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Pump line clearing aborted by user.")
            return

        # Interact with the user to clear the pump lines
        print("Press enter to start reversing the pump, then press enter to stop when liquid is removed from tube.\n"
              "If very sticky residue is present, very warm water sucked by reverse side of the pump will clear all "
              "stains.")
        input()  # Wait for user to hit enter to start reversing
        pump.startReverse()  # Start the pump in reverse
        input()  # Wait for user to hit enter to stop reversing
        pump.stop()  # Stop the pump

        print("Pump line cleaned successfully.\n")

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in clear_lines: {}".format(e))
    except Exception as e:
        raise Exception("An unexpected error occurred in clear_lines: {}".format(e))


def run_pumps_list(pumps_list, reverse=False):
    """
    Start all pumps in the given list in forward or reverse mode.

    Args:
        pumps_list: List of pump objects to be run.
        reverse: Boolean indicating whether pumps should run in reverse mode (default: False).
    """
    try:
        if not isinstance(pumps_list, list):
            raise TypeError("Expected pumps_list to be a list, but got type {}. "
                            "Error in run_pumps_list.".format(type(pumps_list).__name__))

        if not isinstance(reverse, bool):
            raise TypeError("Expected reverse to be a boolean, but got type {}. "
                            "Error in run_pumps_list.".format(type(reverse).__name__))

        for pump in pumps_list:
            if reverse:
                if not hasattr(pump, 'startReverse'):
                    raise AttributeError("Pump object missing 'startReverse' method. Error in run_pumps_list.")
                pump.startReverse()
            else:
                if not hasattr(pump, 'start'):
                    raise AttributeError("Pump object missing 'start' method. Error in run_pumps_list.")
                pump.start()

    except TypeError as e:
        raise TypeError("Type error occurred in run_pumps_list: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in run_pumps_list: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in run_pumps_list: {}".format(e))


def stop_pumps_list(pumps_list):
    """Stop all pumps in the given list."""
    try:
        if not isinstance(pumps_list, list):
            raise TypeError("Expected pumps_list to be a list, but got type {}. Error in stop_pumps_list.".format(
                type(pumps_list).__name__))

        for pump in pumps_list:
            if not hasattr(pump, 'stop'):
                raise AttributeError("Pump object missing 'stop' method. Error in stop_pumps_list.")
            pump.stop()

    except TypeError as e:
        raise TypeError("Type error occurred in stop_pumps_list: {}".format(e))

    except AttributeError as e:
        raise AttributeError("Attribute error occurred in stop_pumps_list: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in stop_pumps_list: {}".format(e))


def start_fresh_water_pump(pin):
    # noinspection GrazieInspection
    """
        Activates the fresh water pump by setting the specified GPIO pin to HIGH.

        Args:
            pin (int): The GPIO pin connected to the pump relay.
        """
    try:
        if not isinstance(pin, int):
            raise TypeError("Expected pin_number to be an integer, but got type {}. "
                            "Error in start_fresh_water_pump.".format(type(pin).__name__))

        # Set the GPIO pin to HIGH to start the pump
        GPIO.output(pin, GPIO.HIGH)

    except TypeError as e:
        raise TypeError("Type error occurred in start_fresh_water_pump: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in start_fresh_water_pump: {}".format(e))


def end_fresh_water_pump(pin):
    # noinspection GrazieInspection
    """
        Deactivates the fresh water pump by setting the specified GPIO pin to LOW.

        Args:
            pin (int): The GPIO pin connected to the pump relay.
        """
    try:
        if not isinstance(pin, int):
            raise TypeError("Expected pin_number to be an integer, but got type {}. "
                            "Error in end_fresh_water_pump.".format(type(pin).__name__))

        # Set the GPIO pin to LOW to stop the pump
        GPIO.output(pin, GPIO.LOW)

    except TypeError as e:
        raise TypeError("Type error occurred in end_fresh_water_pump: {}".format(e))

    except Exception as e:
        raise Exception("An unexpected error occurred in end_fresh_water_pump: {}".format(e))
