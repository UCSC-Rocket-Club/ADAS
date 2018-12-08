/**
 * @file IMU_reader.c
 * author: Julio Sandino
 * Organization: UCSC Rocket Team
 */

#include <stdio.h>
#include <signal.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include <rc/mpu.h>
#include <rc/time.h>

#define I2C_BUS 2

// This program will do the following functionality
// It will read from the IMU and print the output to
// stdout
//
typedef enum g_mode_t {
	G_MODE_RAD,
	G_MODE_DEG,
	G_MODE_RAW
} g_mode_t;

typedef enum a_mode_t {
	A_MODE_MS2,
	A_MODE_G,
	A_MODE_RAW
} a_mode_t;

int running;

static void __signal_handler(__attribute__ ((unused)) int dummy)
{
	running=0;
	return;
}

int main(int argc, char*argv[])
{
	// make PID file to indicate your project is running
	// due to the check made on the call to rc_kill_existing_process() above
	// we can be fairly confident there is no PID file already and we can
	// make our own safely.
	rc_kill_existing_process(0.2);
	rc_make_pid_file();

	// set signal handler so the loop can exit cleanly
	signal(SIGINT, __signal_handler);
	running = 1;

	rc_mpu_data_t data; // struct to hold new data

	// use defualts for now, except also enable magnetometer
	rc_mpu_config_t conf = rc_mpu_default_config();
	conf.i2c_bus = I2C_BUS;
	conf.enable_magnetometer = 1;
	conf.show_warnings = 1;

	while (running) {
		if(rc_mpu_initialize(&data, conf)) {
			fprintf(stderr, "rc_mpu_initialize_failed\n");
			return -1;
		}

		// read sensor data
		if (rc_mpu_read_accel(&data) < 0) {
			printf("read accel data failed\n");
		}
		if (rc_mpu_read_gyro(&data) < 0) {
			printf("read gyro data failed\n");
		}
		printf("%f,%f,%f,%f,%f,%f,%f,%f,%f\n",	data.accel[0],\
						data.accel[1],\
						data.accel[2],\
						data.gyro[0],\
						data.gyro[1],\
						data.gyro[2],\
						data.mag[0],\
						data.mag[1],\
						data.mag[2]);
		fflush(stdout);
		rc_usleep(100000);
	}
	

	printf("\n");
	rc_mpu_power_off();
	return 0;
}
