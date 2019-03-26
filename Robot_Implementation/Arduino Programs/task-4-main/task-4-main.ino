/*
 * Team ID          : 226
 * Authors          : Karthik K Bhat, Vishwas N S, Shreyas R
 * File Name        : eYRCAB226.ino
 * Theme            : Antbot
 * Functions        : movement, line_sensor_calibrate, set_robot_movement, get_bot_position, pick_place, cancel_inertia
 * Global variables : left_sensor_threshold, center_sensor_threshold, right_sensor_threshold,
 *                    robot_movement_direction, bot_position, node_count, left_motor_pwm, right_motor_pwm,
 *                    node_flag, camera_position, pick_place_flag, job_done_flag, white_space_stop, node_stop
 */

// Include the required Library Files
#include <Servo.h>

// Pin numbers for line sensors
#define left_line_sensor A0
#define center_line_sensor A2
#define right_line_sensor A4
#define jump_threshold 100                         // Change in the value of Line sensor reading to determine the threshold

// Motor parameter to control the speeds
#define right_motor_base_pwm 255                  // Base pwm - Such that the robot goes in a straight line   
#define left_motor_base_pwm 255

#define left_motor_slow_speed_pwm 255             // PWM such that bot moves in a slower speed
#define right_motor_slow_speed_pwm 255

#define motor_speed_variation 150                  // Change in PWM value to account for change in direction for line correction

// Pin numbers for Motor control with L298D
#define forward_left_motor 7     //7
#define backward_left_motor 8   //4
#define enable_left_motor 6      //5

#define forward_right_motor 2    //12
#define backward_right_motor 4   //2
#define enable_right_motor 3     //3

// Parameters of the robot for movements
#define length_of_shaft 27
#define motor_rpm 100
#define wheel_diameter 6.7
#define sensor_wheel_distance 9

// Pin numbers for Servo pins and buzzer
#define grabber_servo_pin 10
#define lift_servo_pin 9
#define camera_servo_pin 11

#define buzzer 12

// Instances for servo motors
Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;


// Global Variables Declaration
int left_sensor_threshold = 450;                        // Threshold values for line sensor
int center_sensor_threshold = 450;
int right_sensor_threshold = 450;

/* To indicate the direction of movement for robot
 *  -2  Left direction
 *  -1  Backward
 *   0  Stop
 *  +1  Forward
 *  +2  Right direction
 */
int robot_movement_direction = 0;

/* For robot orientation with respect to line
 *  -1  Bot left of line
 *   0  
 *  +1  Bot right of line
 */
int bot_position;                            // To identify the last known position of the bot
int node_count = 0;                          // To count the number of nodes in the path to stop
int left_motor_pwm;                          // Variable for differential pwm for line correction
int right_motor_pwm;

bool node_flag = 0;                          // 0 - No node detected, 1 - Node detected
//bool camera_position;                        // 0 - Downwards, 1 - Upwards
bool pick_place_flag;                        // 0 - Pick Supply, 1 - Deliver supply
bool job_done_flag = 0;                      // Flag to denote if a job was completed or not
bool node_stop = 0;

int lift_up = 0;
int lift_down = 25;

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
   pinMode(left_line_sensor, INPUT);
   pinMode(center_line_sensor, INPUT);
   pinMode(right_line_sensor, INPUT);
   
   // Declaring the servo pins in respective instance
   grabber_servo.attach(grabber_servo_pin);
   lift_servo.attach(lift_servo_pin);
   camera_servo.attach(camera_servo_pin);

   /*  Initializing Pick and Place Mechanism
    *  Lift servo: 0 -> Up, 23 -> Down
    *  Grab servo: 0 -> Open, 180 -> Close
    */
   lift_servo.write(lift_up);
   grabber_servo.write(0);
   pick_place_flag = 0;

   //Camera servo: 40 
   camera_servo.write(40);
   //camera_position = 1;
}

