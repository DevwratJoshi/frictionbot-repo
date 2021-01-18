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
def show_usage():
  print("Usage : plot_positions.py <file name>")
  
data_folder = "/home/dev/frictionbot-repo/simulations/Seed_method_distance_from_mean/data/corrected_mass/actual_friction/box_width_15/"
typ = type("Failed")
if len(sys.argv) < 2:
  show_usage()
  sys.exit()

url = data_folder + sys.argv[1]

try:
  data = pd.read_csv(url, header=None, index_col=False)
except:
  print(url)
  sys.exit()

data_points = data.values.shape[0]
pos = data.values # the positions of the segregators. Assuming 2 segregators for now.
# Flag to check if segregators have touched already. No need to check for other data points then
seg_touch_flag = False 
# Flag to check if segregators have touched the wall already. No need to check for other data points then
wall_touch_flag = False
sims_done = 0
if typ ==  type(data.values[0][0]): # the same type as a string
  print("This sim failed")
  sys.exit()

fig,(ax1, ax2) = plt.subplots(1,2, figsize=(10,6))

ax1.set_xlim(0, 1+box_bottom/module_length)
ax1.set_ylim(0, 1+box_height/module_length)
ax2.set_ylim(0, math.sqrt(box_bottom**2 + box_height**2)/module_length)

x1_vals = pos[:,0] - pos[:,4] 
x1_vals = box_bottom/2 + x1_vals
x1_vals = x1_vals/module_length
y1_vals = pos[:, 5] - pos[:,1]
y1_vals = y1_vals - box_wall_width/2
y1_vals = y1_vals/module_length
ax1.plot(x1_vals, y1_vals, color='red')

x2_vals = pos[:,2] - pos[:,4] 
x2_vals = box_bottom/2 + x2_vals
x2_vals = x2_vals/module_length
y2_vals = pos[:, 5] - pos[:,3]
y2_vals = y2_vals - box_wall_width/2
y2_vals = y2_vals/module_length
ax1.plot(x2_vals, y2_vals, color='blue')

rel_x = x2_vals - x1_vals
rel_y = y2_vals - y1_vals
dists = np.sqrt(rel_x**2 + rel_y**2)

ax2.plot(dists, color='green')
ax2.plot(np.abs(rel_x), color='orange')
plt.show()
