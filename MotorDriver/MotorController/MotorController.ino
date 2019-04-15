#include <MotorController.h>

#define ENCODERA 23 // channel A
#define ENCODERB 22 // channel B
#define MOTORPWM 16
#define MOTORDIR 15
#define MOTORGND 17 

// initialize motor controller for adas
MotorController adas(ENCODERA, ENCODERB, MOTORPWM, MOTORDIR, MOTORGND);

void getNumber();
String inputNumber = "";


bool shit, retract = false;
int projectedPosition = 0
;
int temp, pos;
void setup(){
  Serial1.begin(115200);
  Serial1.println("shit fuck");
  inputNumber.reserve(200);
  temp = 0;
  pos = 0;
}


void loop() {
  getNumber();

  if(shit) {
    Serial1.write("the fucking projected pos is ");
    Serial1.println(projectedPosition);
//    delay(500);
    adas.attemptPosition(projectedPosition * 100);
    
    shit = false;
  }
  if (retract){
    
    // fully retract motor
    adas.motorDone();
    exit(0);
  }
  else{
//    temp = adas.position();
//    if(temp != pos){
//      Serial1.println(temp);
//      pos = temp;
//    }
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
void getNumber() {
  delay(5);
  char var;
  if (Serial1.available() > 0) {
    while(Serial1.available()){
      var = (char) Serial1.read();
    }
    //adas.stopMotor();
    // get the new byte:
//    Serial1.println("hello");
//    Serial1.flush();
//    if(isdigit(inputNumber[0])){
//      int temp, number = 0;
//      for(int i = 0; inputNumber[i] != '\n'; i++){
//        temp = inputNumber[i] - '0';
//        number *= 10;
//        number += temp;
//      }
//      Serial1.println("got");
      if (var == 'e'){
        retract = true;
        return;  
      }
      projectedPosition = var - '0';
      shit=true;
      return;
    }
    
//    // if the incoming character is a newline
//    // update the global projected position
//    else 
    
    // signify the end of the program and stop everything
//    else if (inputNumber[0] == 'e'){
//      
//    }
//  }
}
