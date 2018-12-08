/**
 * @file rc_project_template.c
 *
 * This is meant to be a skeleton program for Robot Control projects. Change
 * this description and file name before modifying for your own purpose.
 */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include "motor.h" //include adas motor shit

#define MOTOR_DRIVER_MARGIN 5 // margin of postition to stop motor and lock in place
#define MOTOR_DRIVER_CPR 1120 // pulses per revolution of output shaft
#define MOTOR_DRIVER_MAX  1120/4 // pulses in max deployment, i.e. stay under this pulse the motor outputs 1120 pulses for 1 revolution
#define MOTOR_DRIVER_ENCODER_POS 3 // encoder port we're plugging into
#define MOTOR_DRIVER_READ_HZ 1000000000/25 // time in ns/periods between each cycle i.e. refresh rate
#define DIVISION 100000
// function declarations
void on_pause_press();
void on_pause_release();
void Init();
int outsideMargin(int current, int projected);
void moveMotor(int currentPos, int projectedPos);


// fake encoder positions to test functions
static uint64_t lastReadTime = 0;
static int initFlag = 0; // initialize flag
/**
 * This template contains these critical components
 * - ensure no existing instances are running and make new PID file
 * - start the signal handler
 * - initialize subsystems you wish to use
 * - while loop that checks for EXITING condition
 * - cleanup subsystems at the end
 *
 * @return     0 during normal operation, -1 on error
 */
int main()
{
        // initilize everything
        Init();
        // Assign functions to be called when button events occur
        rc_button_set_callbacks(RC_BTN_PIN_PAUSE,on_pause_press,on_pause_release);
        // make PID file to indicate your project is running
        // due to the check made on the call to rc_kill_existing_process() above
        // we can be fairly confident there is no PID file already and we can
        // make our own safely.


        // position data
        int currentPos;
        //int[] projectedPos = [123,1231,2312,312,3123,123,123,12,31,23,123,12,3123123];
	int projectedPos[10] = {123, 132, 32466, 5235, 9000, 900, 234, 123, 1325, 23532};

        rc_make_pid_file();
        printf("\nPress and release pause button to turn green LED on and off\n");
        printf("hold pause button down for 2 seconds to exit\n");
        // Keep looping until state changes to EXITING
        rc_set_state(RUNNING);
        int i = 0;
        while(rc_get_state()!=EXITING){

                // the main code, if going just do this stuff
                if(rc_get_state()==RUNNING){
                  // turn on leds to signal we've started
                  rc_led_set(RC_LED_GREEN, 1);
                  rc_led_set(RC_LED_RED, 0);
                  // get current position
                  currentPos = rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS);
                  printf("Curretn position: %d\n going to position: %d\n", currentPos,projectedPos[i]);
		  // see if need to change position
                  // getProjectedPos(&projectedPos);
		  printf("\r");
		  fflush(stdout);
                  // now move motor if needed
                  moveMotor(currentPos, projectedPos[i++]);
		  if(i == 10) i = 0;
                }
                // end of actual code, now in hibernate
                else{
                        rc_led_set(RC_LED_GREEN, 0);
                        rc_led_set(RC_LED_RED, 1);
                        adas_motor_free_spin();
                }
                // always sleep at some point
                // wait 1/25 sec to mimic refresh rate
                rc_usleep(DIVISION);
        }
        // turn off LEDs and close file descriptors
        rc_led_set(RC_LED_GREEN, 0);
        rc_led_set(RC_LED_RED, 0);
        rc_led_cleanup();
        rc_button_cleanup();    // stop button handlers
        adas_motor_cleanup();
        rc_remove_pid_file();   // remove pid file LAST
        return 0;
}



