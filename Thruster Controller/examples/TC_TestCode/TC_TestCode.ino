#include <Servo.h>

void setup() {
pinMode(7, OUTPUT); // Configure pin 7 as an Output
pinMode(8, OUTPUT); // Configure pin 8 as an Output
digitalWrite(7, HIGH); // Initialize pin 7 
digitalWrite(8, HIGH); // Initialize pin 8 
}

// Low on pin 7 means extend
// Low on pin 8 means retract
// High for both is stationary

void loop() {
  // Extend 
  digitalWrite(7, LOW);
  digitalWrite(8, HIGH);
  delay(3000);
  
  // Stop
  digitalWrite(7, HIGH);
  digitalWrite(8, HIGH);
  delay(3000); 
  
  // Retract
  digitalWrite(7, HIGH);
  digitalWrite(8, LOW);
  delay(3000); 

  // Stop 
  digitalWrite(7, HIGH);
  digitalWrite(8, HIGH);
  delay(3000); 
}