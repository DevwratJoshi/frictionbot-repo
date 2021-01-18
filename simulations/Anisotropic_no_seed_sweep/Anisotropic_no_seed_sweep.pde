// VolBot simulator using the jave-processing ported version of box2D by shiffman
// In this simulation, the box shakes side to side. This is to give us a wider range to take videos with
import shiffman.box2d.*;
import org.jbox2d.collision.shapes.*;
import org.jbox2d.common.*;
import org.jbox2d.dynamics.*;
import org.jbox2d.dynamics.joints.*;

Box2DProcessing box2d;

Box box;
final float stepsPerSec = 100.0;  
final float big_diameter = 1.73; // The diameter ratio of actual robot_large to actual robot_small
final float segregator_frac = 0.1; // fraction of modules that are segregators
int maxSteps = 5000;
float small = 20;
float big = small*big_diameter;
float segregator_size = big; // Fixed segregator size



//Worth noting here that dataCollectionRate seconds between sims and readings_per_sim readings means dataCollectionRate*readings_per_sim seconds for a group of conditions 

int steps = 0; // keeps track of the number of times the world has stepped

final int DELAY = 10;
// A list for all of our robots
ArrayList<Robot> robots;
ArrayList<Vec2> path;
//Ground ground;
int no_of_robots = 120;
int large_robots = 0;
int small_robots = 0; 
float packing_fraction;
int count = 0;
char flag = 'n';
float velConst = 1;
Vec2 vel = new Vec2();
boolean box_pause = true;

float density_small = 6.5; // Actual density of the small robot
float fric_low = 0.05; // Approximate friction of PTFE on PTFE
float fric_high = 0.7; // Friction of rubber on polyurethane (not PTFE, but actual values might be similar)
   
int delay = 0;
int record = 0;
float box_bottom = small*2*40.0;  
float box_height = small*2*10.0;
float box_edge_width = 40;
float mean_box_height;
Vec2 center_pos, center_velo;
int velocityDirection = 1;

Vec2 mouse1, mouse2;
Vec2 temp_mouse = new Vec2();
boolean mouseActive;
String in_folder = "initial_positions/box_width_15/";
String in = "initial_positions_";
String data_folder = "data/corrected_mass/"; // Remember to move the data files into the appropriate folders
PrintWriter output_data, output; // The output file for initial positions, final positions
String output_data_filename = "";
String extention; // The extention for the files

boolean blueBallSelected = false;
BufferedReader reader;
int fileCounter;
float probability = 0.1; // The initial value of the probability
final float probIncrease = 0.1; // The amount the probability will increase per loop

boolean dataCollectMode = false;
Vec2 lastBoxPos = new Vec2(0, 0);
float SavedBoxHeight = 0.;

int ampNumber = 0;


boolean exitFlag = false; // exit() does not let the program exit immidiately. It will execute draw one last time, which might be troublesome. 
// Do not let anything else run if exitFlag is true

boolean to_collect_data = false;

int in_counter = 1;  

int initial_in_counter = 1;
int in_counter_step = 1;
int in_counter_final = 5;


//float freqs[] = {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9};  
float freqs[] = {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9};
int freq_counter = 0;


//int amplitudes[] = {(int)small, 2*(int)small,3*(int)small, 4*(int)small, 5*(int)small, 6*(int)small, 7*(int)small, 8*(int)small, 9*(int)small, 10*(int)small};
int amplitudes[] = {3*(int)small, 4*(int)small, 5*(int)small, 6*(int)small, 7*(int)small, 8*(int)small, 9*(int)small, 10*(int)small};
int amp_counter = 0;
//String seperations[] = {"2", "3","4","5","6","7"}; // The seperations for which data is available
String x_separations[] = {"2"};//, "3", "4"};//,"10", "12", "14", "16", "18", "20"};
//String y_separations[] = {"0", "1", "2", "3", "4", "5", "6"};
String y_separations[] = {"2"};//"2-5", "3", "3-5" ,"4"};
int x_separations_counter = 0; // counter to keep track of which seperation is currently being simulated
int y_separations_counter = 0;
int number_of_segregators = 0;
void setup()
{
  frameRate(400);
  size(2000, 1000);
  smooth();

  box2d = new Box2DProcessing(this, 100); /// This is the ratio of pixels to m.

  box2d.createWorld();
  box2d.setGravity(0, 0.0);
  mean_box_height = height/2 + box_height/2 + box_edge_width/2;

  robots = new ArrayList<Robot>();
  path = new ArrayList<Vec2>();
  center_velo = new Vec2();
  center_pos = new Vec2();
  //ground = new Ground();
   
  in_counter = initial_in_counter - in_counter_step; // Initial setSimulationConditions will add in_counter_step to in_counter
  extention = ".txt";
   
  //output = createWriter(data_folder + "README");
  //output.println("frequency = " + str(freq) + " amp = " + str(amplitude));
  ///output.println("big diameter = " + str(int(big)) + "\n small diameter = " + str(int(small)));
  //output.println("number of robots = " + str(no_of_robots));
  //output.println("box_bottom = " + str(int(box_bottom)));
  //output.println("friction_low = " + str(fric_low) + " friction_high = " + str(fric_high));
 // output.flush();
 // output.close();
}

