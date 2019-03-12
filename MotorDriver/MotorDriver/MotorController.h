/*
MotorController.h - Library for ADAS MOTOR DUMBASS.
Created by Gavin Chen 3/5/19.
Released into the public domain.
*/
#ifndef MotorController_h
#define MotorController_h

#include "Arduino.h"
#include "ADASmotor.h"
#include <Encoder.h>


class MotorController
{
  public:

    // constructor function, takes in encoder and motor object
    // cant really do initialization checks in this shit
    // so assumes they're initialized correctly (bad practice i know get off my ass)
    MotorController(int encoderA, int encoderB, int motorPwm, int motorDir, int motorGnd);

    // attempt to move to a position
    // THERE IS NO LOOPING IN THIS FUNCTION
    // think of it as updating the current future of the motor
    // there is a slight race condition, if the motor isn't in the margin
    // at the time this function is called (i.e. it zips past the projected pos)
    // there will be no stopping of the motor
    // will automatically stop if the motor is outside of the limits though
    void attemptPosition(int pos);

    // fully retract motor
    // loops, nothing else will be done to the motor until it is fully retracted
    void motorDone();

    // return motor position
    int position();
  private:
    Encoder encoder;
    Motor motor;
    bool initFlag = false;
    bool outsideMargin(int current, int projected);

};

#endif
