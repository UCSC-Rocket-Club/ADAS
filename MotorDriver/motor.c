/**
 * @file motor.c
 * @author James Strawson
 * @date 2018
 */

#include <stdio.h>
#include <rc/motor.h>
#include <rc/model.h>
#include <rc/gpio.h>

// preposessor macros
#define unlikely(x)	__builtin_expect (!!(x), 0)


#define MOT_STBY		0,20	//gpio0.20	P9.41

static int init_flag = 0;

// get the direction (sign) of the input
// @input: the number that encodes motor movement
// @outut: 1 for clockwise (positive), 0 for counter clockwise (negative zero inclusive)
int _getDirection(double duty){
	if (duty > 0) return 1;
	else return 0;
}

int rc_motor_init(void)
{
	return rc_motor_init_freq(RC_MOTOR_DEFAULT_PWM_FREQ);
}


int rc_motor_init_freq(int pwm_frequency_hz)
{
	int i;

	// set up gpio pins
	if(unlikely(rc_gpio_init(MOT_STBY, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in rc_motor_init, failed to set up gpio %d,%d\n", MOT_STBY);
		return -1;
	}

	if(unlikely(rc_gpio_init(DIRECTION, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in rc_motor_init, failed to set up gpio %d,%d for direction\n", DIRECTION);
		return -1;
	}

	if(unlikely(rc_gpio_init(SPEED, GPIOHANDLE_REQUEST_OUTPUT))){
		fprintf(stderr,"ERROR in rc_motor_init, failed to set up gpio %d,%d for speed\n", SPEED);
		return -1;
	}


	// now set all the gpio pins and pwm to something predictable
	init_flag = 1;
	if(unlikely(rc_motor_free_spin(0))){
		fprintf(stderr,"ERROR in rc_motor_init\n");
		init_flag = 0;
		return -1;
	}

	// make sure standby is off since most users won't use it
	if(unlikely(rc_gpio_set_value(MOT_STBY,1))){
		fprintf(stderr,"ERROR in rc_motor_init, can't write to gpio %d,%d\n",MOT_STBY);
		return -1;
	}
	init_flag = 1;
	return 0;
}



int rc_motor_cleanup(void)
{
	int i;
	if(!init_flag) return 0;
	rc_motor_free_spin(0);
	rc_gpio_cleanup(MOT_STBY);
	rc_gpio_cleanup(DIRECTION);
	rc_gpio_cleanup(SPEED);
	return 0;
}


int rc_motor_set(double duty)
{
	int a,b,i;

	// sanity checks
	if(unlikely(init_flag==0)){
		fprintf(stderr, "ERROR in rc_motor_set, call rc_motor_init first\n");
		return -1;
	}

	// check that the duty cycle is within +-1
	if	(duty > 1.0)	duty = 1.0;
	else if	(duty <-1.0)	duty =-1.0;

	// set direction
	// if negative duty spin 0, else 1
	dir = _getDirection(duty);
	// set direction
	if(unlikely(rc_gpio_set_value(DIRECTION, dir))){
		fprintf(stderr,"ERROR in rc_motor_set, failed to write to gpio direction pin %d,%d\n", DIRECTION);
		return -1;
	}

	// set speed
	if(unlikely(rc_gpio_set_value(SPEED, 1))){
		fprintf(stderr,"ERROR in rc_motor_set, failed to write to gpio speed pin %d,%d\n", SPEED);
		return -1;
	}

	return 0;
}


int rc_motor_free_spin()
{
	int i;

	// sanity checks
	if(unlikely(init_flag==0)){
		fprintf(stderr, "ERROR in rc_motor_free_spin, call rc_motor_init first\n");
		return -1;
	}

	// set speed to zero
	if(unlikely(rc_gpio_set_value(SPEED, 0))){
		fprintf(stderr,"ERROR in rc_motor_free_spin, failed to write to gpio pin %d,%d\n",SPEED);
		return -1;
	}

	return 0;
}



int rc_motor_brake(double duty)
{
	int i, reverse;

	// get the reverse direction to spin
	reverse = !_getDirection(duty); // get sign of direction and reverse it

	if(unlikely(init_flag==0)){
		fprintf(stderr, "ERROR in rc_motor_brake, call rc_motor_init first\n");
		return -1;
	}

	// set gpio and pwm for that motor
	if(unlikely(rc_gpio_set_value(DIRECTION, reverse))){
		fprintf(stderr,"ERROR in rc_motor_brake, failed to write to gpio direction pin %d,%d\n", DIRECTION);
		return -1;
	}
	if(unlikely(rc_gpio_set_value(SPEED, 1))){
		fprintf(stderr,"ERROR in rc_motor_brake, failed to write to gpio speed pin %d,%d\n",SPEED);
		return -1;
	}
	// reverse the direction for defined amount of time
	rc_usleep(BACK_FORCE_TIME);

  // then just free spin
	// gear ratio of motor will automatcially stop motor
	rc_motor_free_spin()
	return 0;
}