// Default arduino loop function - to keep executing the instructions indefintely
void loop()
{
   /* Serial Communnication instructions:
    *  1. Move: 'M' followed by direction integer representing number of nodes to pass. Positive being front direction and negative being back.
    *  2. Turn: 'T' followed by direction angle. Positive for clockwise (right-side), Negative for counter-clockwise (left-side)
    *  3. Rotate: 'L' or 'R' - Turn with respect to the lines
    *  4. Buzzer: 'B'
    *  5. Pick and Place mechanism: 'P'
    *  6. Camera servo: 'C'
    *  7. Move a certain distance: 'O' followed by the distance. Positive is front, Negative is back 
    *  8. Stop when just when Node is reached: 'N'
    *  9. Line sensor Calibration: 'I'
    */
   if (Serial.available())
   {
     // Read the data from Serial buffer.
     char data = Serial.read();
     if (data == 'M') // For linear movement of the bot
     {
        // Message syntax - "M X" X being an integer representing number of nodes to pass. Positive being front direction and negative being back.
        String i = Serial.readString();
        int number_of_nodes = i.toInt();

        // Set robot direction to move.
        robot_movement_direction = number_of_nodes/abs(number_of_nodes);
        set_robot_movement();

        // Clear the flags
        node_flag = 0;
        node_count = 0;
        // Whenever the robot is on a line, move until the robot is on node.
        while(movement(number_of_nodes))
        {
           // If any data is sent during movement, read 
           if (Serial.available())
           {
              data = Serial.read();
              // If it is 'X', stop the motors
              if (data == 'X')
              {
                 robot_movement_direction = 0;
                 set_robot_movement();
                 bot_position = 0;
                 break;
              }
           }
        }
        // Set job_done_flag
        job_done_flag = 1;
        node_flag = 0;
     }

     else if (data == 'T')
     {
        // Message syntax - "T X" X being an integer representing the angle to turn
        String i = Serial.readString();
        int angle = i.toInt();

        float time_duration = (length_of_shaft*abs(angle))/(motor_rpm*6*wheel_diameter)*1000;
        // Set the direction
        if (angle >=0)
           robot_movement_direction = 2;
        else 
           robot_movement_direction = -2;
        set_robot_movement();

        // Keep the motor running until the robot rotates the given angle
        // Formuala to caculate time delay in seconds = (angle_to_rotate * length_between_wheels)/(rpm_of_motor * 6 * diameter_of_wheel)
        delay(time_duration);

        // Stop the motors and overcome the inertia
        cancel_inertia();
        job_done_flag = 1;
     }

     else if(data == 'L' || data == 'R')
     {
        // If L, then movement direction is left (-2)
        if (data == 'L')
           robot_movement_direction = -2;
        // If R, then movement direction is right (2)
        else if (data == 'R')
           robot_movement_direction = 2;
        set_robot_movement();

        // Move for a small period to come out of the line
        delay(300);

        // Loop until bot is on the line
        while(1)
        {
           // If turning right, slow down when right sensor is on line
           // If turning left, slow down when left sensor is on line
           if (get_bot_position()== -1 || get_bot_position() == 1)
           {
              analogWrite(enable_right_motor, 160);
              analogWrite(enable_left_motor, 160);
           }
           if (get_bot_position() == 0)
           {
              cancel_inertia();
              robot_movement_direction=0;
              set_robot_movement();
              break;
           }
        }
        job_done_flag = 1;
     }

     // To beep the buzzer
     else if (data == 'B')
     {
        // Turn on the buzzer
        digitalWrite(buzzer, HIGH);
        // Wait for 5 seconds as per the rulebook
        delay(5000);
        digitalWrite(buzzer, LOW);
        job_done_flag = 1;
     }

     // For Pick and Place mechanism
     else if (data == 'P')
     {
        pick_place();
        job_done_flag = 1;
     }

     // For Camera servo movements
     /*else if (data == 'C')
     {
        if (camera_position)
        {
           camera_servo.write(40);
           camera_position = 0;
        }
        else
        {
           camera_servo.write(70);
           camera_position = 1;
        }
        job_done_flag = 1;
     }*/
     
     // For a small distance movement of the bot (Front direction)
     else if (data == 'O')
     {
        // Message syntax - "O X" X being an integer value representing the distance to move in centimeter
        String i = Serial.readString();
        int distance = i.toInt();

        if (distance > 0)
           robot_movement_direction = 1;
        else
           robot_movement_direction = -1;
        set_robot_movement();
        
        // Run the motor. (PWM is used to keep the bot move in straight line
        if (robot_movement_direction == 1)
        {
           analogWrite(enable_left_motor, left_motor_base_pwm);
           analogWrite(enable_right_motor, right_motor_base_pwm);
        }
        else if (robot_movement_direction == -1)
        {
           analogWrite(enable_left_motor, left_motor_slow_speed_pwm);
           analogWrite(enable_right_motor, right_motor_slow_speed_pwm);
        }

        // Keep the motor running until the robot travels the given distance
        // Formuala to caculate time delay in seconds = (distance_to_travel * 60)/(rpm_of_motor * pi * diameter_of_wheel)
        delay((abs(distance)*60)/(motor_rpm*3.142*wheel_diameter)*1000);

        // Stop the motors by cancelling the inertia
        cancel_inertia();
        job_done_flag = 1;
     }

     else if (data == 'N')
     {
        // Stop the bot just when node is reached. Set the corresponding flag to indicate the same
        node_stop = 1;
        job_done_flag = 1;
     }

     else if (data == 'I')
     {
        // Calibrate the line sensors
        line_sensor_calibrate();
        job_done_flag = 1;
     }
  }
   
  // If job is done, send "Job done" signal to Pi
  if(job_done_flag)
  {
     Serial.println("Job done");
     // Clear the flag and wait for next command
     job_done_flag = 0;  
  }
   
}

