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
data_folder = "/home/dev/frictionbot-repo/simulations/Seed_method_distance_from_mean/data/box_width_14/"
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
frequency_list = [str(round(i, 1)) for i in np.linspace(0.3, 0.9, 7)]
amplitude_list = [str(int(i)) for i in np.linspace(3*module_length/2, (module_length/2)*10, 8)]
list1 = []
list2 = []
input_list = [str(i) for i in range(1, 11)] # The input file numbers

xPosInit = np.zeros((101,)) # First element is initial element. Followed by last 100 element
fig,ax = plt.subplots(1,1, figsize=(10,10))
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
    xData = np.zeros((len(list1), len(list2))) # The array with column 1 storing mean and column 2 storing std.dev of change in x coordinate
    seperation = sys.argv[3]
    if not seperation in seperation_list:
        print("This seperation is unavailable")
        sys.exit()
    
    for i in range(len(list2)):
        for j in range(len(list1)):
            segregators_touch_count = 0. # Add one if the segregators touch in a simulation
            for d in input_list:
                url = data_folder + "_freq" + list1[j] + "_ampl" + list2[i] + "_sepr" + seperation + "_inpt" + d + ".txt"
                data = pd.read_csv(url, header=None, index_col=False)
                data_points = data.values.shape[0]
                pos = data.values[:, :4] # the positions of the segregators. Assuming 2 segregators for now.
                for k in range(data_points):
                  distance_betn_segregators = math.sqrt((pos[k][0] - pos[k][2])**2 + (pos[k][1] - pos[k][3])**2)
                  if distance_betn_segregators <= module_length + 2:
                    segregators_touch_count += 1.0
                    break
                
            segregators_touch_count = segregators_touch_count/float(len(input_list))
            xData[j][i] = segregators_touch_count
               
    

    plt.rcParams.update({'font.size':20})
    ax.set_xlabel("Frequency of vibration", fontsize='large')
    ax.set_ylabel("Amplitude of vibration", fontsize='large')
    ax.set_xticklabels([str(i) for i in list1])
    ax.set_yticklabels([str(i) for i in list2])


    levels = MaxNLocator(nbins=10).tick_values(0, 1)



cmap = plt.get_cmap('RdBu')

im = ax.pcolormesh(list1 + ['0'], list2 + ['0'], np.transpose(xData), cmap=cmap, norm=MidpointNormalize(0.0, 1.0, 0.5))
cb = fig.colorbar(im, ax=ax)
cb.set_ticks(np.arange(0.0, 1.1, 0.1))
ax.set_title("Migration along X axis")



cb.ax.tick_params(labelsize=16)
#ax.quiver(x,y,trueX_norm, trueY_norm, pivot='mid')

#ax.set_title("freq {} amp {} up {} down {}".format(freq, amp, up, down))
ax.set_xticks(0.5 +  np.arange(len(list1)))
ax.set_yticks(0.5 + np.arange(len(list2)))
ax.tick_params(labelsize=18)
#xu = float(up) *(20.0/(10.0))
#yu = 20
#xd = float(down)*(20.0/10.0)
#yd = 0


plt.show()
