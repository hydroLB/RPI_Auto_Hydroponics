from pumps import *
waterPump.startReverse()
nutrientPump1.startReverse()
nutrientPump2.startReverse()
nutrientPump3.startReverse()
nutrientPump4.startReverse()
pHDownPump.startReverse()
pHUpPump.startReverse()

print("Press enter to stop")
input()

waterPump.stop()
nutrientPump1.stop()
nutrientPump2.stop()
nutrientPump3.stop()
nutrientPump4.stop()
pHDownPump.stop()
pHUpPump.stop()
