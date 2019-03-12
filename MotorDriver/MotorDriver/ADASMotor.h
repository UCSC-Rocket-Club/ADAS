/*
  ADASmotor.h - Library for ADAS MOTOR DUMBASS.
  Created by Gavin Chen 3/5/19.
  Released into the public domain.
*/
#ifndef ADASmotor_h
#define ADASmotor_h


#include "Arduino.h"

class Motor
{
  public:
    //optionally configure motor driver gnd pin,
    //be careful gnd pin doesnt sink too much current
    Motor(int pwm, int dir, int gnd);

    //sets motor to move in a direction at a speed
    // once set the motor will just continue to move there
    //input: direction and speed
    //dir = high (true) counter clockwise (deploy), else other
    //speed = normalized between 0-1, a percentage. if above or below sets to
    // 1 or 0 respectively
    void moveMotor(boolean dir, float speed);

    //just stops the motor
    void stopMotor();
  private:
    int pwmPin;
    int dirPin;
    bool initFlag = false;
    int currentDir = 0;
    float currentSpeed = 0;
};

#endif
