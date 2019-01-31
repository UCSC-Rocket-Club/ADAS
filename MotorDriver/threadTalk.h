#ifndef THREADTALKER
#define THREADTALKER

#include <pthread.h>
#include <string.h>

// struct to pass data to thread
typedef struct args_t{
  int *projectedPos;
  pthread_t *thread;
  int *exit;
}args_t;

/*
 * start the thread for getting new position values
 * input: allocated memory pointer to hold the position
 * and whether to finish the thread or not. 1 for finished 0 not
 * return: the id of the created thread or 0 if it fucked up
*/
args_t *startThread();

/*
* gets the next projected pos from whatever source
* should be the pipe from the algorithm
* only writes the position once every MOTOR_DRIVER_READ_HZ
* input: pointer to the int holding the projected position
*/
void *getProjectedPos(void *argv);

#endif