/* 
 *  Function Name : Movement
 *  Input         : int number_of_nodes
 *  Output        : bool value - 0 robot stopped, 1 robot moving
 *  Logic         : 1. To check the robot position using line sensor
 *                  2. If the bot is sensed to be on a line or on white space, keep moving front as per the calculated speed
 *                  3. If a node is sensed, and node_flag was 0 then, increment the node count.
 *                  4. If the node_stop is 1 and node_count was same as number_of_nodes, then stop the bot after going front, else just stop
 *                  5. Return 1 if bot is moving, else return 0
 *  Example Call  : movement()
 */
bool movement(int number_of_nodes)
{
   // To get the position of the bot
   int error = get_bot_position();

   // If on the line (-1/1) or white space (-3)
   if(abs(error) == 1 or error == 0 or error == -3)
   {
      node_flag = 0;
   }
   // If a node is present (-2, 2, 3)
   else if(abs(error) == 2 || error == 3)
   {
      // If there bot was on line and node was sensed, increment node_count
      if(node_flag == 0)
      {
         node_flag = 1;
         node_count ++;
      }
      // If node_count = number_of_nodes, stop the bot
      if(node_count == number_of_nodes)
      {
         // if node_stop was 0, then move front a bit (sensor_wheel_distance) 
         if(node_stop == 0)
         {
            analogWrite(enable_left_motor, left_motor_base_pwm);
            analogWrite(enable_right_motor, right_motor_base_pwm);
            delay((abs(sensor_wheel_distance)*60)/(motor_rpm*3.142*wheel_diameter)*1000);
         }
         robot_movement_direction = 0;
         set_robot_movement();
         node_stop = 0;
         return 0;
      }
   }
   // Run motor at different speeds to align to the line
   analogWrite(enable_left_motor, left_motor_pwm);
   analogWrite(enable_right_motor, right_motor_pwm);
   return 1;
}

/* 
 *  Function Name : line_sensor_calibrate
 *  Input         : None
 *  Output        : None
 *  Logic         : 1. Keep robot on the white area before the start node.   
 *                  2. Read the line sensor value for white area for 50 tries
 *                  3. Take the greatest value to be the value of the sensor
 *                  4. Move the bot until a large change is observed
 *                  5. Read the line sensor value for black area for 50 tries
 *                  6. Take the least value to be the sensor value
 *                  7. Find the threshold for each sensor by taking the average of white and black value
 *  Example Call  : line_sensor_calibrate()
 */
