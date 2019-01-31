#include "threadTalk.h"
#include <stdlib.h>
#include <stdio.h>

	/*
	 * start the thread for getting new position values
	 * input: allocated memory pointer to hold the position
	 * and whether to finish the thread or not. 1 for finished 0 not
	 * return: the id of the created thread or 0 if it fucked up
	*/
	args_t *startThread(){
	  // create arguments
	  args_t *arguments = (args_t*) malloc(sizeof(args_t));
	  arguments->projectedPos = calloc(1, sizeof(int));
	  arguments->thread = calloc(1, sizeof(pthread_t));
	  arguments->exit = calloc(1, sizeof(int)); //sets exit to 0

	  // start thread
	  if(pthread_create(arguments->thread, NULL, &getProjectedPos, arguments)){
	    fprintf(stderr, "ERROR: failed to start positon listener thread\n");
	    return 0;
	  }

	  return arguments;
	}

	/*
	* gets the next projected pos from whatever source
	* should be the pipe from the algorithm
	* only writes the position once every MOTOR_DRIVER_READ_HZ
	* input: pointer to the int holding the projected position
	*/
	void *getProjectedPos(void *argv){
	  args_t *input = argv;
	  printf("started the threadshit boi the finished flag is %d \n", *input->exit);
  int number;
  // just run fucker while input args says so
  while(!*input->exit){
    // just pull in stuff from the input
    if(scanf("%d", &number) == EOF) fprintf(stderr, "There was an error reading from the pipe\n"); // read from buffer
    // only change the input if it differs (minnimize lock time)
    if(number != *input->projectedPos){
     *input->projectedPos = number; // change to position to move to
     printf("changed the number boi\n");
    }
  }
  // exit cleanly
  pthread_exit(NULL);
}
