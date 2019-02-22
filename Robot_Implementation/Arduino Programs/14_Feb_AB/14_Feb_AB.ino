/* Last Modified on: 18-Feb-2019
 * Last Modified by: Vishwas N S
 * Last Modified details: 
 * 1. Backward movement fix. 
 *
 * To-Do
 * 1. Add PID to line following to make it smooth
 * 2. Place Mechanism with robot movements 
 */

/*
 * Team ID          : 226
 * Authors          : Karthik K Bhat, Vishwas N S, Shreyas R
 * File Name        : eYRCAB226.ino
 * Theme            : Antbot
 * Functions        : 
 * Global variables : 
 */

// Include the required Library Files
#include <Servo.h>

// PD Values for line correction (PID where Ki = 0)
#define Kp 0.5
#define Kd 1

// Pin numbers for line sensors
#define left_line_sensor A0
#define center_line_sensor A2
#define right_line_sensor A4

// Motor parameter to control the speeds
#define right_motor_base_pwm 255                    // Base pwm - Such that the robot goes in a straight line   
#define left_motor_base_pwm 255
#define motor_speed_variation 100
#define motor_low_speed_value 100

// Pin numbers for Motor control with L298D
#define forward_left_motor 7
#define backward_left_motor 4
#define enable_left_motor 5

#define forward_right_motor 12
#define backward_right_motor 2
#define enable_right_motor 3

// Parameters of the robot for movements
#define length_of_shaft 26.5
#define motor_rpm 100
#define wheel_diameter 6.8

// Pin numbers for Servo pins and buzzer
#define grabber_servo_pin 6
#define lift_servo_pin 9
#define camera_servo_pin 10

#define buzzer 8

// Instances for servo motors
Servo grabber_servo;
Servo lift_servo;
Servo camera_servo;

// Global Variables Declaration
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
 *  +3  T or + Node
 */
int bot_position;                           // To identify the last known position of the bot
bool camera_position;                       // 0 - Downwards, 1 - Upwards
bool pick_place_flag;                       // 0 - Pick Supply, 1 - Deliver supply
bool job_done_flag = 0;                     // Flag to denote if a job was completed or not
bool white_space_stop = 0;                  // Flag to stop the bot if white space was detected by the line sensor

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
    *  Lift servo: 0 -> Up, 28 -> Down
    *  Grab servo: 0 -> Open, 180 -> Close
    *  Camera servo: 120 -> Up 70 -> Down facing 
    */
   
   lift_servo.write(0);
   grabber_servo.write(0);
   pick_place_flag = 0;

   camera_servo.write(70);
   camera_position = 1;

   // To calibrate line sensor
   delay(500); //Wait for sensors to stabilize
   line_sensor_calibrate();

   //Send a singal to Pi saying setup is done.
   Serial.print("Job done");
}

