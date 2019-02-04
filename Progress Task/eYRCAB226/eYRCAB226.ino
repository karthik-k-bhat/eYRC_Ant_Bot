#include <Servo.h>

#define Kp 0.5
#define Kd 1

#define left_line_sensor A0
#define center_line_sensor A2
#define right_line_sensor A4

#define right_motor_max_pwm 255
#define left_motor_max_pwm 255
#define right_motor_base_pwm 187 
#define left_motor_base_pwm 255

#define forward_left_motor 4
#define backward_left_motor 6
#define enable_left_motor 5

#define forward_right_motor 2
#define backward_right_motor 12
#define enable_right_motor 3

#define length_of_shaft 26.5
#define motor_rpm 50
#define wheel_diameter 6.8

#define grabber_servo_pin 6
#define lift_servo_pin 9
#define camera_servo_pin 10

#define buzzer 1

// #define COMMON_ANODE                 //uncomment this line if using a Common Anode LED

#define red_led 4
#define green_led 5
#define blue_led 8

Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;

int left_sensor_threshold;
int center_sensor_threshold;
int right_sensor_threshold;
int robot_movement_direction = 0;
int lastError = 0;

int red_pwm = 254;
int green_pwm = 254;
#ifdef COMMON_ANODE
   red = 255 - red;
   green = 255 - green;
#endif

long int led_on_time;

bool pick_place_flag;                       // 0 - Pick Supply, 1 - Deliver supply
bool camera_position;                       // 0 - Downwards, 1 - Upwards
bool led_on_flag = 0;

void setup()
{
   Serial.begin(9600);
   
   // Declaring the input/output pins
   pinMode(forward_right_motor, OUTPUT);
   pinMode(backward_right_motor, OUTPUT);
   pinMode(enable_right_motor, OUTPUT);
   pinMode(forward_left_motor, OUTPUT);
   pinMode(backward_left_motor, OUTPUT);
   pinMode(enable_left_motor, OUTPUT);
   pinMode(buzzer, OUTPUT);
   pinMode(red_led, OUTPUT);
   pinMode(green_led, OUTPUT);
   pinMode(blue_led, OUTPUT);

   pinMode(left_line_sensor, INPUT);
   pinMode(center_line_sensor, INPUT);
   pinMode(right_line_sensor, INPUT);
   
   // Declaring the servo pins in respective instance
   grabber_servo.attach(grabber_servo_pin);
   lift_servo.attach(lift_servo_pin);
   camera_servo.attach(camera_servo_pin);

   /*  Initializing Pick and Place Mechanism
    *  Lift servo: 0 -> Up, 28 -> Down
    *  Grab servo: 0 -> Open, 180 -> Close
    */
   
   lift_servo.write(0);
   grabber_servo.write(0);
   pick_place_flag = 0;

   camera_servo.write(120);
   camera_position = 0;
   
   line_sensor_calibrate();
}

void loop()
{
   /* Serial Communnication instructions:
    *  1. Move: 'M' followed by direction integer. 1 for Forward, -1 for Backward, 0 for Stop
    *  2. Turn: 'T' followed by direction angle. Positive for clockwise (right-side), Negative for counter-clockwise (left-side)
    *  3. Buzzer: 'B'
    *  4. RGB LED: 'R' for Red, 'B' for Blue, 'G' for Green, 'Y' for Yellow 
    *  5. Pick and Place mechanism: 'P'
    *  6. Camera servo: 'C'
    *  7. Move 10 cm front: 'O'
    */
   if (Serial.available())
   {
     char data = Serial.read();
     if (data == 'M')
     {
        String i = Serial.readString();
        robot_movement_direction = i.toInt();
        set_robot_movement();
        if (abs(get_bot_position()) >= 2)
        {
           analogWrite(enable_left_motor, left_motor_base_pwm);
           analogWrite(enable_right_motor, right_motor_base_pwm);
           delay(50);
        }
        while(movement())
        {
           if (Serial.available())
           {
              data = Serial.read();
              if (data == 'X')
              {
                 robot_movement_direction = 0;
                 set_robot_movement();
                 break;
              }
           }
        }
     }
     else if (data == 'T')
     {
        String i = Serial.readString();
        int angle = i.toInt();
        if (angle >=0)
           robot_movement_direction = 2;
        else 
           robot_movement_direction = -2;
        set_robot_movement();
        delay((length_of_shaft*abs(angle))/(motor_rpm*12*wheel_diameter)*1000);
        robot_movement_direction = 0;
        set_robot_movement();
     }
     else if (data == 'B')
     {
        digitalWrite(buzzer, HIGH);
        delay(5000);
     }
     else if (data == 'P')
     {
        pick_place();
     }
     else if (data == 'R')
     {
        digitalWrite(red_led, HIGH);
        digitalWrite(green_led, LOW);
        digitalWrite(blue_led, LOW);
        led_on_time = millis();
        led_on_flag = 1;
     }
     else if (data == 'G')
     {
        digitalWrite(red_led, LOW);        
        digitalWrite(green_led, HIGH);
        digitalWrite(blue_led, LOW);
        led_on_time = millis();
        led_on_flag = 1;
     }
     else if (data == 'B')
     {
        digitalWrite(red_led, LOW);
        digitalWrite(green_led, LOW);
        digitalWrite(blue_led, HIGH);
        led_on_time = millis();
        led_on_flag = 1;
     }
     else if (data == 'Y')
     {
        analogWrite(red_led, red_pwm);
        analogWrite(green_led, green_pwm);
        digitalWrite(blue_led, LOW);
        led_on_time = millis();
        led_on_flag = 1;
     }
     else if (data == 'C')
     {
        if (camera_position)
        {
           camera_servo.write(120);
           camera_position = 0;
        }
        else
        {
           camera_servo.write(70);
           camera_position = 1;
        }
     } 
     else if (data == 'O')
     {
        robot_movement_direction = 1;
        set_robot_movement();
        analogWrite(enable_left_motor, left_motor_base_pwm);
        analogWrite(enable_right_motor, right_motor_base_pwm);
        delay((10*30)/(50*3.142*wheel_diameter)*1000);
        digitalWrite(enable_left_motor, LOW);
        digitalWrite(enable_right_motor, LOW);
        
     }
   }

   if (led_on_flag == 1 && (millis() - led_on_time > 1000))
   {
      digitalWrite(red_led, LOW);
      digitalWrite(green_led, LOW);
      digitalWrite(blue_led, LOW);
      led_on_flag = 0;
   }
}

