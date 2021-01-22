## IMPORTANT: There is an error in the format of the data files for these sims. 
# The format is supposed to be:
# One row denoting the intial position of the box (box_x position, box_y_position)
# 80 rows (number of robots) with inital robot positions as (robot_x, robot_y, robot_type) type = 's' for high friction and 'm' for low friction 
# One row with final box position
# 80 rows (number of robots) with final robot positions as (robot_x, robot_y, robot_type)
# However, forgot to add the robot types in the final robot positions
# But the order of the types should be the same, as the robots objects are arranged as an array in the sim
# To correct this, the list of robot types is used in the same order for the intial and final positions in the file

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate
import math
import matplotlib.colors as colors
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import sys
import copy
import random
module_length = 20*2
big_module_length = 20*2*1.73
box_bottom = module_length*15
box_wall_width = 40 #Width of the sides of the wall
mean_box_pos = 10.0*1000/11.0
box_height = 8*module_length
number_of_robots = 80
def show_usage():
  print("Usage : plot_positions.py <file name>")

 
data_folder = "/home/dev/frictionbot-repo/simulations/Banding_simulation/data/corrected_mass/actual_friction/box_width_15/"
typ = type("Failed")
if len(sys.argv) < 2:
  show_usage()
  sys.exit()

url = data_folder + sys.argv[1]

try:
  data = pd.read_csv(url, header=None, names=["X", "Y", "Type"])
except:
  print(url)
  sys.exit()

data_points = data.values.shape[0]
init_pos = data.values[1:81, :2] # the positions of the segregators. Assuming 2 segregators for now.
final_pos = data.values[82:, :2] 
types_list = data.values[1:81, 2]
init_box_pos = data.values[0, :2]
final_box_pos = data.values[81, :2]



sims_done = 0
if typ ==  type(data.values[0][0]): # the same type as a string
  print("This sim failed")
  sys.exit()

fig,(ax1, ax2) = plt.subplots(1,2, figsize=(15,8))

# ax1.set_xlim(0, 1+box_bottom/module_length)
# ax2.set_xlim(0, 1+box_bottom/module_length)
# ax1.set_ylim(0, 1+box_height/module_length)
# ax2.set_ylim(0, 1+box_height/module_length)

init_box_origin_x = init_box_pos[0] - box_bottom/2
init_box_origin_y = init_box_pos[1] - box_wall_width/2
x1_vals = init_pos[:,0] - init_box_origin_x
x1_vals = x1_vals/module_length
y1_vals = init_box_origin_y - init_pos[:, 1] 
y1_vals = y1_vals/module_length

final_box_origin_x = final_box_pos[0] - box_bottom/2
final_box_origin_y = final_box_pos[1] - box_wall_width/2
x2_vals = final_pos[:,0] - final_box_origin_x
x2_vals = x2_vals/module_length
y2_vals = final_box_origin_y - final_pos[:, 1] 
y2_vals = y2_vals/module_length

init_low_fric   = np.zeros((int(len(types_list)/2), 2))
init_high_fric  = np.zeros((int(len(types_list)/2), 2))
final_low_fric  = np.zeros((int(len(types_list)/2), 2))
final_high_fric = np.zeros((int(len(types_list)/2), 2))

high_fric_count = 0
low_fric_count = 0

for i in range(len(types_list)):
  if(types_list[i] == 's'): #This means the robot is high friction => red dot
    init_high_fric[high_fric_count][0]  = x1_vals[i]
    init_high_fric[high_fric_count][1]  = y1_vals[i]
    final_high_fric[high_fric_count][0] = x2_vals[i]
    final_high_fric[high_fric_count][1] = y2_vals[i]
    high_fric_count += 1
  elif types_list[i] == 'm':
    init_low_fric[low_fric_count][0]  = x1_vals[i]
    init_low_fric[low_fric_count][1]  = y1_vals[i]
    final_low_fric[low_fric_count][0] = x2_vals[i]
    final_low_fric[low_fric_count][1] = y2_vals[i]
    low_fric_count += 1


