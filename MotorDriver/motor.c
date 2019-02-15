/**
 * @file motor.c
 * @author James Strawson
 * @date 2018
 */

#include <stdio.h>
#include <stdlib.h>
#include "motor.h"
#include <rc/model.h>
#include <rc/gpio.h>
#include <rc/time.h>

// preposessor macros
#define unlikely(x)	__builtin_expect (!!(x), 0)

// motor pin definitions

// direction pin: chip, pin
#define DIRECTION_A   3,20

#define DIRECTION_B 3,17

// speed pin: chip, pin
#define SPEED   1,17

// kep track of whether things were initialized
static int init_flag = 0;
// check to see if moving i.e. need to pulse motor to stop
static int moving = 0;

// get the direction (sign) of the input
// @input: the number that encodes motor movement
// @outut: 1 for clockwise (positive), 0 for counter clockwise (negative zero inclusive)
int _getDirection(double duty){
	if (duty > 0) return 1;
	else return 0;
}

int adas_motor_init(void)
{
	return adas_motor_init_freq(ADAS_MOTOR_DEFAULT_PWM_FREQ);
}


int adas_motor_init_freq(int pwm_frequency_hz)
{

	// set up gpio pins
	if(unlikely(rc_gpio_init(DIRECTION_A, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in adas_motor_init, failed to set up gpio %d,%d for direction\n", DIRECTION);
		return -1;
	}

	if(unlikely(rc_gpio_init(DIRECTION_B, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in adas_motor_init, failed to set up gpio %d,%d for direction\n", DIRECTION);
		return -1;
	}


	if(unlikely(rc_gpio_init(SPEED, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in adas_motor_init, failed to set up gpio %d,%d for speed\n", SPEED);
		return -1;
	}


	// now set all the gpio pins and pwm to something predictable
	init_flag = 1;
	if(unlikely(adas_motor_free_spin())){
		fprintf(stderr,"ERROR in adas_motor_init\n");
		init_flag = 0;
		return -1;
	}

	init_flag = 1;
	return 0;
}



int adas_motor_cleanup(void)
{
	if(!init_flag) return 0;
	adas_motor_free_spin(0);
	rc_gpio_cleanup(DIRECTION_A);
	rc_gpio_cleanup(DIRECTION_B);
	rc_gpio_cleanup(SPEED);
	return 0;
}


int adas_motor_set(double duty)
{
	int dir;

	// sanity checks
	if(unlikely(init_flag==0)){
		fprintf(stderr, "ERROR in adas_motor_set, call adas_motor_init first\n");
		return -1;
	}

	// check that the duty cycle is within +-1
	if	(duty > 1.0)	duty = 1.0;
	else if	(duty <-1.0)	duty =-1.0;

	// set direction
	// if negative duty spin 0, else 1
	dir = _getDirection(duty);
	if (moving == dir) return 0; // if doing as is just go

	
	// turn off motor while changing direction
	if(unlikely(rc_gpio_set_value(SPEED, 0))){
		fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio speed pin %d,%d\n", SPEED);
		return -1;
	}


		
	// set direction

	if (dir)
	{
		if(unlikely(rc_gpio_set_value(DIRECTION_A, 1))){
			fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
			return -1;
		}
		if(unlikely(rc_gpio_set_value(DIRECTION_B, 0))){
			fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
			return -1;
		}
	}

	else
	{
		if(unlikely(rc_gpio_set_value(DIRECTION_A, 0))){
			fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
			return -1;
		}
		if(unlikely(rc_gpio_set_value(DIRECTION_B, 1))){
			fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
			return -1;
		}
	}
	

	// set speed
	if(unlikely(rc_gpio_set_value(SPEED, 1))){
		fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio speed pin %d,%d\n", SPEED);
		return -1;
	}

	// log that we're moving the motor
	moving = dir;
	return 0;
}


int adas_motor_free_spin()
{
	// sanity checks
	if(unlikely(init_flag==0)){
		fprintf(stderr, "ERROR in adas_motor_free_spin, call adas_motor_init first\n");
		return -1;
	}

	// set speed to zero
	if(unlikely(rc_gpio_set_value(SPEED, 0))){
		fprintf(stderr,"ERROR in adas_motor_free_spin, failed to write to gpio pin %d,%d\n",SPEED);
		return -1;
	}

	return 0;
}



int adas_motor_brake()
{
	// int reverse;

	// // get the reverse direction to spin
	// reverse = !_getDirection(duty); // get sign of direction and reverse it

	// if(unlikely(init_flag==0)){
	// 	fprintf(stderr, "ERROR in adas_motor_brake, call adas_motor_init first\n");
	// 	return -1;
	// }

	// // check to see if motor was just moving
	// // only pulse if motor was just moving
	// if(moving){
	// 	// set gpio and pwm for that motor
	// 	if(unlikely(rc_gpio_set_value(DIRECTION, reverse))){
	// 		fprintf(stderr,"ERROR in adas_motor_brake, failed to write to gpio direction pin %d,%d\n", DIRECTION);
	// 		return -1;
	// 	}
	// 	if(unlikely(rc_gpio_set_value(SPEED, 1))){
	// 		fprintf(stderr,"ERROR in adas_motor_brake, failed to write to gpio speed pin %d,%d\n",SPEED);
	// 		return -1;
	// 	}
	// 	// reverse the direction for defined amount of time
	// 	rc_usleep(BACK_FORCE_TIME);
	// }

 //  // then just free spin
	// // if wasn't moving dont worry bout it fuck it
	// // gear ratio of motor will automatcially stop motor
	// moving = 1;


	if(unlikely(rc_gpio_set_value(DIRECTION_A, 0))){
		fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
		return -1;
	}
	if(unlikely(rc_gpio_set_value(DIRECTION_B, 0))){
		fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
		return -1;
	}

	if(unlikely(rc_gpio_set_value(SPEED, 0))){
		fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
		return -1;
	}
	moving = -1;


	adas_motor_free_spin();
	return 0;
}