void draw() {   
  if (steps == 0)
  {
    setSimulationConditions();
    if(!exitFlag)
    {
      // Creating the box
      box = new Box(width/2, mean_box_height, 'd');
      robots = new ArrayList<Robot>();
      /// End creating the box
  
      //////// Creating new robots using data from initial_positions.txt
      String file_name = in_folder + "initial_x" + x_separations[x_separations_counter] + "_y" + y_separations[y_separations_counter] + "/initial_" +str(in_counter)  +  extention;
      println(file_name);
      createRobots(file_name);
      /////// End of creating robots
      //output_data.println(segregatorPos(true).x + "," + segregatorPos(true).y + "," + segregatorPos(false).x + "," + segregatorPos(false).y + "," + robotCOM().x + "," + robotCOM().y + "," + record);
      //////// Setting delay to zero
      delay = 0;
      ///////// End setting delay to zero
           ///////////// Robots must all be the correct size initially. Check the initial lambda before shaking begins
           
    }
  }
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  
  /*
    If the dataCollectMode is made true, the following sequence will be initiated. 
    The following steps are taken
    1) The box is stopped by making boxPause = true
    2) The function waits for all the robots to stop moving. Set the initial positions of the robots and check that they do not move. 
    N.B. Check that the integer values of the postions are the same as the last timestep
  */
  if(!exitFlag)
  {
      background(255);
      try {
        box2d.step(1/stepsPerSec, 8, 3);
      }
      catch(AssertionError err)
      {
       err.printStackTrace(); 
       delay = 0;
       output_data  = createWriter(output_data_filename);
       output_data.print("Failed\n");
       output_data.flush();
       output_data.close();
       
       steps = 0;
      
      } //<>//
      steps++;
      //box_pause = false;
      // Display all the boundaries
     // box.display();
      //ground.display();
  
      //displayRobots();
  
    if(delay == DELAY)
      {
        //Vec2 bpos = new Vec2();
        //bpos = box.checkPos();
        //box.killBody();
        //box = new Box(bpos.x, bpos.y, 'd');
        box_pause = false;
        
      }
  
      delay++;
      if (delay > DELAY)
      {
        record++;
        display_sim_conditions();
  //////////////////////////// Shake box block  
  
        if (!box_pause)
        {
          box.applyVelocity(calcVelocity(box.checkPos()));
        } 
        
        else if (box_pause)
        {
          vel.x = 0.;
          vel.y = 0.;
          box.applyVelocity(vel);
        }
  //////////////////////////// End shake box block
  

  
        Vec2 box_vel = box.checkLinearVelocity();
       for (int i = robots.size()-1; i >= 0; i--) 
       {
        Robot p = robots.get(i);
        //println(p.r);
        p.applyFrictionForce(box_vel);
        
      }
    
      } /////////End of delay
      
      ///////////////////////// Change robot size block
      //for(int i = robots.size()-1; i >=0; i--)
      //{
      // Robot r = robots.get(i);
      // if(robotInWall(r))
      // {
      //   //if(r.isSeed)
      //   //r.changeRadius(big);
      //   r.changeFriction(fric_high);
         
      //   if(r.type == 'm')
      //   r.colour = 'y';
      // }
       
      // else
      // {
      //  if(r.type == 'm')
      //  { //<>//
      //   r.changeRadius(small);
      //   r.changeFriction(fric_low);
      //   r.colour = 'g';
      //  }
      // }
       
      //}
//////////////////////////// End Change robot size block

    

      ///// Start storing data points
      // Store position every 10th step (10 data_points per second). Too many positions otherwise
      if(record %10 ==0)
      {
        ////////// Start storing segregator positions
        Vec2 segregator_positions[] = new Vec2[number_of_segregators]; 

        for(Robot r : robots)
        {
            if(r.segregator_id >0)
            {
               segregator_positions[r.segregator_id-1] = r.checkPos(); // Segregator ids start from 1
            }
        }
        //////// End storing segregator positions
        Vec2 curr_box_pos = box.checkPos();
        for(int i = 0; i < number_of_segregators; i++)
        {
          output_data.print((int)segregator_positions[i].x + "," + (int)segregator_positions[i].y+ ",");
        }
        output_data.print((int)curr_box_pos.x + "," + (int)curr_box_pos.y + ",");
        output_data.print("\n");
        output_data.flush();
      }
      packing_fraction = 0.;
      if(record >= maxSteps) //|| segregatorsTouching())
      {
       // output_data.println(segregatorPos(true).x + "," + segregatorPos(true).y + "," + segregatorPos(false).x + "," + segregatorPos(false).y + "," + robotCOM().x + "," + robotCOM().y + "," + record);
        output_data.flush();
        output_data.close();

       
        steps = 0;
       record = 0;

      }
      
      
      pushMatrix();
      noStroke();
      fill(100, 0, 0);
      ellipse(width/2, height, amplitudes[amp_counter]*2, amplitudes[amp_counter]*2);
      Vec2 meh = new Vec2();
      meh = box.checkPos();
      stroke(0, 0, 100);
      line(meh.x, meh.y, meh.x, height);
      popMatrix();

  }
  
  else // If exitFlag is true
  {
   exit(); 
  }



}


