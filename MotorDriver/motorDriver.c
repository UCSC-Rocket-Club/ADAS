/**
 * @file rc_project_template.c
 *
 * This is meant to be a skeleton program for Robot Control projects. Change
 * this description and file name before modifying for your own purpose.
 */
<<<<<<< HEAD
#include <stdio.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include "motor.h" //include adas motor shit

#define MARGIN 5 // margin of postition to stop motor and lock in place
#define DIVISION 40000 // time between each cycle i.e. refresh rate
// function declarations
void on_pause_press();
void on_pause_release();
int inMargin(int current, int projected);
void moveMotor(int currentPos, int projectedPos);

// fake encoder positions to test functions
static int fakeProjected[] = {100,100,100};
static int fakeCurrent[] = {0,100,-100};
=======

// takes in stdin from algorithm for positon to move to
// outputs encoder positon on every time we refresh data

#include <stdio.h>
#include <stdlib.h>
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

// function declarations
void on_pause_press();
void on_pause_release();
int Init(int *position, int *finished, pthread_t *thread_id);
int outsideMargin(int current, int projected);
void moveMotor(int currentPos, int projectedPos);
void *getProjectedPos(void *argv);

// struct to pass data to thread
typedef struct {
  int *projectedPos;
  pthread_t *input;
  int *finished;
}args;


// fake encoder positions to test functions
static int initFlag = 0; // initialize flag
>>>>>>> origin/MotorDriver
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
<<<<<<< HEAD
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
        // Assign functions to be called when button events occur
        rc_button_set_callbacks(RC_BTN_PIN_PAUSE,on_pause_press,on_pause_release);
        adas_motor_init();
        // make PID file to indicate your project is running
        // due to the check made on the call to rc_kill_existing_process() above
        // we can be fairly confident there is no PID file already and we can
        // make our own safely.

        int directionPin = 2;
        int speed = 5;
        int currentPos = 5;
        int projectedPos = 6;
        int pulse = 0;


        rc_make_pid_file();
        printf("\nPress and release pause button to turn green LED on and off\n");
        printf("hold pause button down for 2 seconds to exit\n");
        // Keep looping until state changes to EXITING
        rc_set_state(RUNNING);
        int i = 0;
        while(rc_get_state()!=EXITING){

                // do things based on the state
                if(rc_get_state()==RUNNING){
                  moveMotor(fakeCurrent[i], fakeProjected[i++]);
                  if (i == sizeof(fakeCurrent)/sizeof(fakeCurrent[0])) i = 0;
                }
=======
        // thread to get shit
        pthread_t talkThread;
        int currentPos, finished;
	       int projectedPos = 100;
        // initilize everything
        if(Init(&projectedPos, &finished, &talkThread)) {
          fprintf(stderr, "Error in initialize\n");
          fflush(stdout);
          return -1;
        }
        int go = 1;
        // Assign functions to be called when button events occur
        rc_button_set_callbacks(RC_BTN_PIN_PAUSE,on_pause_press,on_pause_release);
	   printf("going to %d\n", projectedPos);

	char buffer[100];
        while(rc_get_state() != EXITING){
          // if(scanf("%d", &projectedPos)){
	    fgets(buffer, 100, stdin);
	    printf("%s", buffer);
	    projectedPos = atoi(buffer);
            currentPos = rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS);
            moveMotor(currentPos, projectedPos);
            printf("%d\n", rc_encoder_eqep_read(MOTOR_DRIVER_ENCODER_POS));
            rc_usleep(10000);
          //}

        }

        /*while(go){

                // the main code, if going just do this stuff
                if(rc_get_state()==RUNNING){
                  // turn on leds to signal we've started
                  rc_led_set(RC_LED_GREEN, 1);
                  rc_led_set(RC_LED_RED, 0);
                  // get current position
                  // printf("Curretn position: %d\n going to position: %d\n", currentPos,projectedPos);
		                // see if need to change position
                  // getProjectedPos(&projectedPos);
		                // printf("\r");
		                  fflush(stdout);
                  // now move motor if needed
                }
                // end of actual code, now in hibernate
>>>>>>> origin/MotorDriver
                else{
                        rc_led_set(RC_LED_GREEN, 0);
                        rc_led_set(RC_LED_RED, 1);
                        adas_motor_free_spin();
                }
                // always sleep at some point
<<<<<<< HEAD
                // wait 1/25 sec to mimic refresh rate
                rc_usleep(DIVISION);
        }
        // turn off LEDs and close file descriptors
        rc_led_set(RC_LED_GREEN, 0);
        rc_led_set(RC_LED_RED, 0);
        rc_led_cleanup();
=======
        */
        // turn off LEDs and close file descripto 	rs
        rc_led_set(RC_LED_GREEN, 0);
        rc_led_set(RC_LED_RED, 0);
	finished = 1; // close thread talker
        rc_led_cleanup();
	//char *error[200];
	//if(pthread_join(talkThread, error)) fprintf(stderr, "error with thread closing: %s", error); // close thread