void line_sensor_calibrate()
{
   // Initialize the local variables
   int left_white_value = 0, left_black_value = 0;
   int center_white_value = 0, center_black_value = 0;
   int right_white_value = 0, right_black_value = 0; 
   
   int left_jump_value = 0, right_jump_value = 0, center_jump_value = 0;

   
   int tries = 50, left = 0,right = 0, center = 0;
   // Read the analog values many times
   for(int i=0;i<tries;i++)
   {
      left = analogRead(left_line_sensor);
      center = analogRead(center_line_sensor);
      right = analogRead(right_line_sensor);
      if(left>left_white_value)
         left_white_value = left;
      if(right>right_white_value)
         right_white_value = right;
      if(center>center_white_value)
         center_white_value = center;
   }
   // Print the value on the Serial monitor
   Serial.print("Left sensor white value ");
   Serial.print(left_white_value);
   Serial.print(", Center sensor white value ");
   Serial.print(center_white_value);
   Serial.print(", Right sensor white value ");
   Serial.println( right_white_value); 
   delay(100);

   // Move the robot front
   robot_movement_direction = 1;
   set_robot_movement();
   
   analogWrite(enable_right_motor, right_motor_slow_speed_pwm);
   analogWrite(enable_left_motor, left_motor_slow_speed_pwm);

   // Move the bot front until there is a large jump in the line sensor values
   while (left_jump_value < jump_threshold || center_jump_value < jump_threshold || right_jump_value < jump_threshold)
   {
      // Read the analog values
      left_black_value = analogRead(left_line_sensor);
      center_black_value = analogRead(center_line_sensor);
      right_black_value = analogRead(right_line_sensor);

      // Calculate the jump in the value
      left_jump_value = left_black_value - left_white_value;
      center_jump_value = center_black_value - center_white_value;
      right_jump_value = right_black_value - right_white_value;
      //  time_moved = millis() - time_started;
   }

   // Stop the bot
   robot_movement_direction = 0;
   set_robot_movement();

   // Read analog values for many times
   for(int i=0;i<tries;i++)
   {
      left = analogRead(left_line_sensor);
      center = analogRead(center_line_sensor);
      right = analogRead(right_line_sensor);
      if(left<left_black_value)
         left_black_value = left;
      if(right<right_black_value)
         right_black_value = right;
      if(center<center_black_value)
         center_black_value = center;
   }
   
   Serial.print("Left sensor black value ");
   Serial.print(left_black_value);
   Serial.print(", Center sensor black value ");
   Serial.print(center_black_value);
   Serial.print(", Right sensor black value ");
   Serial.println(right_black_value);  

   left_sensor_threshold = (left_black_value - (left_black_value - left_white_value)/3.5);
   center_sensor_threshold = (center_black_value - (center_black_value - center_white_value)/3.5);
   right_sensor_threshold = (right_black_value - (right_black_value - right_white_value)/3.5);
   
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
   }
   else if (robot_movement_direction == -1)         // -1 -> Backward
   {
      digitalWrite(forward_right_motor, LOW);
      digitalWrite(backward_right_motor, HIGH);
      digitalWrite(forward_left_motor, LOW);
      digitalWrite(backward_left_motor, HIGH);
   }
   else if (robot_movement_direction == 2)          // 2 -> Clockwise (Right)
   {
      digitalWrite(forward_right_motor, LOW);
      digitalWrite(backward_right_motor, HIGH);
      digitalWrite(forward_left_motor, HIGH);
      digitalWrite(backward_left_motor, LOW);

      digitalWrite(enable_right_motor, HIGH);
      digitalWrite(enable_left_motor, HIGH);
   }
   else if (robot_movement_direction == -2)         // -2 -> Counter-clockwise (Left)
   {
      digitalWrite(forward_right_motor, HIGH);
      digitalWrite(backward_right_motor, LOW);
      digitalWrite(forward_left_motor, LOW);
      digitalWrite(backward_left_motor, HIGH);

      digitalWrite(enable_right_motor, HIGH);
      digitalWrite(enable_left_motor, HIGH);
   }
   else if (robot_movement_direction == 0)          // 0 -> Stop
   {
      digitalWrite(enable_right_motor, LOW);
      digitalWrite(enable_left_motor, LOW);
   }
}