/*
 * gets the next projected pos from whatever source
 * should be the pipe from the algorithm
 * only writes the position once every MOTOR_DRIVER_READ_HZ
 * input: pointer to the int holding the projected position
void getProjectedPos(int* projectedPos){
  uint64_t currentTime = rc_nanos_since_boot();
  // only get the shit if the refresh time is good
  if(currentTime - lastReadTime <= MOTOR_DRIVER_READ_HZ){
    if(scanf("%d", &number) == EOF) fprintf(stderr, "There was an error reading from the pipe\n"); // read from buffer
    *projectedPos = 0; // change to position to move to
    // update time
    lastReadTime = currentTime;
  }
}


 */
/*
 * initialize everything
 * signal handler
 * button
 * motor driver
 * encoder
 * read flag
 *
 */
void Init(){
  if(!initFlag){
    // make sure another instance isn't running
    // if return value is -3 then a background process is running with
    // higher privaledges and we couldn't kill it, in which case we should
    // not continue or there may be hardware conflicts. If it returned -4
    // then there was an invalid argument that needs to be fixed.
    if(rc_kill_existing_process(2.0)<-2) return -1;
    // start signal handler so we can exit cleanly
    if(rc_enable_signal_handler()==-1){
            fprintf(stderr,"ERROR: failed to start signal handler\n");
            return -1;
    }
    // initialize pause button
    if(rc_button_init(RC_BTN_PIN_PAUSE, RC_BTN_POLARITY_NORM_HIGH,
                                            RC_BTN_DEBOUNCE_DEFAULT_US)){
            fprintf(stderr,"ERROR: failed to initialize pause button\n");
            return -1;
    }

    // initialize motor
    if(adas_motor_init()){
      fprintf(stderr,"ERROR: failed to initialize motor\n");
      return -1;
    }

    // initialize encoder first
    if(rc_encoder_eqep_init()){
          fprintf(stderr,"ERROR: failed to run rc_encoder_eqep_init\n");
          return -1;
    }

    // initialize time for reading from buffer
    lastReadTime = rc_nanos_since_boot();
    pthread_t getInput;
    initFlag = 1;
    }
}

/**
 * continuous loop to check position of motor and needed pos
 * call to move motor or stay in place
 * @params: current pos of motor, projected pos of motor
 */
void moveMotor(int currentPos, int projectedPos){
  double difference = currentPos - projectedPos;
  if(outsideMargin(currentPos, projectedPos)){
	  printf("im moving bitch");
    adas_motor_set(difference);
  }
  else if(!outsideMargin(currentPos, projectedPos)){
	  adas_motor_free_spin();
  }

}

/**
 * whether or not the current position is within the margin
 * i.e. whether or not to stop the motor (think of it as a bit mask)
 * call as if(outsideMargin) fucking move;
 * else fucking stop
 * input: the current position, the projected position
 * 
 * output: 0 if need to move stillx 1 if within margin
*/ 
int outsideMargin(int current, int projected){
  return !(current - projected < MOTOR_DRIVER_MARGIN
        && current - projected > -MOTOR_DRIVER_MARGIN
         || current > MOTOR_DRIVER_MAX
        || current < -MOTOR_DRIVER_MAX);
}

/**
 * Make the Pause button toggle between paused and running states.
 */
void on_pause_release()
{
        if(rc_get_state()==RUNNING)     rc_set_state(PAUSED);
        else if(rc_get_state()==PAUSED) rc_set_state(RUNNING);
        return;
}
/**
* If the user holds the pause button for 2 seconds, set state to EXITING which
* triggers the rest of the program to exit cleanly.
**/
void on_pause_press()
{
        int i;
        const int samples = 100; // check for release 100 times in this period
        const int us_wait = 2000000; // 2 seconds
        // now keep checking to see if the button is still held down
        for(i=0;i<samples;i++){
                rc_usleep(us_wait/samples);
                if(rc_button_get_state(RC_BTN_PIN_PAUSE)==RC_BTN_STATE_RELEASED) return;
        }
        printf("long press detected, shutting down\n");
        rc_set_state(EXITING);
        return;
}