int movement()
{
  int error = get_bot_position();
  int right_motor_pwm = 0;
  int left_motor_pwm = 0;
  if (abs(error) < 2 || error == -3)
  {
     int motorSpeed = Kp * error + Kd * (error - lastError);
     lastError = error;
     if (robot_movement_direction == 1)                           // 1 - Forward
     {
        right_motor_pwm = right_motor_base_pwm + motorSpeed;
        left_motor_pwm = left_motor_base_pwm - motorSpeed;
     }
     else if (robot_movement_direction == -1)                     // -1 - Backward
     {
        right_motor_pwm = right_motor_base_pwm - motorSpeed;
        left_motor_pwm = left_motor_base_pwm + motorSpeed;
     }
     
     if (right_motor_pwm > right_motor_max_pwm )
        right_motor_pwm = right_motor_max_pwm;                    // prevent the motor from going beyond max speed
     if (left_motor_pwm > left_motor_max_pwm )
        left_motor_pwm = left_motor_max_pwm;
     if (right_motor_pwm < 0)
        right_motor_pwm = 0;                                      // keep the motor speed positive
     if (left_motor_pwm < 0)
        left_motor_pwm = 0;

     analogWrite(enable_left_motor, left_motor_pwm);
     analogWrite(enable_right_motor, right_motor_pwm);
     return 1;
  }
  else
  {
    robot_movement_direction = 0;
    set_robot_movement();
    if (error == -2)
       Serial.println("Left-branched Node");
    else if (error == 2)
       Serial.println("Right-branched Node");
    else if (error == -3)
       Serial.println("White Space");
    else if (error == 3)
       Serial.println("Node");   
    return 0;
  }
}

void line_sensor_calibrate()
{
   Serial.println("Calibrating Line Sensor");
   int left_white_value = 0, left_black_value = 0;
   int center_white_value = 0, center_black_value = 0;
   int right_white_value = 0, right_black_value = 0; 

   left_white_value = analogRead(left_line_sensor);
   center_white_value = analogRead(center_line_sensor);
   right_white_value = analogRead(right_line_sensor);
   Serial.print("Left sensor white value ");
   Serial.print(left_white_value);
   Serial.print(", Center sensor white value ");
   Serial.print(center_white_value);
   Serial.print(", Right sensor white value ");
   Serial.println( right_white_value);
   robot_movement_direction = 1;
   set_robot_movement();
   
   analogWrite(enable_right_motor, right_motor_base_pwm);
   analogWrite(enable_left_motor, left_motor_base_pwm);
  
   delay(80);                                         // 80 ms (for approx 1.5 cms)
  
   robot_movement_direction = 0;
   set_robot_movement();
   delay(2000);                                      // Uncomment Later
   
   left_black_value = analogRead(left_line_sensor);
   center_black_value = analogRead(center_line_sensor);
   right_black_value = analogRead(right_line_sensor);
   Serial.print("Left sensor black value ");
   Serial.print(left_black_value);
   Serial.print(", Center sensor black value ");
   Serial.print(center_black_value);
   Serial.print(", Right sensor black value ");
   Serial.println( right_black_value);  

   left_sensor_threshold = ((left_black_value + left_white_value) / 2);// - (left_white_value / 3);
   center_sensor_threshold = ((center_black_value + center_white_value) / 2);// - (center_white_value / 3);
   right_sensor_threshold = ((right_black_value + right_white_value) / 2);// - (right_white_value / 3);
   Serial.print("Left sensor threshold ");
   Serial.print(left_sensor_threshold);
   Serial.print(", Center sensor threshold ");
   Serial.print(center_sensor_threshold);
   Serial.print(", Right sensor threshold ");
   Serial.println( right_sensor_threshold);
}

