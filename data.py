# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 2020

@author: Jeff Peterson

This script automatically fetches the latest state data sets from the COVID
tracking project and then plots the change in cases versus the total number of
cases. If the plot is linear or has a constant slope, then this indicates
exponential growth. If the slope beocmes negative, that means that the number
of new cases per day is decreasing and that the exponential growth has been
haulted.
"""
from matplotlib import pyplot as plt
from helper_functions import data_by_state, plot_state_data

##############################################################################
# CUSTOMIZABLE VARIABLES
##############################################################################

# Which states to compare my state to
my_state = 'NM'
comparison_states = ['NY','WA', 'SD', 'MT']

# Number of days over which to perform a moving average
N_avg = 5

# Number of points at the end of the data over which to find the slope
N_slope = 15

##############################################################################
# CODE
##############################################################################

# Close all figures
plt.close('all')

# Initial loading of the data from the COVID Tracking Project
# https://covidtracking.com/

state_data_url  =   'https://covidtracking.com/api/v1/states/daily.json'
state_info_url  =   'https://covidtracking.com/api/v1/states/info.json'
us_data_url     =   'https://covidtracking.com/api/us/daily'

# Transform state data
state_data      =   data_by_state(state_data_url, us_data_url=us_data_url)
state_info      =   data_by_state(state_info_url)

# Plot all of the states on one plot
slopes_by_state = plot_state_data(state_data, state_info, N_avg, N_slope)
for state, slope in sorted(slopes_by_state.items(), key=lambda x: x[1]):
    print(state, slope)

# Combine my_state with comparison states and the overall US data
try:
    comparison_states.remove(my_state)
except ValueError:
    pass
comparison_states = ['US'] + [my_state] + comparison_states

# Plot a subset of state data
select_data = {state:data for state, data in state_data.items() if state in comparison_states}
plot_state_data(select_data, state_info, N_avg, N_slope, labels=True, my_state=my_state)

plt.show()