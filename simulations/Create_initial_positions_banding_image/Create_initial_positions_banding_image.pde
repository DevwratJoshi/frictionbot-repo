// VolBot simulator using the jave-processing ported version of box2D by shiffman

import shiffman.box2d.*;
import org.jbox2d.collision.shapes.*;
import org.jbox2d.common.*;
import org.jbox2d.dynamics.*;
import org.jbox2d.dynamics.joints.*;

Box2DProcessing box2d;

Box box;
int steps = 0; // keeps track of the number of times the world has stepped
final int DELAY = 300;
// A list for all of our rectangles
ArrayList<Robot> robots;
Ground ground;
int no_of_robots = 267; // 267 for 40 by 10
int high_mobility = 134;
int low_mobility =  133;
int low_mob_count = 0;
int high_mob_count = 0;
boolean box_pause = true;
int small = 20;
float big = small*1.73;
float mid = 25;

Vec2 robot1_pos;
Vec2 robot2_pos;

int count = 0;
char flag = 'n';
float velConst = 1;
Vec2 vel = new Vec2();

int freq = 60;
int delay = 0;
int record = 0;

char b = 'n';
float box_bottom = small*2*40.0;
float box_height = small*2*10.0;
float box_edge_width = 40;
float mean_box_height;
int velocityDirection;
int amplitude = int(small*6);
Vec2 mouse1, mouse2;
Vec2 temp_mouse = new Vec2();
boolean mouseActive;
int max_record = 10000;
String blah;
float packing_fraction;
int in_counter = 0;
int initial_in_counter = 1;
int in_counter_step = 1;
int in_counter_final =10;

boolean exitFlag = false;

void setup()
{
  frameRate(1000);
  size(2000, 800);
  smooth();    
  box2d = new Box2DProcessing(this, 100);
  box2d.createWorld();
  mean_box_height = height/2 + box_height/2 + box_edge_width/2;
  in_counter = 0;
  box2d.setGravity(0., 0.);
  box = new Box(width/2, mean_box_height, 'k');
  robots = new ArrayList<Robot>();
  amplitude = (int)(small*4);
  ground = new Ground();
  blah = "initial_x3_y2-5/initial_10" + ".txt";
}
void draw() {
  background(255);

  if(steps == 0)
  {
    
     in_counter += 1;
     println("in_counter = " + in_counter);
    if(in_counter > in_counter_final)
    {
       in_counter = initial_in_counter; 
       exit();
             
     } 
  }  
  if (count < no_of_robots && random(1) < 0.8)
  {
    
    Vec2 new_pos = new Vec2();
    boolean space_available = false;
    if(high_mobility > high_mob_count)
    {
     for(int i = 0; i < 100; i++)
      {
        new_pos.x = random(0, width);
        new_pos.y = random(0, height);
        
       if(checkPosAvailable(new_pos, small))
       {
        space_available = true;
        break; 
       }
       
      }
        if(space_available)
          {
            Robot p = new Robot(new_pos.x, new_pos.y, small, 'g', 'm');
            robots.add(p);
            count++;
            high_mob_count++;
          }
    }
    space_available = false;
    if(low_mobility > low_mob_count)
    {
       for(int i = 0; i < 100; i++)
      {
        new_pos.x = random(0, width);
        new_pos.y = random(0, height);
        
       if(checkPosAvailable(new_pos, small))
       {
        space_available = true;
        break; 
       }
      }
    if(space_available)
          {
              Robot p = new Robot(new_pos.x, new_pos.y, small, 'r', 's');
              robots.add(p);
              count++;
              low_mob_count++;
          }
    }
    
  for(Robot r: robots)
  {
   r.applyRandomVelocity(2.5); //Velocity of magnitude 2 in a random direction
  }
    
 }

  // We must always step through time!
  box2d.step();
  steps++;

  // Display all the boundaries
  box.display();
  ground.display();

  for (Robot p : robots) {
    p.display();
  }


  if(count >= no_of_robots)
  {
    println("Count greater than no of robots");
     count = 0;
     steps = 0;
     high_mob_count = 0;
     low_mob_count = 0;
     write_to_file("initial_positions/box_width_40" + "/initial_" + str(in_counter) + ".txt");
     for (int i = robots.size()-1; i >= 0; i--)
       {
        Robot p = robots.get(i);
        p.killBody();
        robots.remove(i);
       }
      robots = new ArrayList<Robot>();
       box2d.step(1/60.0, 8,3); // Not sure if required. Give it a step to remove the robots from the internal cals
  }

}

/*
This function will check if placing a robot of radius rad at position indicated by pos will overlap with any robots already created 
*/
boolean checkPosAvailable(Vec2 pos, float rad)
{
  if(!robot_in_box(pos, rad))
  return false;
  
  for(Robot r : robots)
  {
   Vec2 r_pos = new Vec2();
   r_pos = r.checkPos();
   if(sqrt(square(r_pos.x-pos.x) + square(r_pos.y-pos.y)) < rad + r.r)
   {
    return false; 
   }
  }
  return true;
}

void write_to_file(String file_name)
{
  PrintWriter output;
  output = createWriter(file_name);
 int type;
  int r;
  println(high_mobility + " " + low_mobility + "  " + count);
  for (int i = robots.size()-1; i >= 0; i--) {
    Robot p = robots.get(i);

    switch(p.type) // Easier to read ints that chars so 1 for segregator an 2 for mover
    {
     case 's':
     {
     type = 1;
     break;
     }
     
     case 'm':
     {
     type = 2;
     break;
     }
     default:
     type = 2;
     
    }
    if(p.r == big)
    r = 1;
    
    else 
    r = 2;
   // We want the coordinates in terms of the position of the box
    output.println((int)(p.checkPos().x - box.checkPos().x + box_bottom/2) + " " + (int)(box.checkPos().y - p.checkPos().y)+ " " + r + " " + type);
  }
  output.flush();
  output.close();
  println(file_name); 
}
// This function checks if the robot is within the box

boolean robot_in_box(Vec2 pos, float rad)
{
  Vec2 b_pos = box.checkPos();
  if(b_pos.x - box_bottom/2 + rad <= pos.x && b_pos.x + box_bottom/2 - rad >= pos.x && b_pos.y - box.checkWidth()/2 - rad >= pos.y && b_pos.y - box.checkWidth()/2 - box.checkHeight() + rad <= pos.y)
    return true;
  
  return false;
  
}

float square(float a)
{
 return a*a; 
}
