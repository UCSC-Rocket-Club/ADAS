#include <stdio.h>
#include <robotcontrol.h>
#include <rc/encoder.h>

int main() {

	if( rc_encoder_init() ) {
		printf("Failed to init. Exiting.\n\n");
		return -1;
	}
	else {
		printf("Init successful.\n\n");
	}

	rc_encoder_write(1, 420);
	printf("%d\n", rc_encoder_read(1));
	
	if ( rc_encoder_cleanup() == 0 )
		printf("Cleanup success.\n\n");

	return 0;
}
