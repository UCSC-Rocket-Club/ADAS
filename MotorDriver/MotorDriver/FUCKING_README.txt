api for motordriver.c

Purpose: controls motor through stdin interface of standard C program

To compile: run make in the directory with all files

Wiring: The motor driver is hooked up to the gpio pin port 3, and the encoder wire is connected to port 3

Use: Send in delimited values (can be anything as long as its not seperated by newline) to move motor to.
The program will find the most recent number to move the motor to.
i.e. if it recieves 10 30 40 35 
it will move the motor to position 35 and flush all other numbers.

To exit the program the SIGINIT signal is send to the program and interpreted exit. The motor is then fully retracted and 
the program disposes of all libraries and exits. 