# Find the ideal number of clusters with the distortion jump method
# Algorithm => 
# 0) Decide the max number of centers to calculate for
# 1) Get the locations of the centers using k means 
# 2) Get the distortions associated with those centers
# 3) Select a transformation power Y (Paper ways typical power is p/2, so choosing 1, as there are two components)
# 4) Get argmax k ((distortion)_k)^-Y - ((distortion)_k-1)^-Y. Set (d_0)^-Y = 0
no_of_centers_list = list(np.arange(1, 20, 1)) # list of number of centers to get distortions for
distortions = np.zeros(len(no_of_centers_list))

source_array = copy.deepcopy(final_high_fric)
positions = copy.deepcopy(source_array)

k = 20 #Try for 3 centers
centers = np.zeros((k, 2))
#Get a k number of centers by choosing k positions randomly from the module positions list
for i in range(k):
  ind = random.randint(0, positions.shape[0]-1)
  centers[i] = copy.deepcopy((positions[ind]))
  positions = np.delete(positions, ind, 0)
# Got the appropriate number of centers 

print(centers)
ax2.scatter(centers[:,0], centers[:,1], color='orange', s=100)
#Use the centers as starting position for the k means algorithm
count = 0
last_distortion = 10000000 # The last distortion
# An list to hold the grouped positions.
# This will make it easier to plot which groups the modules have been put into by k means
 
# Perform k means for a maximum of this many times
while count < 1000:  
  grouped_positions = []
  for i in range(k):
    grouped_positions.append([])
  new_centers = np.zeros((k, 2))
  cluster_counts = np.zeros(k) #The number of points in a particular group. Used later calculate the new center position. To calculate average
  distortion = 0 #Keep track of the total distortion 
  for i in range(source_array.shape[0]): # For all the points under consideration
    min_dist = np.linalg.norm(centers[0] - source_array[i])
    cluster_id = 0 # the id of the cluster this point belongs to 
    for j in range(1, k): # for all the center points, find the one closest to this point
      dist_to_center = np.linalg.norm(centers[j] - source_array[i])
      if dist_to_center < min_dist:
        min_dist = dist_to_center
        cluster_id = j
    # Add the point's coordinates to the correct cluster. Will be used to get the new center
    new_centers[cluster_id] += source_array[i] # Component-wise addition into the appropriate box
    # Save the new position in the grouped position array
    grouped_positions[cluster_id].append(source_array[i])
    cluster_counts[cluster_id]+= 1
    
  
  for i in range(k): # divide the
    centers[i, 0] = new_centers[i, 0]/cluster_counts[i] # These are the new centers
    centers[i, 1] = new_centers[i,1]/cluster_counts[i] # These are the new centers
  
  for i in range(len(grouped_positions)): # For all the points under consideration    
    for pos in grouped_positions[i]:
      distortion += np.linalg.norm(pos - centers[i]) #The distance to its currently assigned center


  # Not bothering to calculate the distortion again here. Do not think it matters that much
  if(last_distortion - distortion < 0):
    print("The distortion has increased in a loop. There might be something wrong \n")
    

  if(last_distortion - distortion < 0.01): # this is arbitrary
    print("Distortion limit reached in " + str(count) + " steps")
    
    break

  print("Last distortion = " + str(last_distortion) + "\nCurrent distortion = " + str(distortion) + "\n")
  last_distortion = distortion
  
  count += 1

print("Distortion = " + str(distortion) + "\n")
#Have the k means centers now
ax1.set_title("Initial positions")
ax2.set_title("Final positions")
ax1.set_aspect(1)
ax2.set_aspect(1)

fig.canvas.draw()
s = ((ax1.get_window_extent().width  / (15+1.) * 72./fig.dpi) ** 2)

ax1.scatter(init_low_fric[:, 0], init_low_fric[:, 1], color='green', s = s)
ax1.scatter(init_high_fric[:, 0], init_high_fric[:, 1], color='red', s = s)
ax2.scatter(final_high_fric[:, 0], final_high_fric[:, 1], color='red', s = s)
ax2.scatter(final_low_fric[:, 0], final_low_fric[:, 1], color='green', s = s)
cols = [(1-i/k, 0, i/k) for i in range(k)]
for i in range(len(grouped_positions)):
  ax2.scatter(np.array(grouped_positions[i])[:,0], np.array(grouped_positions[i])[:,1], color=cols[i], s=20)
  ax2.scatter(centers[i,0], centers[i,1], color=cols[i], s=50)
plt.show()
