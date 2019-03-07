#include <ADASMotor.h>
#include <MotorController.h>
#include <Encoder.h>

int projectedPosition = 0;
boolean retract = false;


void setup() {
  Serial.begin(9600);
  Encoder encoder(22, 23);
  Motor motor(16, 15, 17);
  // initialize motor controller
  MotorController adas(encoder, motor);
}

void loop() {
  if (retract){
    // fully retract motor
    adas.motorDone();
    exit();
  }
  else{
    attemptPosition(projectedPosition);
  }
  

}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.

  goes through the current serial buffer and parses data
  if its numbers, get the most recent number (numbers delminated by newline)
  if its an e, this signifies the end of the program so retract and be done with it

  after this loop the projectedPosition global varriable has the last (most recent)
  inputted number from the serial

  credit to FUCKING CE12 FOR HOW TO PARSE AN INT IN C COMMUNICATION WHO FUCKING KNEW THIS SHIT
  WAS GOING TO END UP BEING USEFUL HOLY FUCK MAX DUNNEEEEEEEE
*/
void serialEvent() {
  int temp, number = 0;
  while (Serial.available() > 0) {
    // get the new byte:
    char inChar = (char)Serial.read();
    if(isdigit(inChar)){
      temp = atoi(inChar);
      number *= 10; // shift a tens place to add in new number
      number += temp; // add in temp number
    }
    
    // if the incoming character is a newline
    // update the global projected position
    else if (inChar == '\n') {
      projectedPosition = number;
    }
    
    // signify the end of the program and stop everything
    else if (inChar == 'e'){
      retract = true;
    }
  }
}