/////////////////////////////////////////////// End of draw

boolean segregatorsTouching()
{
 for(int i = robots.size()-1; i >=0; i--)
 {
   Robot p = robots.get(i);
   if(p.type == 's')
   {
     for(int j = robots.size()-1; j >=0; j--)
       {
        if(i != j)
          {    
            Robot q = robots.get(j);
            if(q.type == 's')
              {
                  if(vec_diff(p.checkPos(), q.checkPos()) <= p.r+q.r)
                  return true;
              }
          }
       }
   }
 }
 
 return false;
}

void display_sim_conditions()
{
  pushMatrix();
  fill(0, 102, 153);
  textSize(32);
  //text("Frequency = " + str(freqs[freq_counter]) + "    Friction_red = " + str(fric_low), 120, 30); 
  //text("Amplitude = " + str(amplitudes[amp_counter]) + "     Friction_green = " + str(fric_low), 120, 60);
 // float robot_area = 0.;

  text("Frame_rate = " + frameRate, 120, 100);  
  text("Max record = " + maxSteps, 120, 200);
  text("Current record = " + record, 600, 200);
  popMatrix();
  
}
float vec_diff(Vec2 a, Vec2 b) //A helper function to calculate the euclidean distance between a and b
{
  float diff = 0.;
  
  diff = sqrt((a.x-b.x)*(a.x-b.x) + (a.y-b.y)*(a.y-b.y));
  
  return diff;
}

void write_to_file(PrintWriter f)
{  
  Vec2 b_pos = box.checkPos();
  for(Robot r : robots)
  {
    Vec2 pos = r.checkPos();
    //f.println(robot_initials[0] + "," + robot_initials[1] + "," + robot_initials[2] + "," + robot_initials[3] + "," + (pos.x - b_pos.x + box_bottom/2)/(small*2) + "," + (b_pos.y - pos.y)/(small*2) + "," + r.type + "," + r.friction_with_bed + "," + r.r + "," + packing_fraction); // Storing the radius and the friction of the robot
  }
  f.flush();
  f.close();

}

boolean robotInWall(Robot r) // This determines if the robot is to form part of the wall
{
  
  if(r.isSeed)
  {
    return true;
  }
  else if(r.type == 'm')
  {
   for(Robot p: robots)
   {
    if(p.type == 's')
    {
     if(vec_diff(p.checkPos(), r.checkPos()) <= (r.r+p.r))
     {
       if(!p.isSeed) // become small if in contact with segregator that is not the seed
       return false;
       
      if(p.isSeed)
      return true; 
     }
    }
   }
  }
  
  return false;
  
}

/////////////////////////////////////////////// 
void displayRobots()
{
  for (Robot p : robots)
  {
    p.display();
  }
}




