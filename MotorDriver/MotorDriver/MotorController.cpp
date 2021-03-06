#include "ADASmotor.h"
#include "MotorController.h"
#include <Encoder.h>
#define MOTOR_DRIVER_MARGIN 5 //margin to get motor to within
#define MOTOR_DRIVER_MAX 900 // maximum deployment


// constructor function
// take in an initialized encoder and motor object
MotorController::MotorController(int encoderA, int encoderB, int motorPwm,
int motorDir, int motorGnd):
encoder(encoderA, encoderB), motor(motorPwm, motorDir, motorGnd)
{
  initFlag = true;
  pinMode(20, OUTPUT);
  Serial.println("fucker");
}


// no loop EVERYTHING ONLY GETS EXECUTED ONCE PER CALL
// just go through and update movement position of motor if needed
// essentially just updates state of motor movement
// input: position to move motor to
void MotorController::attemptPosition(int pos){
/*  int currentPos = (int) encoder.read(); // get current positon
  bool direction;
  // if im outside the margin of where I wanna go
  // then move
  //for (size_t i = 0; i < 25 && outsideMargin(currentPos, pos); i++) {
  while (outsideMargin(currentPos, pos)) {
    Serial.println("shit");
    // if where we need to go is forward of where we are, true
    // otherwise false
    if (pos - currentPos < 0) direction = true;
    else direction =  false;
    // deploy to that position at full speed
    motor.moveMotor(direction, 1.0);
    currentPos = (int) encoder.read();
    delay(5);
  }
  // otherwise if within margin halt the motor
  for (size_t i = 0; i < 10; i++) {
    Serial.println("made it");
  }
  motor.stopMotor();*/

  int currentPos = (int) encoder.read(); // get current positon
  bool direction;
  // bool out =;
  // if im outside the margin of where I wanna go
  // then move
  if (outsideMargin(currentPos, pos)) {
    // if where we need to go is forward of where we are, true
    // otherwise false
    direction = (pos - currentPos) > 0 ? false : true;
    // deploy to that position at full speed
    digitalWrite(20, HIGH);
    motor.moveMotor(direction, 1.0);
  }

  // otherwise if within margin halt the motor
  else{
    motor.stopMotor();
    digitalWrite(20,LOW);
  }
  return;
}

int MotorController::position(){
  return (int) encoder.read();
}

// fully retract motor to 0 position

void MotorController::motorDone(){
  int currentPos = (int) encoder.read();
  // if where we need to go is forward of where we are, true
  // otherwise false
  bool direction = (0 - currentPos) > 0 ? false : true;
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
 * i.e. output 1 if i need to keep going or my projected position is ok to move towards
*/
bool MotorController::outsideMargin(int current, int projected){
	int difference = current-projected;
// am i within the margin
//	0 = reached the margin so stop
  int outsideMargin = !(difference < MOTOR_DRIVER_MARGIN && difference > -MOTOR_DRIVER_MARGIN);

  // 1 if im under the maximum range
  int withinMax = current <= MOTOR_DRIVER_MAX  && current >= 0;

// only go if im under the maximum range or im trying to turn backward
  int allowGo = (withinMax || (current <= 0 && projected > current)
	       	|| (current >= MOTOR_DRIVER_MAX && projected < current));
//	printf("inmargin: %d, inMax: %d", inMargin, inMax);
  return outsideMargin && allowGo;
}
