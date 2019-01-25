#include <Servo.h>

#define buzzer_pin XX

#define red_led_pin XX
#define blue_led_pin XX
#define green_led_pin XX

#define camera_servo_pin XX
#define arms_servo_pin XX

#define line_sensor_left_pin XX
#define line_sensor_center_pin XX
#define line_sensor_right_pin XX

Servo camera_servo;
Servo arms_servo;


void setup() 
{
   Serial.begin(9600);
   
   camera_servo.attach(camera_servo_pin);
   arms_servo.attach(arms_servo_pin);

   pinMode(buzzer_pin, OUTPUT);
   
   pinMode(red_led_pin, OUTPUT);
   pinMode(blue_led_pin, OUTPUT);
   pinMode(green_led_pin, OUTPUT);
}


void loop()
{
   if (Serial.available)
   {
      char data = Serial.read();
   }
}


void line_sensor()
{
   int line_sensor_left_value = analogRead(line_sensor_left_pin);
   int line_sensor_center_value = analogRead(line_sensor_center_pin);
   int line_sensor_right_value = analogRead(line_sensor_right_pin);
   
}
