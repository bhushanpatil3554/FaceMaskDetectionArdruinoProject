#include <Servo.h>
#include <SoftwareSerial.h>
SoftwareSerial MyBlue(2, 3); // RX | TX
int ledPinOpen = 7; //definition digital 8 pins as pin to control the LED
int ledPinClose = 6;
Servo myservo;
int flag = -1;
int flag_previous = -1;
void setup()
{
  myservo.attach(9);
  pinMode(ledPinOpen, OUTPUT);   //Set the digital 8 port mode, OUTPUT: Output mode
  pinMode(ledPinClose, OUTPUT);
  Serial.begin(9600);
  MyBlue.begin(9600);
  Serial.println("Ready to connect\nDefualt password is 1234 or 000");
myservo.write(135); 
digitalWrite(ledPinClose, HIGH);
}
void loop()
{

int angle = myservo.read(); 
//Serial.println(angle);

  if (MyBlue.available())
    flag = MyBlue.read();
  Serial.println(flag);

  if (flag_previous != flag) {
    flag_previous = flag;

    if (flag == 79)
    {

digitalWrite(ledPinClose, LOW);
      digitalWrite(ledPinOpen, HIGH);
      Serial.println("LED On");

      //for (int pos = 90; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        myservo.write(45);              // tell servo to go to position in variable 'pos'
       // delay(15);
     // }
    }
    else if (flag == 67)
    {
      digitalWrite(ledPinOpen, LOW);
      digitalWrite(ledPinClose, HIGH);
      Serial.println("LED Off");
     // for (int pos = 180; pos >= 90; pos -= 1) { // goes from 180 degrees to 0 degrees
        myservo.write(135);              // tell servo to go to position in variable 'pos'
        //delay(15);                       // waits 15ms for the servo to reach the position
      //}
    }else{
            

    }

  }
}
