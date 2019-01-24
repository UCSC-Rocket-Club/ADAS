/**
 * @file rc_project_template.c
 *
 * This is meant to be a skeleton program for Robot Control projects. Change
 * this description and file name before modifying for your own purpose.
 */

// takes in stdin from algorithm for positon to move to
// outputs encoder positon on every time we refresh data

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include "motor.h" //include adas motor shit

#define MOTOR_DRIVER_MARGIN 2 // margin of postition to stop motor and lock in place
#define MOTOR_DRIVER_CPR 1120 // pulses per revolution of output shaft
#define MOTOR_DRIVER_MAX  1120/4 // pulses in max deployment, i.e. stay under this pulse the motor outputs 1120 pulses for 1 revolution
#define MOTOR_DRIVER_ENCODER_POS 3 // encoder port we're plugging into
#define MOTOR_DRIVER_READ_HZ 1000000000/25 // time in ns/periods between each cycle i.e. refresh rate

// function declarations
void on_pause_press();
void on_pause_release();
int Init();
pthread_t startThread(int *position, int *finished);
int outsideMargin(int current, int projected);
void moveMotor(int currentPos, int projectedPos);
void *getProjectedPos(void *argv);

// struct to pass data to thread
typedef struct args_t{
  int *projectedPos;
  pthread_t *input;
  int *finished;
}args_t;


// fake encoder positions to test functions
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
        // thread to get shit
        pthread_t talkThread;
        int currentPos;
	      int* projectedPos = calloc(1, sizeof(int));
        int* finished = calloc(1, sizeof(int));

        // initilize everything
        if(Init()) {
          fprintf(stderr, "Error in initialize\n");
          fflush(stderr);
          return -1;
        }

        // start thread
        talkThread = startThread(projectedPos, finished);
        if(!talkThread){
          fprintf(stderr, "error starting thread\n");
          fflush(stderr);
          return -1;
        }

        /* the projected position is constantly being updated in the background
         * by the other thread
         * therefore just poll the current location and set to the new location when needed
         * set the projected location to a temporary varriable to pass in to make the position change atomic
         */

        int atomicProjectedPos;

        while(rc_get_state() !=  EXITING){

                // the main code, if going just do this stuff
                if(rc_get_state()==RUNNING){
                  // turn on leds to signal we've started
                  rc_led_set(RC_LED_GREEN, 1);
                  rc_led_set(RC_LED_RED, 0);
                  // get current position
                  currentPos = rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS);
                  atomicProjectedPos = *projectedPos;
                  // execute move motor
                  moveMotor(currentPos, atomicProjectedPos);
                  printf("current position is: %d\n", currentPos);
                  rc_usleep(1000);
                  // printf("Curretn position: %d\n going to position: %d\n", currentPos,projectedPos);
		              // see if need to change position
		              fflush(stdout);
                }
                // end of actual code, now in hibernate
                else{
                        rc_led_set(RC_LED_GREEN, 0);
                        rc_led_set(RC_LED_RED, 1);
                        adas_motor_free_spin();
                }
                // always sleep at some point
	}

        // turn off LEDs and close file descripto 	rs
        rc_led_set(RC_LED_GREEN, 0);
        rc_led_set(RC_LED_RED, 0);
	      *finished = 1; // close thread talker
        rc_led_cleanup();
	//char *error[200];
	//if(pthread_join(talkThread, error)) fprintf(stderr, "error with thread closing: %s", error); // close thread
        rc_button_cleanup();    // stop button handlers
        adas_motor_cleanup();
        rc_remove_pid_file();   // remove pid file LAST
        free(finished);
        free(projectedPos);
        return 0;
}

/*
 * initialize everything
 * signal handler
 * button
 * motor driver
 * encoder
 * read flag
 *
 * input: pointer to position int to fill with position data,
 * 	finished int pointer to exit thread cleanly
 * 	thread pointer to hold onto talkThread
 *
 * output: -1 for an error, 0 if eveything initialized correctly
 */
