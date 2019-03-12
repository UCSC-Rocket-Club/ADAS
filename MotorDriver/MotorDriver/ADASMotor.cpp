#include "Arduino.h"
#include "ADASmotor.h"

Motor::Motor(int pwm, int dir, int gnd){
  pwmPin = pwm;
  dirPin = dir;
  pinMode(gnd, OUTPUT);
  pinMode(pwmPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  digitalWrite(gnd, LOW);
  initFlag = true;
}

// moves the motor specified by direction at specified speed
// input direction and speed percentatge (between 0 -1)
// moves the motor counter clockwise if direction is positive
// normalizes speed to between 0 and 1, if above or below it becomes
// 1 or 0 respectively
void Motor::moveMotor(boolean dir, float speed){
  if(!initFlag || (dir == currentDir && speed == currentSpeed)){
    // error checking and optimization
    return;
  }
  if(dir == true){
    digitalWrite(dirPin, HIGH);
    //Serial.println("pin is fucking high and it is %d");
  }
  else{
    digitalWrite(dirPin, LOW);
    //Serial.println("pin is fucking LOWWWWWWW");
  }
  if (speed < 0) speed = 0; // make speed a possitive number
  speed = speed > 1 ? 1 : speed; // keep speed below 1
  analogWrite(pwmPin, static_cast<int>(speed * 255.0));
  currentDir = dir;
  currentSpeed = speed;
}

// stops the motor
void Motor::stopMotor(){
  if (!initFlag) {// error checking
    return;
  }
  analogWrite(pwmPin, 0);
}
