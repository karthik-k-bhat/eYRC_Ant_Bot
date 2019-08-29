#include<Servo.h>

#define grabber_servo_pin 6
#define lift_servo_pin 9
#define camera_servo_pin 10

Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;

void setup()
{
   Serial.begin(9600);
   grabber_servo.attach(grabber_servo_pin);
   lift_servo.attach(lift_servo_pin);
   camera_servo.attach(camera_servo_pin);
   
   lift_servo.write(0);
   Serial.println("Initializing lift");
   delay(1000);
   grabber_servo.write(0);
   Serial.println("Initializing Grab");
   delay(2000);
   
   lift_servo.write(28);
   Serial.println("Going down");
   delay(1000);
   grabber_servo.write(180);
   Serial.println("Grabing");
   delay(2000);
   lift_servo.write(0);
   Serial.println("Going up");
   delay(100);
}

void loop()
{
   
}
