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
    Motor(int pwm, int dir);
    Motor(int pwm, int dir, int gnd);
    void moveMotor(int dir, float speed);
    void stopMotor();
  private:
    int pwmPin;
    int dirPin;
};

#endif
