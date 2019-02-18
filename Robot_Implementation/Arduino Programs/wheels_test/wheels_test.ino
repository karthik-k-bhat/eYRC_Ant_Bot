// Pin numbers for Motor control with L298D
#define forward_left_motor 4
#define backward_left_motor 7
#define enable_left_motor 5
 
#define forward_right_motor 12
#define backward_right_motor 2
#define enable_right_motor 3

// Parameters of the robot for movements
#define length_of_shaft 26.5
#define motor_rpm 100
#define wheel_diameter 6.8

void setup()
{
    pinMode(enable_left_motor, OUTPUT);
    pinMode(enable_right_motor, OUTPUT);
    pinMode(forward_left_motor, OUTPUT);   
    pinMode(backward_left_motor, OUTPUT);
    pinMode(forward_right_motor, OUTPUT);
    pinMode(backward_right_motor, OUTPUT);

    movement(20);
    delay(1000);
    rotate(90);
    delay(1000);
    movement(-20);
    delay(1000);
    rotate(-90);
    delay(1000);

}

void movement(int distance)
{
    if(distance > 0)
    {
        digitalWrite(forward_left_motor, HIGH);
        digitalWrite(forward_right_motor, HIGH);
        digitalWrite(backward_left_motor, LOW);
        digitalWrite(backward_right_motor, LOW);
    }
    else if(distance < 0)
    {
        digitalWrite(forward_left_motor, LOW);
        digitalWrite(forward_right_motor, LOW);
        digitalWrite(backward_left_motor, HIGH);
        digitalWrite(backward_right_motor, HIGH);
    }
    
    int motor_run_time = (abs(distance)*60)/(motor_rpm*3.142*wheel_diameter)*1000;
    
    digitalWrite(enable_left_motor, HIGH);
    digitalWrite(enable_right_motor, HIGH);
    delay(motor_run_time);
    digitalWrite(enable_left_motor, LOW);
    digitalWrite(enable_right_motor, LOW);
    
}

void rotate(int angle)
{
    if(angle > 0)
    {
        digitalWrite(forward_left_motor, HIGH);
        digitalWrite(forward_right_motor, LOW);
        digitalWrite(backward_left_motor, LOW);
        digitalWrite(backward_right_motor, HIGH);
    }
    else if(angle < 0)
    {
        digitalWrite(forward_left_motor, LOW);
        digitalWrite(forward_right_motor, HIGH);
        digitalWrite(backward_left_motor, HIGH);
        digitalWrite(backward_right_motor, LOW);
    }
    
    int motor_run_time = (length_of_shaft*abs(angle))/(motor_rpm*6*wheel_diameter)*1000;
    
    digitalWrite(enable_left_motor, HIGH);
    digitalWrite(enable_right_motor, HIGH);
    delay(motor_run_time);
    digitalWrite(enable_left_motor, LOW);
    digitalWrite(enable_right_motor, LOW);

}

void loop()
{
}
