# ADAS
ADAS BABY!

This is the official repo for the UCSC Rocket team ADaptive Aerobreaking Component. 

 The code consists of 2 parts, our control algorithm to generate real-time deployment profiles for our fins and the firmware to make that possible.

Specifications
- Run on Raspbery Pi 3
- Altitude taken from MP3115a2
- Acceleration and positional data taken from MPU6050
- Motor control feedback with Arduino Teensy
- Closed loop feedback using hall effect encoder acurate to within 360/1120 degrees
- Motor actuation controlled by MD13S motor H-Bridge
