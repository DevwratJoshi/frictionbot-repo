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
int no_of_robots = 80;
  int movers = 318;
int segregators = 2;
float mover_small_frac = 1.0;
int small_movers = int(movers*mover_small_frac);
int large_movers = movers - small_movers;

boolean box_pause = true;
int small = 20;
float big = small*1.73;
float mid = 25;

Vec2 robot1_pos;
Vec2 robot2_pos;
float x_separation = small*2.0*3;
String x_sep_name_list[] = {"4"};
float x_seps[] = {4};
String y_sep_name_list[] = {"1", "1-5", "2", "2-5", "3", "3-5", "4"};
float y_seps[] = {1.0, 1.5,2.0, 2.5, 3.0, 3.5,4.0};

float y_separation = small*2.0*2.5;


int count = 0;
char flag = 'n';
float velConst = 1;
Vec2 vel = new Vec2();

int freq = 60;
int delay = 0;
int record = 0;

char b = 'n';
float box_bottom = small*2*15.0;
float box_height = small*2*8.0;
float box_edge_width = 40;
int mean_box_height;
int velocityDirection;
int amplitude = int(small*6);
Vec2 mouse1, mouse2;
Vec2 temp_mouse = new Vec2();
boolean mouseActive;
int max_record = 10000;
String blah;
float packing_fraction;

int y_sep_counter = 0;
int y_sep_counter_initial =0;
int x_sep_counter = 0;
int x_sep_counter_initial = 0;


int in_counter = 1;
int initial_in_counter = 1;
int in_counter_step = 1;
int in_counter_final =10;

boolean exitFlag = false;

void setup()
{
  size(1200, 800);
  smooth();
 
  box2d = new Box2DProcessing(this, 100);
  box2d.createWorld();
  mean_box_height = 11*height/12;
  in_counter = 0;
  box2d.setGravity(0., 0.);
box = new Box(width/2, height/2 + box_height/2 + box_edge_width/2, 'k');
  robots = new ArrayList<Robot>();
  

  amplitude = (int)(small*4);
  ground = new Ground();
  blah = "initial_x3_y2-5/initial_10" + ".txt";
    

}
void draw() {
  background(255);

  if(count == 0)
  {
    
     in_counter += 1;
    if(in_counter > in_counter_final)
    {
       in_counter = initial_in_counter; 
       y_sep_counter += 1;  
       if(y_sep_counter >= y_sep_name_list.length)
         {
           y_sep_counter  = y_sep_counter_initial;
           x_sep_counter += 1;
          
           if(x_sep_counter >= x_sep_name_list.length)
           {
             x_sep_counter = x_sep_counter_initial;
              exitFlag = true;
               exit();
           }
        } 
     } 
     
     if(!exitFlag)
     create_segregators(x_seps[x_sep_counter]*2.0*small, y_seps[y_sep_counter]*2.0*small); // This increases the count by number of segregators
  }
  if (count < no_of_robots && random(1) < 0.8)
  {
   float ran = random(1);
    
    Vec2 new_pos = new Vec2();
      
    while(true)
    {
      new_pos.x = random(0, width);
      new_pos.y = random(0, height);
      
     if(checkPosAvailable(new_pos, small))
     break;
    }

      Robot p = new Robot(new_pos.x, new_pos.y, small, 'g', 'm');
      
      robots.add(p);
      count++;
     
   
  for(Robot r: robots)
  {
   if (r.type == 'm')
   r.applyRandomVelocity(10); //Velocity of magnitude 2 in a random direction
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
     count = 0;
     write_to_file("initial_x" + x_sep_name_list[x_sep_counter] + "_y" + y_sep_name_list[y_sep_counter] + "/initial_" + str(in_counter) + ".txt");
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
void create_segregators(float x_sep, float y_sep)
{
 ////// Thi is currently hardcoded to have 2 segregators, as that is all I need. Change later to take arguments if required
   Vec2 boxp = box.checkPos();
  
 
  robot1_pos = new Vec2(boxp.x - x_sep/2.0, boxp.y - box_edge_width/2 - box_height/2 - y_sep/2.0);
  robot2_pos = new Vec2(boxp.x + x_sep/2.0, boxp.y - box_edge_width/2 - box_height/2 + y_sep/2.0);
  
  Robot r1 = new Robot(robot1_pos.x, robot1_pos.y, small, 'r', 's');
  robots.add(r1);
  segregators--;
  count++;
  
  Robot r2 = new Robot(robot2_pos.x, robot2_pos.y, small, 'r', 's');
  robots.add(r2);
  segregators--;
  count++;
 
}
void write_to_file(String file_name)
{
  PrintWriter output;
  output = createWriter(file_name);
 int type;
  int r;
  println(segregators + " " + large_movers +  " " + small_movers + "  " + count);
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
