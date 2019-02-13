#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems


// direction pin: chip, pin
#define DIRECTION   3,20
#define FREQUENCY 1000


int main(){


  if(unlikely(rc_gpio_init(DIRECTION, GPIOHANDLE_REQUEST_OUTPUT))){
    fprintf(stderr,"ERROR in adas_motor_init, failed to set up gpio %d,%d for direction\n", DIRECTION);
    return -1;
  }


  while (1) {

    // set speed
    if(unlikely(rc_gpio_set_value(DIRECTION, 1))){
      fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio speed pin %d,%d\n", SPEED);
      return -1;
    }

    rc_usleep(FREQUENCY);

    // set speed
    if(unlikely(rc_gpio_set_value(DIRECTION, 0))){
      fprintf(stderr,"ERROR in adas_motor_set, failed to write to gpio speed pin %d,%d\n", SPEED);
      return -1;
    }

    rc_usleep(FREQUENCY);
  }


}
