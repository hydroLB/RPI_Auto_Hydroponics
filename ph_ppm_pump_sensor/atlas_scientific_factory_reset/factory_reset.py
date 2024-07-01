import fcntl
import io
import time


class AtlasI2C:
    SHORT_TIMEOUT = 0.3

    def __init__(self, address, bus=1):
        self._address = address
        self.bus = bus
        self.file_read = io.open(file=f"/dev/i2c-{self.bus}", mode="rb", buffering=0)
        self.file_write = io.open(file=f"/dev/i2c-{self.bus}", mode="wb", buffering=0)
        self.set_i2c_address(self._address)

    def set_i2c_address(self, addr):
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

    def write(self, cmd):
        cmd += "\r"
        self.file_write.write(cmd.encode('latin-1'))

    def read(self, num_of_bytes=31):
        return self.file_read.read(num_of_bytes)

    def query(self, command):
        self.write(command)
        time.sleep(self.SHORT_TIMEOUT)
        return self.read()


def main():
    try:
        # Initialize the pH sensor with the specified I2C address (99)
        PHSensor = AtlasI2C(address=99)

        # Send factory reset command
        response = PHSensor.query("Factory")

        # Print the response
        print(response)

        # Decode and interpret the response
        if b'*OK' in response:
            print("Factory reset successful.")
        else:
            print("Factory reset failed or no response.")

    except IOError as e:
        print(f"IOError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()