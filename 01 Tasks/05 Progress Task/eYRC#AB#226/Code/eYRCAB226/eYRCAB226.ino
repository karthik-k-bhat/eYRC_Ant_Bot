/*
 * Team ID          : 226
 * Authors          : Karthik K Bhat, Shreyas R
 * File Name        : eYRCAB226.ino
 * Theme            : Antbot
 * Functions        : setup, loop, movement, line_sensor_calibrate, set_robot_movement,
 *                    get_bot_position, pick_place
 * Global variables : left_sensor_threshold, center_sensor_threshold, right_sensor_threshold,
 *                    robot_movement_direction, lastError, pick_place_flag, camera_position
 */

#include <Servo.h>

// PD Values for line correction (PID where Ki = 0)
#define Kp 0.5
#define Kd 1

// Pin numbers for line sensors
#define left_line_sensor A0
#define center_line_sensor A2
#define right_line_sensor A4

// Motor parameter to control with PID algorithm
#define right_motor_max_pwm 255
#define left_motor_max_pwm 255
#define right_motor_base_pwm 187                  // Base pwm - Such that the robot goes in a straight line 
#define left_motor_base_pwm 255

// Pin numbers for Motor control with L298D
#define forward_left_motor 4
#define backward_left_motor 6
#define enable_left_motor 5

#define forward_right_motor 2
#define backward_right_motor 12
#define enable_right_motor 3

// Parameters of the robot for movements
#define length_of_shaft 26.5
#define motor_rpm 50
#define wheel_diameter 6.8

// Pin numbers for Servo pins
#define grabber_servo_pin 6
#define lift_servo_pin 9
#define camera_servo_pin 10

// Instances for servo motors
Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;

// Global Variables
int left_sensor_threshold;                        // Threshold values for line sensor
int center_sensor_threshold;
int right_sensor_threshold;

/* To indicate the direction of movement for robot
 *  -2  Left direction
 *  -1  Backward
 *   0  Stop
 *  +1  Forward
 *  +2  Right direction
 */
int robot_movement_direction = 0;

/* For robot orientation with respect to line
 *  -3  White space
 *  -2  Left Branched Node
 *  -1  Bot left of line
 *   0  
 *  +1  Bot right of line
 *  +2  Right Branched Node
 *  +3  T-Node
 */
int lastError = 0;

bool pick_place_flag;                       // 0 - Pick Supply, 1 - Deliver supply
bool camera_position;                       // 0 - Downwards, 1 - Upwards


// Default arduino setup function - to run the code initially one time
void setup()
{
   // For serial communication between Raspberry Pi and Arduino
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
    *  Camera servo: 120 -> Up 70 -> Down facing 
    */
   
   lift_servo.write(0);
   grabber_servo.write(0);
   pick_place_flag = 0;

   camera_servo.write(120);
   camera_position = 0;

   // To calibrate line sensor
   line_sensor_calibrate();
}

// Default arduino loop function - to keep executing the instructions indefintely
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
     // Read the data from Serial buffer.
     char data = Serial.read();
     if (data == 'M') // For linear movement of the bot
     {
        // Message syntax - "M X" X being an integer from -3 to 3 the robot_movement_direction
        String i = Serial.readString();
        robot_movement_direction = i.toInt();
        set_robot_movement();

        // If robot already on a node, move front
        if (abs(get_bot_position()) >= 2)
        {
           analogWrite(enable_left_motor, left_motor_base_pwm);
           analogWrite(enable_right_motor, right_motor_base_pwm);
           delay(50);
        }

        // Whenever the robot is on a line, move until the robot is on node.
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
     else if (data == 'T') // For Turning the robot
     {
        // Message syntax - "T X" X being an integer representing the angle to turn
        String i = Serial.readString();
        int angle = i.toInt();
        
        // Set the direction
        if (angle >=0)
           robot_movement_direction = 2;
        else 
           robot_movement_direction = -2;
        set_robot_movement();
        
        // Keep the motor running until it rotates the given angle
        delay((length_of_shaft*abs(angle))/(motor_rpm*12*wheel_diameter)*1000);

        // Stop the motors
        robot_movement_direction = 0;
        set_robot_movement();
     }
     
     // For Pick and Place mechanism
     else if (data == 'P')
     {
        pick_place();
     }

     // For Camera servo movements
     else if (data == 'C')
     {
        if (camera_position)
        {
           // 120 degree - camera facing up
           camera_servo.write(120);
           camera_position = 0;
        }
        else
        {
           // 70 degree - camera facing down
           camera_servo.write(70);
           camera_position = 1;
        }
     } 

     // For a small distance movement of the bot (Front direction)
     else if (data == 'O')
     {
        robot_movement_direction = 1;
        set_robot_movement();
        // Run the motor. (PWM is used to keep the bot move in straight line)
        analogWrite(enable_left_motor, left_motor_base_pwm);
        analogWrite(enable_right_motor, right_motor_base_pwm);

        // For 10 cm
        delay((10*30)/(50*3.142*wheel_diameter)*1000);
        // Stop the motors
        digitalWrite(enable_left_motor, LOW);
        digitalWrite(enable_right_motor, LOW);
        
     }
   }
}

