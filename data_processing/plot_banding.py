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
types_list = types_list = data.values[1:81, 2]
init_box_pos = data.values[0, :2]
final_box_pos = data.values[81, :2]


sims_done = 0
if typ ==  type(data.values[0][0]): # the same type as a string
  print("This sim failed")
  sys.exit()

fig,(ax1, ax2) = plt.subplots(1,2, figsize=(15,8))

ax1.set_xlim(0, 1+box_bottom/module_length)
ax2.set_xlim(0, 1+box_bottom/module_length)
ax1.set_ylim(0, 1+box_height/module_length)
ax2.set_ylim(0, 1+box_height/module_length)


x1_vals = init_pos[:,0] - init_box_pos[0] 
x1_vals = box_bottom/2 + x1_vals
x1_vals = x1_vals/module_length
y1_vals = init_box_pos[1] - init_pos[:, 1] 
y1_vals = y1_vals - box_wall_width/2
y1_vals = y1_vals/module_length

x2_vals = final_pos[:,0] - final_box_pos[0] 
x2_vals = box_bottom/2 + x2_vals
x2_vals = x2_vals/module_length
y2_vals = final_box_pos[1] - final_pos[:, 1] 
y2_vals = y2_vals - box_wall_width/2
y2_vals = y2_vals/module_length

init_low_fric = np.zeros((len(types_list), 2))
init_high_fric = np.zeros((len(types_list), 2))
final_low_fric = np.zeros((len(types_list), 2))
final_high_fric = np.zeros((len(types_list), 2))

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
print(low_fric_count, high_fric_count)




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
plt.show()
