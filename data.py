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
import numpy as np
from urllib.request import urlopen
import json
from matplotlib import pyplot as plt
from scipy.stats import linregress
from helper_functions import moving_average

##############################################################################
# CUSTOMIZABLE VARIABLES
##############################################################################

# Which states to compare my state to
my_state = 'MN'
comparison_states = ['NY','NJ']

# Number of days over which to perform a moving average
N_avg = 5

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
raw_state_data  =   json.loads(urlopen(state_data_url).read())
raw_state_info  =   json.loads(urlopen(state_info_url).read())
raw_us_data     =   json.loads(urlopen(us_data_url).read())[::-1]

# Extract US data
us_positive            =   [entry['positive'] for entry in raw_us_data]
us_positiveIncrease    =   [entry['positiveIncrease'] for entry in raw_us_data]

# Transform nformation for each state into a dictionary
state_info      =   {entry['state']:entry for entry in raw_state_info}

# Transform the data so that it is organized by state
data_by_state   =   dict()
slopes_by_state =   dict()
for entry in raw_state_data:
    state = entry['state']
    try:
        data_by_state[state].append(entry)
    except KeyError:
        data_by_state[state] = [entry]

# Plot all of the states on one plot
fig, ax = plt.subplots()
for state in state_info.keys():
    data = data_by_state[state][::-1]
    positive = moving_average([entry['positive'] if entry['positive']
                               else 0
                               for entry in data], N_avg)
    positiveIncrease = moving_average([entry['positiveIncrease'] if entry['positiveIncrease'] 
                                       else 0 
                                       for entry in data], N_avg)
    ax.plot(positive, positiveIncrease, label=None)
    if positive[-1] > 0:
        slopes_by_state[state] = linregress(positive[-15:], positiveIncrease[-15:])[0]
    
ranked_states = sorted(slopes_by_state.items(), key=lambda x : x[1])

# Plot the y=mx line
m = 1
max_cases = np.max([entry['positive'] if entry['positive'] else 0 for entry in raw_state_data])
y_equals_x = np.linspace(0, max_cases, 50)
if m==1:
    yxlabel = 'y=x'
else:
    yxlabel = 'y={:.6g}x'.format(m)
ax.plot(y_equals_x, m*y_equals_x, 'k--', label=yxlabel)

# Plot the US data
ax.plot(us_positive, us_positiveIncrease, 'k--', lw=3.5, label="United States")

# Format the plot
ax.legend()
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlabel('Total number of positive cases')
ax.set_ylabel('Increase in positive cases')

# Create a plot for specific states
fig2, ax2 = plt.subplots()
# Make sure my_state comes first
try:
    comparison_states.remove(my_state)
except ValueError:
    pass
comparison_states = [my_state] + comparison_states
comparison_states.append(ranked_states[-2][0])
for state in comparison_states:
    try:
        state_name = state_info[state]['name']
    except KeyError:
        # This state doesn't exist
        print("Skipping state, {}, from 'my_states' because it isn't in the data set".format(state))
        continue
    data = data_by_state[state][::-1]
    positive = moving_average([entry['positive'] if entry['positive']
                               else 0
                               for entry in data], N_avg)
    positiveIncrease = moving_average([entry['positiveIncrease'] if entry['positiveIncrease'] 
                                       else 0 
                                       for entry in data], N_avg)
    if state == my_state:
        lw = 5
    else:
        lw = 2
    ax2.plot(positive, positiveIncrease, label=state, lw=lw)
    
        

# Plot the y=mx line
ax2.plot(y_equals_x, m*y_equals_x, 'k--', label=yxlabel)

# Plot the US data
# ax2.plot(us_positive, us_positiveIncrease, '--', lw=3.5, label="United States")

# Format the plot
ax2.legend()
ax2.set_yscale('log')
ax2.set_xscale('log')
ax2.set_xlabel('Total number of positive cases')
ax2.set_ylabel('Increase in positive cases')

# Show the plots
plt.show()