/* 
 *  Function Name : Movement
 *  Input         : None
 *  Output        : bool value - 0 robot being a node, 1 robot being on the line
 *  Logic         : 1. To check the robot position using line sensor
 *                  2. calculate the error for PID Algorithm and set the motor speeds
 *                  3. Run the motors at calculated speeds
 *                  4. If a node is identified, return 0, else return 1
 *  Example Call  : movement()
 */
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
        // Calculate the motor driving speed
        right_motor_pwm = right_motor_base_pwm + motorSpeed;
        left_motor_pwm = left_motor_base_pwm - motorSpeed;
     }
     else if (robot_movement_direction == -1)                     // -1 - Backward
     {
        // Calculate the motor driving speed
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
    // Stop the robot
    robot_movement_direction = 0;
    set_robot_movement();

    // Send the message to display on the serial monitor
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

/* 
 *  Function Name : line_sensor_calibrate
 *  Input         : None
 *  Output        : None
 *  Logic         : 1. Keep robot on the white area before the start node.   
 *                  2. Read the line sensor value for white area
 *                  3. Move the robot to the node (for 1.5 cms)
 *                  4. Read the line sensor value for black.
 *                  5. Find the threshold for each sensor by taking the average of white and black value
 *  Example Call  : line_sensor_calibrate()
 */
void line_sensor_calibrate()
{
   Serial.println("Calibrating Line Sensor");
   int left_white_value = 0, left_black_value = 0;
   int center_white_value = 0, center_black_value = 0;
   int right_white_value = 0, right_black_value = 0; 


   // Read the analog values
   left_white_value = analogRead(left_line_sensor);
   center_white_value = analogRead(center_line_sensor);
   right_white_value = analogRead(right_line_sensor);

   // Print the value on the Serial monitor
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
   // Wait 2 seconds before taking value from black area.
   delay(2000);
   
   left_black_value = analogRead(left_line_sensor);
   center_black_value = analogRead(center_line_sensor);
   right_black_value = analogRead(right_line_sensor);
   Serial.print("Left sensor black value ");
   Serial.print(left_black_value);
   Serial.print(", Center sensor black value ");
   Serial.print(center_black_value);
   Serial.print(", Right sensor black value ");
   Serial.println( right_black_value);  

   left_sensor_threshold = ((left_black_value + left_white_value) / 2);
   center_sensor_threshold = ((center_black_value + center_white_value) / 2);
   right_sensor_threshold = ((right_black_value + right_white_value) / 2);
   Serial.print("Left sensor threshold ");
   Serial.print(left_sensor_threshold);
   Serial.print(", Center sensor threshold ");
   Serial.print(center_sensor_threshold);
   Serial.print(", Right sensor threshold ");
   Serial.println( right_sensor_threshold);
}

/* 
 *  Function Name : set_robot_movement
 *  Input         : None
 *  Output        : None
 *  Logic         : 1. Set the directions for movement according the robot_movement_direction
 *                            -2  Left direction
 *                            -1  Backward
 *                             0  Stop
 *                            +1  Forward
 *                            +2  Right direction
 *                  2. For forward directon, motor forward pin to be HIGH and backward pin to be LOW
 *                  3. For backward directon, motor forward pin to be LOW and backward pin to be HIGH
 *                  4. For right directon, Left motor to go forward and right motor to go backward        
 *                  5. For left directon, Left motor to go backward and right motor to go forward         
 *                  6. To start the motor, make the enable pins high, or use analog write to run at different speeds using pwm.
 *                  7. To stop the robot, make the enable pins low.
 *  Example Call  : set_robot_movement()
 */
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

/* 
 *  Function Name : get_bot_position
 *  Input         : None
 *  Output        : Integer to represent the robot position
 *                  For robot orientation with respect to line
 *                        -3  White space
 *                        -2  Left Branched Node
 *                        -1  Bot left of line
 *                         0  
 *                        +1  Bot right of line
 *                        +2  Right Branched Node
 *                        +3  T-Node
 *  
 *  Logic         : 1. Read the sensor values  
 *                  2. Compare the values with the threshold values to get the position accordingly
 *  Example Call  : get_bot_position()
 */

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

  /*  Left Sensor on White space
   *  Center Sensor on White space
   *  Right Sensor on Black
   */
  if (left_sensor_value <= left_sensor_threshold &&
      center_sensor_value <= center_sensor_threshold &&
      right_sensor_value >= right_sensor_threshold)
  {
    // RIGHT CONDITION;
    return 1;
  }

  /*  Left Sensor on White space
   *  Center Sensor on Black
   *  Right Sensor on White space
   */
  else if (left_sensor_value <= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // STRAIGHT LINE CONDITION;
    return 0;
  }

  /*  Left Sensor on Black
   *  Center Sensor on White space
   *  Right Sensor on White space
   */
  else if (left_sensor_value >= left_sensor_threshold &&
           center_sensor_value <= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // LEFT CONDITION;
    return -1;
  }

  /*  Left Sensor on White space
   *  Center Sensor on Black
   *  Right Sensor on Black
   */
  else if (left_sensor_value <= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value >= right_sensor_threshold)
  {
    // RIGHT BRANCHED-NODE CONDITION;
    return 2;
  }

  /*  Left Sensor on Black
   *  Center Sensor on Black
   *  Right Sensor on White space
   */
  else if (left_sensor_value >= left_sensor_threshold &&
           center_sensor_value >= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // LEFT BRANCHED-NODE CONDITION;
    return -2;
  }

  /*  Left Sensor on Black
   *  Center Sensor on Black
   *  Right Sensor on Black
   */
  else if (left_sensor_value >= left_sensor_threshold &&
            center_sensor_value >= center_sensor_threshold &&
            right_sensor_value >= right_sensor_threshold)
  {
    // T-NODE CONDITION;
    return 3;
  }

  /*  Left Sensor on White
   *  Center Sensor on White
   *  Right Sensor on White
   */
  else if (left_sensor_value <= left_sensor_threshold &&
            center_sensor_value <= center_sensor_threshold &&
            right_sensor_value <= right_sensor_threshold)
  {
    // WHITE SPACE CONDITION;
    return -3;
  }
}

/* 
 *  Function Name : pick_place
 *  Input         : None
 *  Output        : None
 *  Logic         : Set the angle to the required servo as required 
 *  Example Call  : movement()
 */

void pick_place()
{
   /*  Lift servo : 0 -> Up, 28 -> Down
    *  Grab servo : 0 -> Open, 180 -> Close
    */
   if (pick_place_flag)             // Deliver the supply
   {
      // Go down
      lift_servo.write(28);
      delay(500);
      // Open the arm
      grabber_servo.write(0);
      delay(1000);
      // Go up
      lift_servo.write(0);
      delay(500);
      // No block lifted
      pick_place_flag = 0;
   }
   else                             // Pick the suuply
   {
      // Go down
      lift_servo.write(28);
      delay(500);
      // Close the arm
      grabber_servo.write(180);
      delay(1000);
      // GO up
      lift_servo.write(0);
      delay(500);
      // Block lifted
      pick_place_flag = 1;
   }
}
