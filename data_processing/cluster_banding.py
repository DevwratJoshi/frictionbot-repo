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
from scipy.ndimage.filters import uniform_filter1d
from scipy.ndimage import median_filter
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
cluster_distance = 1.5 #Modules determined to be in the same cluster if they are at most this much apart (in module-lengths)
def show_usage():
  print("Usage : plot_positions.py <file name>")
 
def scan_robot_neighbourhood(module_coordinates, source_list, group):
  '''
  Self-calling function to remove robots near 'module_coordinates' from 'source_list' and move them to'group'  
  '''
  modules_found = False # A variable that turns false if no modules in the list are found near 'module_coordinates'
  while True:
    for i in range(len(source_list)):
      dist = np.linalg.norm(source_list[i] - module_coordinates)
      if dist < cluster_distance: #
        modules_found = True # This means the while loop shold be run again after this loop
        group.append(copy.deepcopy(source_list[i]))
        source_list.pop(i) # removes the element in place
        print("Length of source list in function = " + str(len(source_list)))
        scan_robot_neighbourhood(group[-1], source_list, group)
        # Breaking here because the function called in the previous line might change the length of the source list
        # This will let us reload the for loop with the appropriate length of the source list
        break 
    if not modules_found:
      return 
    modules_found = False

data_folder = "/home/dev/frictionbot-repo/simulations/Banding_simulation/data/corrected_mass/ideal_friction/box_width_15/"
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

fig,((ax1, ax2)) = plt.subplots(1,2, figsize=(15,8))

ax1.set_xlim(0, 1+box_bottom/module_length)
ax2.set_xlim(0, 1+box_bottom/module_length)
ax1.set_ylim(0, 1+box_height/module_length)
ax2.set_ylim(0, 1+box_height/module_length)

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

# Group the modules together with simple clustering algorithm
robot_clusters = [] #This sould be a list of lists of numpy arrays holding the coordinates of all the robots in the cluster
# This should be changed later to be able to cluster the robots before and after shaking
# Using as a list to allow removing elements inside the function (Cannot be done for numpy arrays)
source_list = list(copy.deepcopy(final_high_fric)) 
while len(source_list) > 0:
  robot_clusters.append([])
  robot_clusters[-1].append(source_list[0])
  #Remove the element from the source list so it does not add itself in the function
  source_list.pop(0)
  scan_robot_neighbourhood(robot_clusters[-1][0], source_list, robot_clusters[-1])
  print("Length of source list outside function = " + str(len(source_list)))
  print(len(robot_clusters))
  print("\n")
  
print(len(robot_clusters))


ax1.set_title("Initial positions")
ax2.set_title("Final positions")
ax1.set_aspect(1)
ax2.set_aspect(1)

fig.canvas.draw()
s = ((ax1.get_window_extent().width  / (15+1.) * 72./fig.dpi) ** 2)

ax1.scatter(final_low_fric[:, 0], final_low_fric[:, 1], color='green', s = s)
ax1.scatter(final_high_fric[:, 0], final_high_fric[:, 1], color='red', s = s)

#ax2.scatter(final_high_fric[:, 0], final_high_fric[:, 1], color='red', s = s)
#ax2.scatter(final_low_fric[:, 0], final_low_fric[:, 1], color='green', s = s)
cols = [(1-i/len(robot_clusters), 0, i/len(robot_clusters)) for i in range(len(robot_clusters))]
for i in range(len(robot_clusters)):
  ax2.scatter(np.array(robot_clusters[i])[:,0], np.array(robot_clusters[i])[:,1], color=cols[i], s=s)
  for pos in robot_clusters[i]:
    ax1.text(pos[0], pos[1], i, ha="center", va="center", color=(1,1,1), fontsize=12)
    ax2.text(pos[0], pos[1], i, ha="center", va="center", color=(1,1,1), fontsize=12)

plt.show()
