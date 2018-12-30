#include<Servo.h>

int arm_servo = 10;

Servo arm;

void setup()
{
   // put your setup code here, to run once:
   Serial.begin(9600);
   arm.attach(arm_servo);
}

void loop()
{
   // put your main code here, to run repeatedly:
   for (int i = 0; i < 5; i ++)
   {
      arm.write(i*45);
      delay(500);
      Serial.println(i*45);
   }
   for (int i = 4; i >= 0; i --)
   {
      arm.write(i*45);
      delay(500);
      Serial.println(i*45);
   }
}
