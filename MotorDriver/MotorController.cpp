#include "ADASmotor.h"
#include <Encoder.h>
#define MOTOR_DRIVER_MARGIN = 2 //margin to get motor to within
#define MOTOR_DRIVER_MAX = 900 // maximum deployment


// constructor function
// take in an initialized encoder and motor object
MotorController::MotorController(Encoder *encoder, Motor *motor){
  encoder = encoder;
  motor = motor;
  initFlag = true;
}

// no loop EVERYTHING ONLY GETS EXECUTED ONCE PER CALL
// just go through and update movement position of motor if needed
// essentially just updates state of motor movement
// input: position to move motor to
void MotorController::attemptPosition(int pos){
  int currentPos = (int) encoder.read(); // get current positon
  // if im outside the margin of where I wanna go
  // then move
  if (outsideMargin(currentPos, pos)) {
    // if where we need to go is forward of where we are, true
    // otherwise false
    boolen direction = (pos - currentPos) > 0 ? true : false;
    // deploy to that position at full speed
    motor.moveMotor(direction, 1.0);
  }

  // otherwise if within margin halt the motor
  motor.stopMotor();
  return;
}

// fully retract motor to 0 position

void MotorController::motorDone(){
  int currentPos = (int) encoder.read();
  // if where we need to go is forward of where we are, true
  // otherwise false
  boolen direction = (0 - currentPos) > 0 ? true : false;
  // deploy to 0 at full speed
  motor.moveMotor(direction, 1.0);

  // while we aren't at zero just keep trying
  while(outsideMargin(currentPos, 0)){
    currentPos = (int) encoder.read();
  }
  // we're at 0, stop everything we're done
  motor.stopMotor();

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
boolean MotorController::outsideMargin(int current, int projected){
	int difference = current-projected;
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