/* 
 *  Function Name : get_bot_position
 *  Input         : line sensor values
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
 *                  3. If the bot is found to be on left/right of the line change the speeds of the motor.
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

  
  /*  Left Sensor on White space
   *  Center Sensor on White space
   *  Right Sensor on Black
   */
  if (left_sensor_value <= left_sensor_threshold &&
      center_sensor_value <= center_sensor_threshold &&
      right_sensor_value >= right_sensor_threshold)
  {
    // RIGHT CONDITION;
    bot_position = 1;
    if (robot_movement_direction == 1)
         right_motor_pwm = right_motor_base_pwm - motor_speed_variation;
      else if (robot_movement_direction == -1)
         right_motor_pwm = right_motor_base_pwm + (motor_speed_variation/2);
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
    bot_position = 0;
    left_motor_pwm = left_motor_base_pwm;
    right_motor_pwm = right_motor_base_pwm;
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
    bot_position = -1;
    if (robot_movement_direction == 1)
      left_motor_pwm = left_motor_base_pwm - motor_speed_variation;
   else if (robot_movement_direction == -1)
      left_motor_pwm = left_motor_base_pwm + (motor_speed_variation/2);
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

   /*  Lift servo : 0 -> Up, 23 -> Down
    *  Grab servo : 0 -> Open, 180 -> Close
    */
   if (pick_place_flag)             // Deliver the supply
   {
      // Go down
      lift_servo.write(lift_down);
      delay(600);
      // Open the arm
      grabber_servo.write(0);
      delay(1000);
      // Go up
      lift_servo.write(lift_up);
      delay(600);
      //delay(500);
      // No block lifted
      pick_place_flag = 0;
   }
   else                             // Pick the supply
   {
      // Go down
      lift_servo.write(lift_down);
      delay(600);
      //delay(500);
      // Close the arm
      grabber_servo.write(180);
      delay(1000);
      // GO up
      lift_servo.write(lift_up);
      delay(600);
      // Block lifted
      pick_place_flag = 1;
   }
}


/* 
 *  Function Name : cancel_inertia
 *  Input         : None
 *  Output        : None
 *  Logic         : When the robot is moving one direction, make the robot move in the opposite direction for very small time duration
 *                  so that the inertia in the motor is nullified.
 *  Example Call  : cancel_inertia()
 */
void cancel_inertia()
{
   // Set the direction of the robot in opposite direction
   robot_movement_direction *= -1;
   set_robot_movement();
   
   // Run the motors for a short time to cancel the inertia of rotation
   delay(10);
   digitalWrite(enable_right_motor, HIGH);
   digitalWrite(enable_left_motor, HIGH);
   // Stop the motors.
   robot_movement_direction = 0;
   set_robot_movement();
}


/* 
 *  Function Name : set_bot_on_line
 *  Input         : line sensor values
 *  Output        : None
 *  Logic         : When the central line sensor is detecting black area, turn the bot in such a way it detects the black region
 *  Example Call  : set_bot_on_line()
 */
void set_bot_on_line()
{
  int left_sensor_value = analogRead(left_line_sensor);
  int center_sensor_value = analogRead(center_line_sensor);
  int right_sensor_value = analogRead(right_line_sensor);
  right_motor_pwm = right_motor_base_pwm;
  left_motor_pwm = left_motor_base_pwm;
  /*  Black Line: "Greater than/equal to" sensor_threshold
   *  White Line: "Lesser than/equal to" sensor_threshold
   */

  
  /*  Left Sensor on White space
   *  Center Sensor on White space
   *  Right Sensor on Black
   */
  if (left_sensor_value <= left_sensor_threshold &&
      center_sensor_value <= center_sensor_threshold &&
      right_sensor_value >= right_sensor_threshold)
  {
  
  }

  /*  Left Sensor on White space
   *  Center Sensor on Black
   *  Right Sensor on White space
   */

  /*  Left Sensor on Black
   *  Center Sensor on White space
   *  Right Sensor on White space
   */
  else if (left_sensor_value >= left_sensor_threshold &&
           center_sensor_value <= center_sensor_threshold &&
           right_sensor_value <= right_sensor_threshold)
  {
    // LEFT CONDITION;
    bot_position = -1;
    if (robot_movement_direction == 1)
      left_motor_pwm -= motor_speed_variation;
   else if (robot_movement_direction == -1)
      left_motor_pwm += (motor_speed_variation/2);
  }
}
