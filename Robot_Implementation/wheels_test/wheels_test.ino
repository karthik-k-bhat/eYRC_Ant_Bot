const int en_a = 2;
const int in_a1 = 3;
const int in_a2 = 4;
const int in_b1 = 5;
const int in_b2 = 6;
const int en_b = 7;

void setup()
{
   Serial.begin(9600);
   pinMode(en_a, OUTPUT);
   pinMode(en_b, OUTPUT);
   pinMode(in_a1, OUTPUT);
   pinMode(in_a2, OUTPUT);
   pinMode(in_b1, OUTPUT);
   pinMode(in_b2, OUTPUT);
}
int inertia_time = 0;
void loop()
{
   if(Serial.available())
   {
      char data = Serial.read();
      if (data == 'F')
      {
         digitalWrite(in_a1, HIGH);
         digitalWrite(in_a2, LOW);
         digitalWrite(in_b1, HIGH);
         digitalWrite(in_b2, LOW);

         digitalWrite(en_a, HIGH);
         digitalWrite(en_b, HIGH);
         delay(1000);

         digitalWrite(in_a1, LOW);
         digitalWrite(in_a2, HIGH);
         digitalWrite(in_b1, LOW);
         digitalWrite(in_b2, HIGH);

         delay(inertia_time);
         digitalWrite(en_a, LOW);
         digitalWrite(en_b, LOW);
      }
      else if (data == 'B')
      {
         digitalWrite(in_a1, LOW);
         digitalWrite(in_a2, HIGH);
         digitalWrite(in_b1, LOW);
         digitalWrite(in_b2, HIGH);

         digitalWrite(en_a, HIGH);
         digitalWrite(en_b, HIGH);
         delay(1000);

         digitalWrite(in_a1, HIGH);
         digitalWrite(in_a2, LOW);
         digitalWrite(in_b1, HIGH);
         digitalWrite(in_b2, LOW);

         delay(inertia_time);
         digitalWrite(en_a, LOW);
         digitalWrite(en_b, LOW);
      }
      else if (data == 'R')
      {
         digitalWrite(in_a1, HIGH);
         digitalWrite(in_a2, LOW);
         digitalWrite(in_b1, LOW);
         digitalWrite(in_b2, HIGH);

         digitalWrite(en_a, HIGH);
         digitalWrite(en_b, HIGH);
         delay(1000);

         digitalWrite(in_a1, LOW);
         digitalWrite(in_a2, HIGH);
         digitalWrite(in_b1, HIGH);
         digitalWrite(in_b2, LOW);

         delay(inertia_time);
         digitalWrite(en_a, LOW);
         digitalWrite(en_b, LOW);
      }
      else if (data == 'L')
      {
         digitalWrite(in_a1, LOW);
         digitalWrite(in_a2, HIGH);
         digitalWrite(in_b1, HIGH);
         digitalWrite(in_b2, LOW);

         digitalWrite(en_a, HIGH);
         digitalWrite(en_b, HIGH); 
         delay(1000);

         digitalWrite(in_a1, HIGH);
         digitalWrite(in_a2, LOW);
         digitalWrite(in_b1, LOW);
         digitalWrite(in_b2, HIGH);

         delay(inertia_time);
         digitalWrite(en_a, LOW);
         digitalWrite(en_b, LOW);
      }
   }
}
