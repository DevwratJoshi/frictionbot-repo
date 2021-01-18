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
box_bottom = module_length*15
mean_box_pos = 10.0*1000/11.0
steps_per_second = 100.0 # the time step of the simulation]
vibration_cycles = 30 # Number of times the box is shaken
data_folder = "/home/dev/frictionbot-repo/simulations/Seed_method_distance_from_mean/data/corrected_mass/equal_friction/box_width_15/"
def show_usage():
  print("Usage: plotPosChange.py {F/A/S (Parameter on X axis) } {F/A/S (Parameter on y axis)} {Value of constant parameter}")
class MidpointNormalize(colors.Normalize):
    """Normalise the colorbar."""
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

if len(sys.argv) < 4:
    show_usage()
    sys.exit()

seperation_list = ['2', '3','4', '5', '6', '7'] #The length of the flashlight in mid module lengths
frequency_list = [str(round(i, 1)) for i in np.linspace(0.2, 0.9, 8)]
amplitude_list = [str(int(i)) for i in np.linspace(module_length/2, (module_length/2)*10, 10)]
list1 = []
list2 = []
input_list = [str(i) for i in range(1, 11)] # The input file numbers

xPosInit = np.zeros((101,)) # First element is initial element. Followed by last 100 element
fig,(ax1, ax2) = plt.subplots(1,2, figsize=(18,10))
flashSize = 'mid' # The diameter of the flashlight

if sys.argv[1] == sys.argv[2]:
  print("The parameter on the X and Y axes must be different. Exiting")
  show_usage()
  sys.exit()

if 'F' in sys.argv[1]:
  list1 = frequency_list

elif 'F' in sys.argv[2]:
  list2 = frequency_list

else:
  frequency = sys.argv[3]

if 'A' in sys.argv[1]:
  list1 = amplitude_list

elif 'A' in sys.argv[2]:
  list2 = amplitude_list
else:
  amplitude = sys.argv[3]

if 'S' in sys.argv[1]:
  list1 = seperation_list

elif 'S' in sys.argv[2]:
  list2 = seperation_list

else:
  seperation = sys.argv[3]