void createRobots(String input)
{
  robots = new ArrayList<Robot>();
  reader = createReader(input);
  String line = null;
  large_robots = 0;
  small_robots = 0;
  int segregators = 0;
  int movers = 0;
 float r = 0.;
 char col;

 char t;
  try {
   while ((line = reader.readLine()) != null) 
    {
      //println(line);
      int[] nums = int(split(line, " "));
      char colour = 'g';
         float d;
          float f;
         
         if(nums[3] == 1)
        {
          d = density_small;
          col = 'r';
          f = fric_high;
          t = 's';
         
          
          //output_data.flush();
        }  
        else
        {
          d = density_small;
          col = 'g';
          f= fric_low;
          t = 'm';
        }
        if(nums[2] == 1) // 1  for big, 2 for small
        {
          r = big; 
        }
        else
          r = small;
          
          Robot p = new Robot(box.checkPos().x - box_bottom/2 + nums[0], box.checkPos().y - nums[1], r, col, true, d, f, t); // Segregator
           
          if(p.type=='s')
          {
            segregators = segregators+1;
            p.segregator_id = segregators;
          }
          robots.add(p);
    }
    reader.close();
  } 
  catch (IOException e) 
  {
    e.printStackTrace();
  }
  
  number_of_segregators = segregators; // Store the number of segregators
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
Vec2 calcVelocity(Vec2 box_pos)
{
  Vec2 new_velocity = new Vec2();
  float constVelo = 0.1;
  float maxVelo;
  int section = 0;
  float mean_box_xpos = width/2;
  maxVelo = 2*PI*freqs[freq_counter]*amplitudes[amp_counter]/100.0;
  //println("maxvelo = " + maxVelo);
  constVelo = 0.1*maxVelo;
  if(constVelo < 0.1)
  constVelo = 0.1;
  if (box_pos.x >= width/2 + amplitudes[amp_counter])
  {
    new_velocity.x = -constVelo;
    velocityDirection = -1; // The box will move upward from now on
    section = 1;
  } 
  else if (box_pos.x <= width/2 - amplitudes[amp_counter])
  {
    new_velocity.x = constVelo; 
    velocityDirection = 1;
    section = 2;
  }

  else
  {
    float pos = interpolate1D(box_pos.x, mean_box_xpos - amplitudes[amp_counter], mean_box_xpos + amplitudes[amp_counter], -amplitudes[amp_counter], amplitudes[amp_counter]);
    
    new_velocity.x = 2*PI*freqs[freq_counter]*sqrt(amplitudes[amp_counter]*amplitudes[amp_counter] - pos*pos)/100.0;
    if (velocityDirection == -1)
    {
      new_velocity.x = -1*new_velocity.x;
    }
    section = 5;
  }

  //println(freq);
   
  return new_velocity;
}

//void setSimulationConditions()
//{
  // in_counter += 1;
  // if(in_counter > in_counter_final)
    // {
     //  output_data.flush();
    //   output_data.close();
    //   exitFlag = true;
 //    }  

  //  if(!exitFlag)
   //    output_data = createWriter(data_folder + "data" + str(in_counter) + extention); 
     
//}
void setSimulationConditions()
{
  box2d = new Box2DProcessing(this, 100); /// This is the ratio of pixels to m.
  box2d.createWorld();
  box2d.setGravity(0, 0.0);
  in_counter += 1;
  if(in_counter > in_counter_final)
  {
     in_counter = initial_in_counter; 
      amp_counter += 1;  
     if(amp_counter >= amplitudes.length)
       {
         amp_counter = 0;
         freq_counter += 1;
         //freq = float(freq * 100.0/100);
         if(freq_counter >= freqs.length)
         {
           freq_counter = 0;
           y_separations_counter += 1;
          if(y_separations_counter >= y_separations.length)
          {
             y_separations_counter = 0;
             x_separations_counter +=1;
               if(x_separations_counter >= x_separations.length)
                 {
                   println("This is the end of the program");
                   exitFlag = true;
                   exit();
                 }
           }
        } 
   }
 }
  
   maxSteps =(int)(30.0 * stepsPerSec/freqs[freq_counter]); // Conduct sim for 30 cycles
   if(!exitFlag)
   {
     output_data_filename = data_folder + "_freq" + str(freqs[freq_counter]) + "_ampl" + str(amplitudes[amp_counter]) + "_x_sepr" + x_separations[x_separations_counter] +"_y_sepr" + y_separations[y_separations_counter] +  "_inpt" + str(in_counter) + extention;
     output_data = createWriter(data_folder + "_freq" + str(freqs[freq_counter]) + "_ampl" + str(amplitudes[amp_counter]) + "_x_sepr" + x_separations[x_separations_counter] +"_y_sepr" + y_separations[y_separations_counter] +  "_inpt" + str(in_counter) + extention);
     
   }
}
