
#include <Wire.h>               
#include "SparkFun_MMA8452Q.h"  
int PUL=10; //define Pulse pin
int DIR=9; //define Direction pin
int ENA=5; //define Enable Pin

// IMP: Values set in setup function
float steps_per_rotation = 0.;
float distance_per_rotation = 0.0;
float distance_per_step = distance_per_rotation/steps_per_rotation;
float steps_per_metre = steps_per_rotation/distance_per_rotation;
// Set amplitude to 30 cm
float amplitude = 0.; // IMP: This is the peak amplitude and not the peak-to-peak amplitude 
float frequency = 0.;
int current_step = 0;
int velocityDirection = 0; // Will move toward the motor first
// This many steps will be taken for one velocity value (90 steps is about 1mm) 
// It is not worth calculating a new velocity for each new step since each step is so small
int steps_per_velocity_value = 0; 
int steps_per_direction = 0;
bool move_flag = false;
// This function will return a positive velocity if the direction of velocity is toward the motor and -1 if away from the motor
// The initial velocity is always woward the motor

MMA8452Q accel; // To collect container acceleration data

float calculate_position_from_step(int current_step)
{
  float posit = distance_per_step * (float)current_step;
  return posit;
}
float interpolate1D(float x, float x1, float x2, float C1, float C2)
{

  float value = 0;

  if(x < x1)
    return C1;
  
  else if(x > x2)
    return C2;

  if(x1 == x2)
  {
    return C1;
  }
  else if(x2 > x1)
  {
    value = (C1*(x2-x) + C2*(x-x1))/(x2-x1); 
  }
  
  // Return 0 if the first coordinate is smaller than the second
  return value;
}
float calculate_velocity(float pos, float freq, float amplitude)
{
  float new_velocity = 0.;
  // TODO: Calculate an appropriate constVelo 
  float constVelo = 0.001; // 1mm per second
  float maxVelo = 0.;
  float mean_box_xpos = amplitude;
  maxVelo = 2.0*3.14159*freq*2.0*amplitude;
  //maxVelo = 0.01;
  constVelo = 0.1*maxVelo;
  if(constVelo < 0.02)
    constVelo = 0.02;
  if (pos >= amplitude*2.0)
  {
    new_velocity = -constVelo; 
    velocityDirection = -1; // The box will move upward from now on
  } 
  else if (pos < 0)
  {
    new_velocity = constVelo; 
    velocityDirection = 1;
  }

  else
  {
    // IMP: The map function cannot be used for float values. 
    // This needs to be checked, but this may be setting the new_velocity to 0 
    //new_velocity = maxVelo*sin(map(pos, 0.0, amplitude*2.0, radians(6), PI-radians(6)));
    // Using linear interpolation instead of mapping
    
    float interp_pos = interpolate1D(pos, 0.0, amplitude*2.0, -amplitude+0.001, amplitude-0.001);
    new_velocity = 2*PI*freq*sqrt(amplitude*amplitude - interp_pos*interp_pos); //////// New line 
    
    if (velocityDirection == -1)
    {
      new_velocity = -1*abs(new_velocity);
    }
  }

  //println(freq);

  return new_velocity;
}

void setup() 
{
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (ENA, OUTPUT);
  Serial.begin(115200); 
  PUL=10; //define Pulse pin
  DIR=9; //define Direction pin
  ENA=5; //define Enable Pin
  // 6400 steps = 1 rotation of the stapper shaft
  // 1 rotation is 71.41 mm
  steps_per_rotation = 800;
  distance_per_rotation = 0.07161;
  distance_per_step = distance_per_rotation/steps_per_rotation;
  steps_per_metre = steps_per_rotation/distance_per_rotation;
  // Set amplitude to 30 cm
  amplitude = 0.12; // IMP: This is the peak amplitude and not the peak-to-peak amplitude 
  frequency = 0.7;
  current_step = 0;
  velocityDirection = 1; // Will move toward the motor first
  // This many steps will be taken for one velocity value (90 steps is about 1mm) 
  // It is not worth calculating a new velocity for each new step since each step is so small
  steps_per_velocity_value = 5; 
  steps_per_direction = amplitude * steps_per_rotation/distance_per_rotation;
  move_flag = false;
  //TODO: Add block to initialize stage position
  
  accel.init(SCALE_2G, ODR_12); /// Initialize accelerometer
}
// The delay is inversely proportional to the velocity. 
// A smaller deley means a larger velocity.
// Steps to get simusoidal velocity. 
// If delay is large enough, 
// Can control time between steps
void loop() 
{

  if(Serial.available())
  {
    char a  = Serial.read();
    if(a == 's')
    {
      move_flag = !move_flag;
    }
  }


  // Assume that the stage is in the correct position here. 
  
  if(move_flag)
  {                                     
      float velocity = calculate_velocity(calculate_position_from_step(current_step), frequency, amplitude);
      
      int count_direction = 1; // Whether to increase or decrease the current steps. Depends on the direction of the velocity
      if(velocity < 0.0)
      {
        digitalWrite(DIR,HIGH); //Away from the motor is velocity is negative
        count_direction = -1;
      }
      else
      {
        digitalWrite(DIR,LOW);   //Towards the motor if the velocity is positive
        count_direction = 1;
      }
      velocity = abs(velocity);
      float steps_per_sec = velocity * steps_per_metre;
      float del = 0;
      if(steps_per_sec > 1)
      {
        del = 1000000.0/steps_per_sec;
        float del_on = del/4.0;
        float del_off= 3.0*del/4.0;
        // Move for a few steps with this velocity
        // No point calculating a new velocity for each step
        int i = 0;
        for(i = 0; i<steps_per_velocity_value; i++)
        {
          digitalWrite(PUL,HIGH);
          delayMicroseconds(del_on);
          digitalWrite(PUL,LOW);
          delayMicroseconds(del_off);
        }
        current_step = current_step + count_direction*steps_per_velocity_value;
      }  

//      if(accel.available())
//      {
//        Serial.println(accel.getX());
//        //Serial.print(",");
//        //Serial.print(millis());
//        //Serial.println();
//      }
  }
  else
  {
    delay(2);
  }
}
