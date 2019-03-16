#!/usr/bin/python
from MS5611 import MS5611

sensor = MS5611(i2c=0x77, elevation=230)
sensor.read()
sensor.printResults()
print(sensor.getAltitude())
