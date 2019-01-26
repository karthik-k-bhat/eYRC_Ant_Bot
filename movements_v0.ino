#include <Servo.h>
#define enable_left_motor 3
#define enable_right_motor 2
#define forward_left_motor 11
#define backward_left_motor 12
#define forward_right_motor 7
#define backward_right_motor 4
#define rpm 50
#define length_of_shaft 26.5
#define wheel_diameter 6.8 
#define left_sensor_pin A0
#define centre_sensor_pin A1
#define right_sensor_pin A2
#define grabber_servo_pin 6
#define lift_servo_pin 9
#define camera_servo_pin 10

Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;

String i="";
long int motor_start_time = 0;
long int motor_stop_time=0;
bool motor_turn_flag=0;
bool motor_start_flag=0;
int direction_moved = 0;

void setup()
{
   Serial.begin(9600);
   pinMode(enable_left_motor, OUTPUT);
   pinMode(enable_right_motor, OUTPUT);
   pinMode(forward_left_motor, OUTPUT);   
   pinMode(backward_left_motor, OUTPUT);
   pinMode(forward_right_motor, OUTPUT);
   pinMode(backward_right_motor, OUTPUT);
   grabber_servo.attach(grabber_servo_pin);
   lift_servo.attach(lift_servo_pin);
   camera_servo.attach(camera_servo_pin);
   lift_servo.write(0);
   Serial.println("Initializing lift");
   delay(1000);
   grabber_servo.write(0);
   Serial.println("Initializing Grab");
   delay(2000);
   movement(10);
  }

void turn(int angle)
{
	
	if(angle>0)
	{
		digitalWrite(forward_left_motor, LOW);
    digitalWrite(forward_right_motor, HIGH);
    digitalWrite(backward_left_motor, HIGH);
    digitalWrite(backward_right_motor, LOW);
    direction_moved = 1;
	}

	if(angle<0)
	{
	   digitalWrite(forward_left_motor, HIGH);
     digitalWrite(forward_right_motor, LOW);
     digitalWrite(backward_left_motor, LOW);
     digitalWrite(backward_right_motor, HIGH);	
     direction_moved = -1;
	}
  digitalWrite(enable_left_motor, HIGH);
  digitalWrite(enable_right_motor, HIGH);
	motor_start_time = millis();
	motor_stop_time = length_of_shaft*abs(angle)/(rpm*12*wheel_diameter)*1000;
	motor_start_flag =1;	
  

}
void movement(int distance)
{
    if(distance > 0)
    {
        digitalWrite(forward_left_motor, HIGH);
        digitalWrite(forward_right_motor, HIGH);
        digitalWrite(backward_left_motor, LOW);
        digitalWrite(backward_right_motor, LOW);
        direction_moved = 1;
    }
    else if(distance < 0)
    {
        digitalWrite(forward_left_motor, HIGH);
        digitalWrite(forward_right_motor, HIGH);
        digitalWrite(backward_left_motor, LOW);
        digitalWrite(backward_right_motor, LOW);
        direction_moved = -1;
    }
    digitalWrite(enable_left_motor, HIGH);
    digitalWrite(enable_right_motor, HIGH);
    motor_start_time = millis();
    motor_stop_time = abs(distance*30)/(rpm*3.142*wheel_diameter)*1000;
    motor_turn_flag = 1;
}

void loop()
{   if(Serial.available())
    {
       char byte_recieved = Serial.read();
       if(byte_recieved=='M')
       {
           i = Serial.readString();
           int data =i.toInt();
           Serial.println(data);
           movement(data);
           i="";
       }
       else if(byte_recieved=='T')
	     {	 
	        i = Serial.readString();
		      int data =i.toInt();
		      Serial.println(data);
		      turn(data);
          i="";
	      }
    }  
    if (motor_start_flag || motor_turn_flag)
    {
        if ((millis() - motor_start_time) > motor_stop_time)
        {
            digitalWrite(enable_left_motor, LOW);
            digitalWrite(enable_right_motor, LOW);
            motor_start_flag = 0;
            motor_turn_flag = 0;
        }
    }
  /*int left = analogRead(left_sensor_pin);
  int centre = analogRead(centre_sensor_pin);
  int right = analogRead(right_sensor_pin);
  
  if(left < 70 && right < 70 && centre > 70)
  {
    digitalWrite(enable_left_motor, HIGH);
    digitalWrite(enable_right_motor, HIGH);
    digitalWrite(forward_left_motor, HIGH);
    digitalWrite(forward_right_motor, HIGH);
    digitalWrite(backward_left_motor, LOW);
    digitalWrite(backward_right_motor, LOW);
  }
  else if(left > 70 && right > 70 && centre >70)
  {
    digitalWrite(enable_left_motor, LOW);
    digitalWrite(enable_right_motor, LOW);
    //Serial.println("1");
  }
  else{Serial.println("0");}*/
}
