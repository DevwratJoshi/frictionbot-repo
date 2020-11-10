### Project description  
This project attempts to apply granular segregation phenomena to swarm robot segregation. In particular, banding phenomena seen in horizontally shaken beds with particles with varying friction. 

#### Simulations:    
The robot simulations for this project can be found in [this repository](https://github.com/DevwratJoshi/VolBotSims). 

#### Experiments:  
The horizontal bed simulations are recreated with a physical experiment setup. The horizontal bed is shaken using a linear actuator driven by a stepper motor.   

  1. Robot: Simple robots capable of changing their frictional coefficient with the underlying bed are proposed. The robots use a solenoid to bring a high-friction sheet of material into contact with the bed, increasing the contact friction between the robot and the swarm bed.   
  2. Experiment setup: The experiment setup involves creating a high-friction set of modules in a section of the bed. This section should ideally maintained by local communication between robots. Currently, a simple approach using aruco code reading software is proposed. Each robot is equipped with an aruco code (from the 4x4_100 library) and wireless communication. An overhead camera can determine the location of each module and the appropriate commands to send to the module can be determined accordingly. This is meant to take the place of local communication algorithms centering aroud hop-count and so on.   

#### This repository:  
This repository contains the code onboard each robot (micropyton), the code used to read the camera input and send the appropriate commands to each robot(python), and the code to control the shaking of the swarm bed (Arduino cpp).  