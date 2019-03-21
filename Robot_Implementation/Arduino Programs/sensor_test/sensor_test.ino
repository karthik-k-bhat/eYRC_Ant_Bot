#define left_line_sensor A0
#define center_line_sensor A2
#define right_line_sensor A4

void setup()
{
   // For serial communication between Raspberry Pi and Arduino
   Serial.begin(9600);
   pinMode(left_line_sensor, INPUT);
   pinMode(center_line_sensor, INPUT);
   pinMode(right_line_sensor, INPUT);
}

void loop()
{
  int left_sensor_value = analogRead(left_line_sensor);
  int center_sensor_value = analogRead(center_line_sensor);
  int right_sensor_value = analogRead(right_line_sensor);

  /*  Black Line: "Greater than/equal to" sensor_threshold
   *  White Line: "Lesser than/equal to" sensor_threshold
   */
  Serial.print(560);
  Serial.print(" ");
  Serial.print(left_sensor_value);
  Serial.print(" ");
  Serial.print(center_sensor_value);
  Serial.print(" ");
  Serial.print(right_sensor_value);
  Serial.print(" ");
  Serial.println(300);
}
