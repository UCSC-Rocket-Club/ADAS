#include <stdio.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include <rc/gpio.h>

int main() {
	if (rc_gpio_init(2,
			  2,
			  GPIOHANDLE_REQUEST_OUTPUT) == 0) {
		printf("It worked!\n");	
		if(rc_gpio_set_value(2, 2, 1) == 0) {
			printf("Success");
		}
	}  else {
		printf("It didn't work!");
	}
	printf("\n");
	return 0;
}
