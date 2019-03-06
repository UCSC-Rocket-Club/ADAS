#include "Arduino.h"
#include "ADASmotor.h"

boolean initFlag = false;

int currentDir = 0;
float currentSpeed = 0;

Motor::Motor(int pwm, int dir){
  pwmPin = pwm;
  dirPin = dir;
  pinMode(pwmPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
}

Motor::Motor(int pwm, int dir, int gnd);{
  pinMode(gnd, OUTPUT);
  digitalWrite(gnd, LOW);
  Motor(pwm, dir);
}

// moves the motor specified by direction at specified speed
// input direction and speed percentatge (between 0 -1)
// moves the motor counter clockwise if direction is positive
// normalizes speed to between 0 and 1, if above or below it becomes
// 1 or 0 respectively
Motor::moveMotor(int dir, float speed){
  if(!initFlag || dir == currentDir || speed == currentSpeed){
    // error checking and optimization
    return;
  }
  if(dir > 0){
    digitalWrite(dirPin, HIGH);
  }
  else{
    digitalWrite(dirPin, LOW);
  }
  if (speed < 0) speed *= 0; // make speed a possitive number
  speed = speed > 1 ? speed : 1; // keep speed below 1
  analogWrite(pwmPin, speed * 255);
}

// stops the motor
Motor::stopMotor(){
  if (!initFlag) {// error checking
    return;
  }
  digitalWrite(pwmPin, 0);
}