// Default arduino loop function - to keep executing the instructions indefintely
void loop()
{
   /* Serial Communnication instructions:
    *  1. Move: 'M' followed by direction integer. 1 for Forward, -1 for Backward, 0 for Stop
    *  2. Turn: 'T' followed by direction angle. Positive for clockwise (right-side), Negative for counter-clockwise (left-side)
    *  3. Buzzer: 'B'
    *  4. Pick and Place mechanism: 'P'
    *  5. Camera servo: 'C'
    *  6. Move a certain distance: 'O' followed by the distance. Positive is front, Negative is back 
    *  7. Stop when white space is detected: 'W'
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
           analogWrite(enable_left_motor, left_motor_base_pwm-50);
           analogWrite(enable_right_motor, right_motor_base_pwm-50);
           delay((3*60)/(motor_rpm*3.142*wheel_diameter)*1000);                         // Move front, away from node (3 cms).
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
                 bot_position = 0;
                 break;
              }
           }
        }
     }
     else if (data == 'T')
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

        // Keep the motor running until the robot rotates the given angle
        // Formuala to caculate time delay in seconds = (angle_to_rotate * length_between_wheels)/(rpm_of_motor * 6 * diameter_of_wheel)
        delay((length_of_shaft*abs(angle))/(motor_rpm*6*wheel_diameter)*1000);

        // Stop the motors
        robot_movement_direction = 0;
        set_robot_movement();
     }

     // To beep the buzzer
     else if (data == 'B')
     {
        digitalWrite(buzzer, HIGH);
        delay(5000);
        digitalWrite(buzzer, LOW);
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
           camera_servo.write(55);
           camera_position = 0;
        }
        else
        {
           camera_servo.write(70);
           camera_position = 1;
        }
        
     }
     
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
          analogWrite(enable_left_motor, left_motor_base_pwm);
          analogWrite(enable_right_motor, right_motor_base_pwm);

        // Keep the motor running until the robot travels the given distance
        // Formuala to caculate time delay in seconds = (distance_to_travel * 60)/(rpm_of_motor * pi * diameter_of_wheel)
        delay((abs(distance)*60)/(motor_rpm*3.142*wheel_diameter)*1000);

        // Stop the motors by cancelling the inertia
        
        digitalWrite(enable_left_motor, LOW);
        digitalWrite(enable_right_motor, LOW);
        cancel_inertia();
     }
     else if (data == 'W')
     {
        // Stop the bot when white space is found. Set the flag
        white_space_stop = 1;
     }

     // Set the job done flag.
     job_done_flag = 1;
   }
   
  // If job is done, send "Job done" signal to Pi
  if(job_done_flag)
  {
    Serial.println  ("Job done");
    // Clear the flag and wait for next command
    job_done_flag = 0;  
  }
   
}

/* 
 *  Function Name : Movement
 *  Input         : None
 *  Output        : bool value - 0 robot being a node, 1 robot being on the line
 *  Logic         : 1. To check the robot position using line sensor
 *                  2. Change the speeds of the motors at different speed if bot is found not on line
 *                  3. Run motor at base speed if bot is found going on line
 *                  4. Stop the bot at node or when white_space_stop is requested
 *                  5. If a node/white space(with white_space_stop flag set) is identified, return 0, else return 1
 *  Example Call  : movement()
 */
 int movement()
{
  int error = get_bot_position();
  int right_motor_pwm = right_motor_base_pwm;
  int left_motor_pwm = left_motor_base_pwm;
  
  if((abs(error) == 2 || error == 3) || (error == -3 && white_space_stop))
  {
     // Stop the robot
     robot_movement_direction = 0;
     set_robot_movement();

     // Send the message to display on the serial monitor
     if (error == -2)
        Serial.println("Left-branched Node");
     else if (error == 2)
        Serial.println("Right-branched Node");
     else if (error == 3)
        Serial.println("T-branched Space Node");
     else if (error == -3)
     {
        Serial.println("White Space");
        // Clear the white_space_stop flag once white space is detected
        white_space_stop = 0;
     }
     return 0;
  }
  else
  {
     if(error == -3 && bot_position == 1)                        // Turn Left
        right_motor_pwm -= motor_speed_variation;
        
     else if(error == -3 && bot_position == -1)                    // Turn Right
        left_motor_pwm -= motor_speed_variation;

     // Run the motor at set speeds
     analogWrite(enable_left_motor, left_motor_pwm);
     analogWrite(enable_right_motor, right_motor_pwm);
     return 1;
  }
}

/* 
 *  Function Name : line_sensor_calibrate
 *  Input         : None
 *  Output        : None
 *  Logic         : 1. Keep robot on the white area before the start node.   
 *                  2. Read the line sensor value for white area
 *                  3. Move the robot until a large jump in the values is observed
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

   int left_jump_value = 0, right_jump_value = 0, center_jump_value = 0;

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
   
   analogWrite(enable_right_motor, motor_low_speed_value);
   analogWrite(enable_left_motor, motor_low_speed_value);

   delay(125);            // Move 2 cms

   left_black_value = analogRead(left_line_sensor);
   center_black_value = analogRead(center_line_sensor);
   right_black_value = analogRead(right_line_sensor);
  
   // Move the bot front until there is a large jump in the line sensor values
   /*
   while(left_jump_value < 100 && center_jump_value < 100 && right_jump_value < 100)
   {
      // Read the analog values
      left_black_value = analogRead(left_line_sensor);
      center_black_value = analogRead(center_line_sensor);
      right_black_value = analogRead(right_line_sensor);

      // Calculate the jump in the value
      left_jump_value = left_black_value - left_white_value;
      center_jump_value = center_black_value - center_white_value;
      right_jump_value = right_black_value - right_white_value;
   }
   */
   robot_movement_direction = 0;
   set_robot_movement();
   
   Serial.print("Left sensor black value ");
   Serial.print(left_black_value);
   Serial.print(", Center sensor black value ");
   Serial.print(center_black_value);
   Serial.print(", Right sensor black value ");
   Serial.println( right_black_value);  

   /*
   left_sensor_threshold = ((left_black_value + left_white_value) / 2);
   center_sensor_threshold = ((center_black_value + center_white_value) / 2);
   right_sensor_threshold = ((right_black_value + right_white_value) / 2);
   */

   left_sensor_threshold = (left_black_value - (left_black_value - left_white_value)/4);
   center_sensor_threshold = (center_black_value - (center_black_value - center_white_value)/4);
   right_sensor_threshold = (right_black_value - (right_black_value - right_white_value)/4);
   
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
    bot_position = 1;
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


/* 
 *  Function Name : cancel_inertia
 *  Input         : None
 *  Output        : None
 *  Logic         : When the robot is moving one direction, make the robot move in the opposite direction for very small distance
 *                  so that the inertia in the motor is nullified.
 *  Example Call  : cancel_inertia()
 */
void cancel_inertia()
{
   // Set the direction of the robot in opposite direction
   robot_movement_direction *= -1;
   set_robot_movement();
   
   // Run the motors for a short time to cancel the inertia of rotation
   delay((2*60)/(motor_rpm*3.142*wheel_diameter)*1000);

   // Stop the motors.
   robot_movement_direction = 0;
   set_robot_movement();
}


/*
int movement_without_pwm()
{
   int error = get_bot_position();
   if (abs(error < 2))
   {
      analogWrite(enable_left_motor, left_motor_base_pwm);
      analogWrite(enable_right_motor, right_motor_base_pwm);
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

// PD Code:
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
*/
