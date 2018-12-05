/**
 * @file rc_project_template.c
 *
 * This is meant to be a skeleton program for Robot Control projects. Change
 * this description and file name before modifying for your own purpose.
 */
#include <stdio.h>
#include <robotcontrol.h> // includes ALL Robot Control subsystems
#include "motor.h" //include adas motor shit

#define MARGIN 5 // margin of postition to stop motor and lock in place
// function declarations
void on_pause_press();
void on_pause_release();
boolean inMargin(int current, int projected);

// fake encoder positions to test functions
static int fakeProjected = [100,-100,-100];
static int fakeCurrent = [0,100,-100];
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
        rc_moto
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
                  moveMotor(fakeCurrent[i], fakeProjected[i]);
                  if (i == sizeof(fakeCurrent)/sizeof(fakeCurrent[0])) i = 0;
                  i++;
                }
                else{
                        rc_led_set(RC_LED_GREEN, 0);
                        rc_led_set(RC_LED_RED, 1);
                        adas_motor_free_spin();
                }
                // always sleep at some point
                // wait 1/25 sec to mimic refresh rate
                rc_usleep(40000);
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

/**
 * continuous loop to check position of motor and needed pos
 * call to move motor or stay in place
 * @params: current pos of motor, projected pos of motor
 */
void moveMotor(int currentPos, int projectedPos){
  int difference = currentPos - projectedPos;
  if(!inMargin(difference)){
    adas_motor_set((double)difference);
  }
  elseif(inMargin(difference)){
    adas_motor_brake((double)difference);
  }

}

/**
 * get the speed to turn the motor
 * input: the current position, the projected position
 * output: 1 if need to move still 0 if within margin
*/
boolean inMargin(int current, int projected){
  return (current - projected < MARGIN && current - projected > -MARGIN )
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