#Assuming 2 segregators for now 
if 'F' in sys.argv and 'A' in sys.argv:
    list1 = frequency_list
    list2 = amplitude_list
    segregator_touch_prob = np.zeros((len(list1), len(list2))) # The array with column 1 storing mean and column 2 storing std.dev of change in x coordinate
    wall_touch_prob = np.zeros((len(list1), len(list2)))
    sims_done_grid = np.zeros((len(list1), len(list2)))
    seperation = sys.argv[3]
    if not seperation in seperation_list:
        print("This seperation is unavailable")
        sys.exit()
    
    typ = type("Failed") # the file has this written if the sim has failed
    for i in range(len(list2)):
        for j in range(len(list1)):
            wall_touch_count = 0
            segregators_touch_count = 0. # Add one if the segregators touch in a simulation
            seg_touch_time_steps = []
            sims_done = 0
            for d in input_list:
                
                url = data_folder + "_freq" + list1[j] + "_ampl" + list2[i] + "_sepr" + seperation + "_inpt" + d + ".txt"
                try:
                  data = pd.read_csv(url, header=None, index_col=False)
                except:
                  print(url)
                  continue
                data_points = data.values.shape[0]
                pos = data.values # the positions of the segregators. Assuming 2 segregators for now.
                # Flag to check if segregators have touched already. No need to check for other data points then
                seg_touch_flag = False 
                # Flag to check if segregators have touched the wall already. No need to check for other data points then
                wall_touch_flag = False
                if typ ==  type(data.values[0][0]): # the same type as a string
                  pass
                else:
                  sims_done += 1
                  for k in range(data_points):
                    if not seg_touch_flag:
                      distance_betn_segregators = math.sqrt((pos[k][0] - pos[k][2])**2 + (pos[k][1] - pos[k][3])**2)
                      if distance_betn_segregators <= module_length:
                        segregators_touch_count += 1.0
                        seg_touch_flag = True
                        seg_touch_time_steps.append(k)

                    if not wall_touch_flag:
                      seg1_from_center = abs(pos[k][0] - pos[k][4]) # only x coordinate required
                      seg2_from_center = abs(pos[k][2] - pos[k][4]) # only x coordinate required
                      if(seg1_from_center > (box_bottom/2 - module_length - 5) or seg2_from_center > (box_bottom/2 - module_length - 5)):
                        wall_touch_count += 1
                        wall_touch_flag = True
                    if wall_touch_flag and seg_touch_flag:
                      break
            if not sims_done == 0:
              segregators_touch_count = segregators_touch_count/sims_done
              segregator_touch_prob[j][i] = segregators_touch_count
              wall_touch_count = wall_touch_count/sims_done
              wall_touch_prob[j][i] = wall_touch_count
              if not len(seg_touch_time_steps) == 0:
                total_time_steps = vibration_cycles * steps_per_second/float(list1[j]) #this is from the simulation program
                avg_touch_time = sum(seg_touch_time_steps)/len(seg_touch_time_steps)
                avg_touch_time_cycles = avg_touch_time/(total_time_steps-10)
                sims_done_grid[j][i] = avg_touch_time_cycles


            else:
                segregator_touch_prob[j][i] = np.nan
                wall_touch_prob[j][i] = np.nan
  
            #sims_done_grid[j][i] = sims_done
    

    plt.rcParams.update({'font.size':20})
    ax1.set_xlabel("Frequency of vibration", fontsize=18)
    ax1.set_ylabel("Amplitude of vibration", fontsize=18)
    ax1.set_xticklabels([str(i) for i in list1])
    ax1.set_yticklabels([str(i) for i in list2])

    ax2.set_xlabel("Frequency of vibration", fontsize=18)
    ax2.set_ylabel("Amplitude of vibration", fontsize=18)
    ax2.set_xticklabels([str(i) for i in list1])
    ax2.set_yticklabels([str(i) for i in list2])


    levels = MaxNLocator(nbins=10).tick_values(0, 1)

#list2 = [str(round(i/module_length, 1) for i in list2)]

plt.rcParams.update({'font.size':15})
cmap = plt.get_cmap('RdBu')
cmap.set_bad('gray',1.)
im = ax1.pcolormesh(list1 + ['0'], list2 + ['0'], np.transpose(segregator_touch_prob), cmap=cmap, norm=MidpointNormalize(0.0, 1.0, 0.5))
cb1 = fig.colorbar(im, ax=ax1)
cb1.set_ticks(np.arange(0.0, 1.1, 0.1))
ax1.set_title("Probability of segregators touching")

im = ax2.pcolormesh(list1 + ['0'], list2 + ['0'], np.transpose(wall_touch_prob), cmap=cmap, norm=MidpointNormalize(0.0, 1.0, 0.5))
cb2 = fig.colorbar(im, ax=ax2)
cb2.set_ticks(np.arange(0.0, 1.1, 0.1))
ax2.set_title("Probability of either segregator touching the wall")


cb1.ax.tick_params(labelsize=16)
cb2.ax.tick_params(labelsize=16)
#ax1.quiver(x,y,trueX_norm, trueY_norm, pivot='mid')

#ax1.set_title("freq {} amp {} up {} down {}".format(freq, amp, up, down))
ax1.set_xticks(0.5 +  np.arange(len(list1)))
ax1.set_yticks(0.5 + np.arange(len(list2)))
ax1.tick_params(labelsize=18)

ax2.set_xticks(0.5 +  np.arange(len(list1)))
ax2.set_yticks(0.5 + np.arange(len(list2)))
ax2.tick_params(labelsize=18)
#xu = float(up) *(20.0/(10.0))
#yu = 20
#xd = float(down)*(20.0/10.0)
#yd = 0
sims_done_grid = np.transpose(sims_done_grid)
for y in range(len(list2)):
    for x in range(len(list1)):
        ax1.text(x+0.5, y+0.5, round(sims_done_grid[y][x], 2), ha="center", va="center", color=(0,0,0), fontsize=12)

plt.show()