>>>>>>> origin/MotorDriver
        rc_button_cleanup();    // stop button handlers
        adas_motor_cleanup();
        rc_remove_pid_file();   // remove pid file LAST
        return 0;
}

<<<<<<< HEAD
=======

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
int Init(int *position, int *finished, pthread_t *thread_id){
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

    pthread_t thread;
    *thread_id = thread;
    // create arguments

    args *arguments = (args*) malloc(sizeof(args));
    arguments->projectedPos = position;
    *finished = 0;
    arguments->finished = finished;

    /*if(pthread_create(&thread, NULL, getProjectedPos, arguments)){
      fprintf(stderr, "ERROR: failed to start positon listener thread\n");
      return -1;
    }*/

    printf("\nPress and release pause button to turn green LED on and off\n");
    printf("hold pause button down for 2 seconds to exit\n");
    // Keep looping until state changes to EXITING
    rc_set_state(RUNNING);

    initFlag = 1;
    }
   return 0;
}

>>>>>>> origin/MotorDriver
/**
 * continuous loop to check position of motor and needed pos
 * call to move motor or stay in place
 * @params: current pos of motor, projected pos of motor
 */
void moveMotor(int currentPos, int projectedPos){
  double difference = currentPos - projectedPos;
<<<<<<< HEAD
  if(!inMargin(currentPos, projectedPos)){
    adas_motor_set(difference);
  }
  else if(inMargin(currentPos, projectedPos)){
    adas_motor_brake(difference);
  }

}

/**
 * get the speed to turn the motor
 * input: the current position, the projected position
 * output: 1 if need to move still 0 if within margin
*/
int inMargin(int current, int projected){
  return (current - projected < MARGIN && current - projected > -MARGIN );
=======
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
* gets the next projected pos from whatever source
* should be the pipe from the algorithm
* only writes the position once every MOTOR_DRIVER_READ_HZ
* input: pointer to the int holding the projected position
*/
void *getProjectedPos(void *argv){
  args *input = (args*) argv;
printf("started the threadshit boi the finished flag is %d \n", input->finished);
  // get start time
  uint64_t startTime = rc_nanos_since_boot();
  uint64_t lastReadTime = rc_nanos_since_boot();
  int number;
  // just run fucker
  while(!input->finished){
	  printf("in pos shit boi \n");
    // just pull in stuff from the input
    if(scanf("%d", &number) == EOF) fprintf(stderr, "There was an error reading from the pipe\n"); // read from buffer
    // only get the shit if the refresh time is good
    if(rc_nanos_since_boot() - lastReadTime <= MOTOR_DRIVER_READ_HZ){
     *(input->projectedPos) = number; // change to position to move to
     printf("changed the number boi\n");
      // update time
      lastReadTime = rc_nanos_since_boot();
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
	difference = (difference < 0)? -1*difference: difference;
//	printf("difference is: %d", difference);
//	reached the margin so stop
  int inMargin = !(difference < MOTOR_DRIVER_MARGIN);

  // in the max range, return 1 if i realize my mistake and want to turn backward, otherwise 0
  int inMax =  current < MOTOR_DRIVER_MAX
        && current > -MOTOR_DRIVER_MAX;
  int allowGo = (inMax || !inMax && (
                (current < 0 && projected > current)
	       	|| (current > 0 && projected < current)))? 1: 0;
//	printf("inmargin: %d, inMax: %d", inMargin, inMax);
  return inMargin && allowGo;
>>>>>>> origin/MotorDriver
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
