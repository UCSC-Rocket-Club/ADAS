#!/usr/bin/python
import smbus
import math
import os
import time

class IMU:
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    bus = smbus.SMBus(1)
    address = 0x68

    # Activate to be able to address the module
    bus.write_byte_data(address, power_mgmt_1, 0)

    def read_byte(self, reg):
        return bus.read_byte_data(self.address, reg)

    def read_word(self, reg):
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        value = (h << 8) + l
        return value

    def read_word_2c(self, reg):
        val = self.read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self, a,b):
        return math.sqrt((a*a)+(b*b))

    # Expects Accelerometer values x, y, z
    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    # Expects Accelerometer values x, y, z 
    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    # Returns a list of 3 values for gyroscope [x,y,z] in degrees
    def get_gyro_data(self):
        gyroscope_xout = self.read_word_2c(0x43) / 131
        gyroscope_yout = self.read_word_2c(0x45) / 131
        gyroscope_zout = self.read_word_2c(0x47) / 131

        return [gyroscope_xout, gyroscope_yout, gyroscope_zout]

    # Returns a list of 3 values for accelerometer [x,y,z] in gs
    def get_accel_data(self):
        accelerometer_xout = self.read_word_2c(0x3b) / 16384.0
        accelerometer_yout = self.read_word_2c(0x3d) / 16384.0 
        accelerometer_zout = self.read_word_2c(0x3f) / 16384.0

        return [accelerometer_xout, accelerometer_yout, accelerometer_zout] 
