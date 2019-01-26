#define enable_left_motor 
#define enable_right_motor 
#define forward_left_motor 
#define backward_left_motor 
#define forward_right_motor 
#define backward_right_motor 
#define rpm 50
#define length_of_shaft
#define wheel_diameter

void setup()
{
    pinMode(enable_left_motor, OUTPUT);
    pinMode(enable_right_motor, OUTPUT);
    pinMode(forward_left_motor, OUTPUT);   
    pinMode(backward_left_motor, OUTPUT);
    pinMode(forward_right_motor, OUTPUT);
    pinMode(backward_right_motor, OUTPUT);
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
        digitalWrite(forward_left_motor, HIGH);
        digitalWrite(forward_right_motor, HIGH);
        digitalWrite(backward_left_motor, LOW);
        digitalWrite(backward_right_motor, LOW);
    }
    motor_start_time = millis();
    motor_stop_time = abs(distance*60)/(rpm*3.142*wheel_diameter)
    motor_start_flag = 1;
    digitalWrite(enable_left_motor, HIGH);
    digitalWrite(enable_right_motor, HIGH);
}

void loop()
{
    if (motor_start_flag)
    {
        if ((millis() - motor_start_time) > motor_stop_time)
        {
            digitalWrite(enable_left_motor, HIGH);
            digitalWrite(enable_right_motor, HIGH);
            motor_start_flag = 0;
        }
    }
}