void set_robot_movement()
{
   if (robot_movement_direction == 1)               // 1 -> Forward
   {
      digitalWrite(forward_right_motor, HIGH);
      digitalWrite(backward_right_motor, LOW);
      digitalWrite(forward_left_motor, HIGH);
      digitalWrite(backward_left_motor, LOW);
      Serial.println("Direction Set: Forward");
   }
   else if (robot_movement_direction == -1)         // -1 -> Backward
   {
      digitalWrite(forward_right_motor, LOW);
      digitalWrite(backward_right_motor, HIGH);
      digitalWrite(forward_left_motor, LOW);
      digitalWrite(backward_left_motor, HIGH);
      Serial.println("Direction Set: Backward");
   }
   else if (robot_movement_direction == 2)          // 2 -> Clockwise (Right)
   {
      digitalWrite(forward_right_motor, LOW);
      digitalWrite(backward_right_motor, HIGH);
      digitalWrite(forward_left_motor, HIGH);
      digitalWrite(backward_left_motor, LOW);

      digitalWrite(enable_right_motor, HIGH);
      digitalWrite(enable_left_motor, HIGH);
      Serial.println("Direction Set: Right");
   }
   else if (robot_movement_direction == -2)         // -2 -> Counter-clockwise (Left)
   {
      digitalWrite(forward_right_motor, HIGH);
      digitalWrite(backward_right_motor, LOW);
      digitalWrite(forward_left_motor, LOW);
      digitalWrite(backward_left_motor, HIGH);

      digitalWrite(enable_right_motor, HIGH);
      digitalWrite(enable_left_motor, HIGH);
      Serial.println("Direction Set: Left");
   }
   else if (robot_movement_direction == 0)          // 0 -> Stop
   {
      digitalWrite(enable_right_motor, LOW);
      digitalWrite(enable_left_motor, LOW);
   }
}


int get_bot_position()
{
  int left_sensor_value = analogRead(left_line_sensor);
  int center_sensor_value = analogRead(center_line_sensor);
  int right_sensor_value = analogRead(right_line_sensor);

  /*  Black Line: "Greater than/equal to" sensor_threshold
   *  White Line: "Lesser than/equal to" sensor_threshold
   */
  Serial.print(left_sensor_value);
  Serial.print(" ");
  Serial.print(center_sensor_value);
  Serial.print(" ");
  Serial.println(right_sensor_value);
  if (left_sensor_value <= left_sensor_threshold &&
      center_sensor_value <= center_sensor_threshold &&
      right_sensor_value >= right_sensor_threshold)
  {
    // RIGHT CONDITION;
    return 1;
  }
  
  else if (left_sensor_value <= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // STRAIGHT LINE CONDITION;
    return 0;
  }
  
  else if (left_sensor_value >= left_sensor_threshold &&
           center_sensor_value <= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // LEFT CONDITION;
    return -1;
  }
  
  else if (left_sensor_value <= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value >= right_sensor_threshold)
  {
    // RIGHT BRANCHED-NODE CONDITION;
    return 2;
  }
  
  else if (left_sensor_value >= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // LEFT BRANCHED-NODE CONDITION;
    return -2;
  }
  
  else if (left_sensor_value >= left_sensor_threshold &&
            center_sensor_value >= center_sensor_threshold &&
            right_sensor_value >= right_sensor_threshold)
  {
    // T-NODE CONDITION;
    return 3;
  }

  else if (left_sensor_value <= left_sensor_threshold &&
            center_sensor_value <= center_sensor_threshold &&
            right_sensor_value <= right_sensor_threshold)
  {
    // WHITE SPACE CONDITION;
    return -3;
  }
}

void pick_place()
{
   /*  Lift servo: 0 -> Up, 28 -> Down
    *  Grab servo: 0 -> Open, 180 -> Close
    */
   if (pick_place_flag)             // Deliver the supply
   {
      lift_servo.write(28);
      delay(500);
      grabber_servo.write(0);
      delay(1000);
      lift_servo.write(0);
      delay(500);
      pick_place_flag = 0;
   }
   else                             // Pick the suuply
   {
      lift_servo.write(28);
      delay(500);
      grabber_servo.write(180);
      delay(1000);
      lift_servo.write(0);
      delay(500);
      pick_place_flag = 1;
   }

}
