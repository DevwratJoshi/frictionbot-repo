## IMPORTANT: There is an error in the format of the data files for these sims. 
# The format is supposed to be:
# One row denoting the intial position of the box (box_x position, box_y_position)
# 80 rows (number of robots) with inital robot positions as (robot_x, robot_y, robot_type) type = 's' for high friction and 'm' for low friction 
# One row with final box position
# 80 rows (number of robots) with final robot positions as (robot_x, robot_y, robot_type)
# However, forgot to add the robot types in the final robot positions
# But the order of the types should be the same, as the robots objects are arranged as an array in the sim
# To correct this, the list of robot types is used in the same order for the intial and final positions in the file

# Sweep through all the frequencies and amplitudes and find the average reduction in clusters for different frequencies and amplitudes
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

class MidpointNormalize(colors.Normalize):
    """Normalise the colorbar."""
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

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
        
        scan_robot_neighbourhood(group[-1], source_list, group)
        # Breaking here because the function called in the previous line might change the length of the source list
        # This will let us reload the for loop with the appropriate length of the source list
        break 
    if not modules_found:
      return 
    modules_found = False

data_folder = "/home/dev/frictionbot-repo/simulations/Banding_simulation/data/corrected_mass/ideal_friction/box_width_15/"
typ = type("Failed")


frequency_list = [str(round(i, 1)) for i in np.linspace(0.2, 0.9, 8)]
amplitude_list = [str(int(i)) for i in np.linspace(module_length/2, (module_length/2)*10, 10)]
list2 = amplitude_list
list1 = frequency_list
input_list = [str(i) for i in range(1, 11)] # The input file numbers
initial_clusters = np.zeros(len(input_list))
cluster_reduction_grid = np.zeros((len(list1), len(list2)))
cluster_grid = np.zeros((len(list1), len(list2)))


fig,ax1 = plt.subplots(figsize=(18,10))
for i in range(len(list2)):
  for j in range(len(list1)):
    no_of_clusters = 0
    sims_done = 0
    for input_index in range(len(input_list)):
      url = data_folder + "_freq" + list1[j] + "_ampl" + list2[i] +  "_inpt" + input_list[input_index] + ".txt"
      try:
        data = pd.read_csv(url, header=None, names=["X", "Y", "Type"])
      except:
        print(url)
        sys.exit()

      if typ ==  type(data.values[0][0]): # the same type as a string
        continue
      else:
        sims_done += 1

      data_points = data.values.shape[0]
      init_pos = data.values[1:81, :2] # the positions of the segregators. Assuming 2 segregators for now.
      final_pos = data.values[82:, :2] 
      types_list = data.values[1:81, 2]
      init_box_pos = data.values[0, :2]
      final_box_pos = data.values[81, :2]


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

      for k in range(len(types_list)):
        if(types_list[k] == 's'): #This means the robot is high friction => red dot
          init_high_fric[high_fric_count][0]  = x1_vals[k]
          init_high_fric[high_fric_count][1]  = y1_vals[k]
          final_high_fric[high_fric_count][0] = x2_vals[k]
          final_high_fric[high_fric_count][1] = y2_vals[k]
          high_fric_count += 1
        elif types_list[k] == 'm':
          init_low_fric[low_fric_count][0]  = x1_vals[k]
          init_low_fric[low_fric_count][1]  = y1_vals[k]
          final_low_fric[low_fric_count][0] = x2_vals[k]
          final_low_fric[low_fric_count][1] = y2_vals[k]
          low_fric_count += 1

      # Group the modules together with simple clustering algorithm
      robot_clusters = [] #This sould be a list of lists of numpy arrays holding the coordinates of all the robots in the cluster
      # This should be changed later to be able to cluster the robots before and after shaking
      # Using as a list to allow removing elements inside the function (Cannot be done for numpy arrays)
      # Get the initial number of clusters 
      if initial_clusters[input_index] == 0.:
        # in this case, find number of clusters for initial positions
        source_list = list(copy.deepcopy(init_high_fric))
        while len(source_list) > 0:
          robot_clusters.append([])
          robot_clusters[-1].append(source_list[0])
          #Remove the element from the source list so it does not add itself in the function
          source_list.pop(0)
          scan_robot_neighbourhood(robot_clusters[-1][0], source_list, robot_clusters[-1])
        initial_clusters[input_index] = len(robot_clusters)

      robot_clusters = [] #This sould be a list of lists of numpy arrays holding the coordinates of all the robots in the cluster 
      source_list = list(copy.deepcopy(final_high_fric)) 
      while len(source_list) > 0:
        robot_clusters.append([])
        robot_clusters[-1].append(source_list[0])
        #Remove the element from the source list so it does not add itself in the function
        source_list.pop(0)
        scan_robot_neighbourhood(robot_clusters[-1][0], source_list, robot_clusters[-1])


      cluster_grid[j][i] += len(robot_clusters)
      cluster_reduction_grid[j][i] += initial_clusters[input_index] - len(robot_clusters)

    if not sims_done == 0:
      cluster_grid[j][i] /= sims_done
      cluster_reduction_grid[j][i] /= sims_done

    else:
      cluster_grid[j][i] = np.nan
      cluster_reduction_grid[j][i] = np.nan

plt.rcParams.update({'font.size':20})
ax1.set_xlabel("Frequency of vibration", fontsize=18)
ax1.set_ylabel("Amplitude of vibration", fontsize=18)
ax1.set_xticklabels([str(i) for i in list1])
ax1.set_yticklabels([str(i) for i in list2])
levels = MaxNLocator(nbins=10).tick_values(0, 1)

plt.rcParams.update({'font.size':15})
cmap = plt.get_cmap('RdBu_r')
cmap.set_bad('gray',1.)
im = ax1.pcolormesh(list1 + ['0'], list2 + ['0'], np.transpose(cluster_grid), cmap=cmap, norm=MidpointNormalize(0.0, 10, 5))
cb1 = fig.colorbar(im, ax=ax1)
cb1.set_ticks(np.arange(0.0, 11, 1))
ax1.set_title("Clustering")

cb1.ax.tick_params(labelsize=16)
ax1.set_xticks(0.5 +  np.arange(len(list1)))
ax1.set_yticks(0.5 + np.arange(len(list2)))
ax1.tick_params(labelsize=18)

cluster_reduction_grid = np.transpose(cluster_reduction_grid)
for y in range(len(list2)):
    for x in range(len(list1)):
        ax1.text(x+0.5, y+0.5, round(cluster_reduction_grid[y][x], 2), ha="center", va="center", color=(0,0,0), fontsize=12)

plt.show()
