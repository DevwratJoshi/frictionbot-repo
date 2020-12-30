#### Overview
This folder contains scripts to process the data in ../data directory  

Details of the scripts and how to run them should be added here.   

1. plot_param_sweep_touch_probability.py  
   * Final result : A heatmap of the probability of the segregators coming within one module length of each other over the course of the simulation. The probability of the segregators touching over the all the initial configurations is calculated. (N=10 for now)      
   * Possible parameters = initial seperation, frequency, amplitude. Ask for user input to choose which to plot. (Hard coded to plot frequency vs amplitude for now)
   * Currently, the plot defaults tofrequancy on the x axis, amplitude on the y axis. Seperate graph drawn for each seperation.
   * Usage: python plot_param_sweep_touch_probability.py F A Seperation_distance