int Init(){
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

    // make PID file to indicate your project is running
    // due to the check made on the call to rc_kill_existing_process() above
    // we can be fairly confident there is no PID file already and we can
    // make our own safely.
    rc_make_pid_file();

    // Assign functions to be called when button events occur
    rc_button_set_callbacks(RC_BTN_PIN_PAUSE,on_pause_press,on_pause_release);

    printf("\nPress and release pause button to turn green LED on and off\n");
    printf("hold pause button down for 2 seconds to exit\n");
    // Keep looping until state changes to EXITING
    rc_set_state(RUNNING);

    initFlag = 1;
    }
   return 0;
}

/**
 * continuous loop to check position of motor and needed pos
 * call to move motor or stay in place
 * @params: current pos of motor, projected pos of motor
 */
void moveMotor(int currentPos, int projectedPos){
  double difference = currentPos - projectedPos;
//  printf("in movemotor bitch");
  while(outsideMargin(currentPos, projectedPos)){
//	  printf("im moving bitch");
    adas_motor_set(difference);
    currentPos = rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS);
  }
//	  adas_motor_brake(difference);
  adas_motor_free_spin();
	  // need to free spin, break function makes motor spaz out
}

/*
 * start the thread for getting new position values
 * input: allocated memory pointer to hold the position
 * and whether to finish the thread or not. 1 for finished 0 not
 * return: the id of the created thread or null if it fucked up
*/
pthread_t startThread(int *position, int *finished){
  // createa pointer to a thread id
  pthread_t *thread = calloc(1, sizeof(pthread_t));

  // create arguments
  args_t *arguments = (args_t*) malloc(sizeof(args_t));
  arguments->projectedPos = position;
  *finished = 0;
  arguments->finished = finished;

  // start thread
  if(pthread_create(thread, NULL, &getProjectedPos, arguments)){
    fprintf(stderr, "ERROR: failed to start positon listener thread\n");
    return 0;
  }

  return *thread;
}

/*
* gets the next projected pos from whatever source
* should be the pipe from the algorithm
* only writes the position once every MOTOR_DRIVER_READ_HZ
* input: pointer to the int holding the projected position
*/
void *getProjectedPos(void *argv){
  args_t *input = argv;
printf("started the threadshit boi the finished flag is %d \n", *input->finished);
  int number;
  // just run fucker while input args says so
  while(!*input->finished){
	  printf("in pos shit boi \n");
    // just pull in stuff from the input
    if(scanf("%d", &number) == EOF) fprintf(stderr, "There was an error reading from the pipe\n"); // read from buffer
    // only change the input if it differs (minnimize lock time)
    if(number != *input->projectedPos){
     *input->projectedPos = number; // change to position to move to
     printf("changed the number boi\n");
      // log encoder data
      if(initFlag) fprintf(stdout, "%d", rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS));
      // flush to out
      fflush(stdout);
    }
  }
  // exit cleanly
  pthread_exit(NULL);
}

/**
 * whether or not the current position is within the margin
 * i.e. whether or not to stop the motor (think of it as a bit mask)
 * call as if(outsideMargin) fucking move;
 * else fucking stop
 * input: the current position, the projected position
 *
 * output: 1 if im outside margin and need to move, 0 otherwise
*/
int outsideMargin(int current, int projected){
	int difference = current-projected;
//	printf("difference is: %d", difference);
// am i within the margin
//	0 = reached the margin so stop
  int inMargin = !(difference < MOTOR_DRIVER_MARGIN && difference > -MOTOR_DRIVER_MARGIN);

  // 1 if im under the maximum range
  int inMax =  current < MOTOR_DRIVER_MAX
        && current > -MOTOR_DRIVER_MAX;
// only go if im under the maximum range or im trying to turn backward
  int allowGo = (inMax || (current < 0 && projected > current)
	       	|| !(current < 0 && projected > current));
//	printf("inmargin: %d, inMax: %d", inMargin, inMax);
  return inMargin && allowGo;
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
