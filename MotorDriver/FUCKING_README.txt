api for Motor Controller code

Purpose: controls motor through serial interface to arduino microcontroller

hardware:
Arduino Teensy LC
MD13S Cytron motor driver
Neverest 60 DC motor with encoder



To compile: everything will sit on the arduino Teensy, so
1. download arduino ide
2. download and install teensy bootloader addon: https://www.pjrc.com/teensy/loader.html
3. import the .cpp and .h in MotorDriver folder into the arduino library manager
4. open MotorController.ino in arduino
5. select the teensy board for the arduino IDE flash port
6. run the bootloader and upload the software onto the board



Wiring: 


encoder
the encoder wires are hooked up as follows:

board          encoder
vcc    ------- pwr in
gnd    ------- gnd
pin 22 ------- channel A
pin 23 ------- channel B

The pins are aranged to be plugged in easily. The pin definitions at the top of the MotorController.ino code DOES NOT match the actual pinout because of 
a signage error in the code hookup (i fucked up eat me). 


motorDriver
the MD13S motor driver is hooked up to the pins as follows

board           driver
17 ------------- gnd
16 ------------- pwm
15 ------------- dir

this pinout is important since the 17 pin IS NOT TECHNICALLY GROUND IT SIMULATES GROUND BY SETTING THE PIN TO GETTT LOWWWWW. Pin 17 can sink more 
current then normal so thats why its set to the ground pin. The pwm pin is pwm capable which is why its the pwm pin. dir is just a pin, its still cool though.




To Use: connect the serial1 pins on the teensy to a serial connection and send values to the board. numbers will be read in a values 
seperated by newlines. i.e. send a number and press enter. negative values are ignored (i.e. not read in)

To retract the fins and exit the program, send an e character. this will execute the end function. BE WARNED, UPON SEEING e THE PROGRAM
WILL EXIT AND THE BOARD MUST BE RESTARTED TO DO ANY MOVEMENT OR ANYTHING AGAIN!