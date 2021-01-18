 int PUL=10; //define Pulse pin
int DIR=9; //define Direction pin
int ENA=5; //define Enable Pin
int del = 1000;
// 6400 steps = 1 rotation of the stapper shaft
// 1 rotation is 71.41 mm
float steps_per_rotation = 800;
float distance_per_rotation = 0.07141;
// Set amplitude to 10 cm
float amplitude = 0.1; 
bool move_flag = false;
long count = 0;
void setup() {
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (ENA, OUTPUT);
  Serial.begin(115200);
  move_flag = false;
}
// The delay is inversely proportional to the velocity. 
// A smaller deley means a larger velocity.
// Steps to get simusoidal velocity. 
// If delay is large enough, 
// Can control time between steps
void loop() {
  int steps = amplitude * steps_per_rotation/distance_per_rotation;

  if(Serial.available())
  {
    char a  = Serial.read();
    if(a == 's')
    {
      move_flag = !move_flag;
    }
  }
  if(move_flag)
  {
      digitalWrite(DIR,LOW);   //Towards the motor
      for (int i=0; i<steps; i++)
      {
        //digitalWrite(ENA,HIGH);
        digitalWrite(PUL,HIGH);
        delayMicroseconds(del);
        digitalWrite(PUL,LOW);
        delayMicroseconds(del);
      }
      
      digitalWrite(DIR,HIGH); //Away from the motor
      for (int i=0; i<steps; i++)   
      {
        //digitalWrite(ENA,HIGH);
        digitalWrite(PUL,HIGH);
        delayMicroseconds(del);
        digitalWrite(PUL,LOW);
        delayMicroseconds(del);
      }
//      Serial.println(count);

  move_flag = false;
  }

  else
  {
    delay(2);
  }
 
}
