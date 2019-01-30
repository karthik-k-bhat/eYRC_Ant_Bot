#include<Servo.h>

int arm_servo = 8;

Servo arm;

void setup()
{
   // put your setup code here, to run once:
   Serial.begin(9600);
   arm.attach(arm_servo);
   arm.write(68);
}

void loop()
{
   // put your main code here, to run repeatedly:
   arm.write(90);
   delay(1000);
   arm.write(68);
   delay(1000);
}
