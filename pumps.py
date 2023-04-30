
from adafruit_motorkit import MotorKit
driver0 = MotorKit(0x60)
driver1 = MotorKit(0x61)

class Pump:
	def __init__(self,motor,direction):
		self.motor = motor
		self.direction = direction
	def start(self):
		self.motor.throttle = self.direction
	def stop(self):
		self.motor.throttle = 0
	def startReverse(self):
		self.motor.throttle = -self.direction
waterPump = Pump(driver0.motor4,-1)
nutrientPump1 = Pump(driver0.motor3,1)
nutrientPump2 = Pump(driver1.motor3, 1)
nutrientPump3 = Pump(driver1.motor2, 1)
nutrientPump4 = Pump(driver1.motor1, -1)
pHDownPump = Pump(driver1.motor4, -1)
pHUpPump = Pump(driver0.motor1, 1)


