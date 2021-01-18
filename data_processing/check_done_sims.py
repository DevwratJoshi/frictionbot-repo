import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate
import math
import matplotlib.colors as colors
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import sys
import os

module_length = 20*2

box_bottom = module_length*15
mean_box_pos = 10.0*1000/11.0
data_folder = "/home/dev/frictionbot-repo/simulations/Anisotropic_no_seed_sweep/data/"
def show_usage():
  print("Usage: plotPosChange.py {Value of seperation}")
class MidpointNormalize(colors.Normalize):
    """Normalise the colorbar."""
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

if len(sys.argv) < 2:
    show_usage()
    sys.exit()

seperation_list = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20'] #The length of the flashlight in mid module lengths
frequency_list = [str(round(i, 1)) for i in np.linspace(0.2, 0.9, 8)]
amplitude_list = [str(int(i)) for i in np.linspace(module_length/2, (module_length/2)*10, 10)]
list1 = []
list2 = []
input_list = [str(i) for i in range(1, 6)] # The input file numbers

xPosInit = np.zeros((101,)) # First element is initial element. Followed by last 100 element
fig,ax1 = plt.subplots(1, 1, figsize=(18,10))
flashSize = 'mid' # The diameter of the flashlight


list1 = amplitude_list
list2 = frequency_list
sims_done = np.zeros((len(list1), len(list2))) # The array with column 1 storing mean and column 2 storing std.dev of change in x coordinate

seperation = sys.argv[1]
if not seperation in seperation_list:
    print("This seperation is unavailable")
    sys.exit()

for i in range(len(list2)):
    for j in range(len(list1)):
        file_count = 0. # Add one if the segregators touch in a simulation
        
        for d in input_list:
            url = data_folder + "_freq" + list2[i] + "_ampl" + list1[j] + "_x_sepr" + seperation + "_y_sepr0_inpt" + d + ".txt"
            if os.path.exists(url):
                file_count += 1
          
        file_count = file_count/float(len(input_list))
        sims_done[j][i] = file_count




plt.rcParams.update({'font.size':20})
ax1.set_xlabel("Amplitude", fontsize=18)
ax1.set_ylabel("Frequency", fontsize=18)
ax1.set_xticklabels([str(i) for i in list1])
ax1.set_yticklabels([str(i) for i in list2])



levels = MaxNLocator(nbins=10).tick_values(0, 1)



plt.rcParams.update({'font.size':15})
cmap = plt.get_cmap('RdBu')

im = ax1.pcolormesh(list1 + ['0'], list2 + ['0'], np.transpose(sims_done), cmap=cmap, norm=MidpointNormalize(0.0, 1.0, 0.5))
cb1 = fig.colorbar(im, ax=ax1)
cb1.set_ticks(np.arange(0.0, 1.1, 0.1))
ax1.set_title("Sims done")



cb1.ax.tick_params(labelsize=16)

#ax1.quiver(x,y,trueX_norm, trueY_norm, pivot='mid')

#ax1.set_title("freq {} amp {} up {} down {}".format(freq, amp, up, down))
ax1.set_xticks(0.5 +  np.arange(len(list1)))
ax1.set_yticks(0.5 + np.arange(len(list2)))
ax1.tick_params(labelsize=18)

#xu = float(up) *(20.0/(10.0))
#yu = 20
#xd = float(down)*(20.0/10.0)
#yd = 0


plt.show()
