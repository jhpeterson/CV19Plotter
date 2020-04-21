# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 2020

@author: Jeff Peterson
"""
import numpy as np
from urllib.request import urlopen
from matplotlib import pyplot as plt
from matplotlib import colors, ticker
from scipy.stats import linregress
import json

def plot_state_data(data_dict, data_info, N_avg, N_slope, labels=False, 
                    my_state=None, title=None):
    '''
    Parameters
    ----------
    data_dict : dict
        Dictionary with the data by state
    data_info : dict
        Dictionary with the information for each state (like its name)
    N_avg : integer
        Number of points over which to do a moving average
    N_slope : integer
        Number of points over which to calculate a linear regression for the
        slope of the the last part of the data
    labels : boolean, optional
        Whether or not to label the lines in a legend
        (Default: False)
    my_state : str, optional
        The state that we want to compare against
        (Default: None)
    title : str, optional
        Title to put on the plot if specified
    

    Returns
    -------
    slopes_by_state: dict
        For each state, give the slope of a linear regression for the last

    '''
    fig, ax         =   plt.subplots()
    slopes_by_state =   dict()
    for state, data in data_dict.items():
        positive            =   moving_average(data['positive'], N_avg)
        positiveIncrease    =   moving_average(data['positiveIncrease'], N_avg)
        # Choose the line formats for the US and states
        # Defaults for plot (let the plotter decide and have no labels)
        linewidth   =   None
        linestyle   =   None
        color       =   None
        label       =   None
        # Plot the US and my_state differently
        if state == 'US':
            linewidth   =   3.5
            linestyle   =   '--'
            color       =   'k'
            label       =   'United States'
        elif state == my_state:
            linewidth   =   3.5
            label   =   data_info[state]['name']
        else:
            # Do we want labels for the states?
            if labels:
                label   =   data_info[state]['name']
        # Plot
        ax.plot(positive, positiveIncrease,
                linewidth=linewidth,
                linestyle=linestyle,
                color=color,
                label=label)
        # If there are positive cases here, find the slope of the last 15 days
        if positive[-1] > 0:
            slopes_by_state[state] = linregress(positive[-N_slope:], 
                                                positiveIncrease[-N_slope:]).slope

    # Plot the y=mx line
    max_cases = np.max([np.max(data_dict[state]['positive']) for state in data_dict.keys()])
    y_equals_x = np.linspace(0, max_cases, 50)
    yxlabel = 'y=x'
    ax.plot(y_equals_x, y_equals_x, 'k--', label=yxlabel)
    
    # Format the plot
    ax.legend()
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylim(bottom=1.0)
    ax.set_xlim(left=1.0)
    ax.set_xlabel('Total number of positive cases')
    ax.set_ylabel('Increase in positive cases')
    if title:
        ax.set_title(title)
    
    return slopes_by_state

def plot_percent_positive(state_data, slopes_by_state, N_avg, N_slope, label_states=None):
    '''
    Parameters
    ----------
    state_data : dict
        Dictionary with data by state.
    slopes_by_state: dict
        Dictionary of states with the slope of new positive cases as a function
        of total positive cases.
    N_avg int
        Number of days over which to average PercentPositive
    N_slope: int
        Number of days over which slope was taken
    label_states: list of str (optional)
        List of states to label in plot (Default: None)

    Returns
    -------
    None.

    '''
    # Set up plot
    fig, ax = plt.subplots()
    
    # Create lists for x and y coordinates as well as a color for the point
    slope_list      =   []  # x
    pct_pos_list    =   []  # y
    tot_pos_list    =   []  # color
    for state, slope in slopes_by_state.items():
        slope_list.append(slope)
        pct_pos = np.average(state_data[state]['PercentPositive'][-N_avg:])
        pct_pos_list.append(pct_pos)
        tot_pos_list.append(state_data[state]['positive'][-1])
        # If states are specified for labeling, go ahead and label them
        if label_states and state in label_states:
            ax.annotate(state, (slope, pct_pos))
            
    # Plot the scatter data
    im = ax.scatter(slope_list, pct_pos_list,
                    c=tot_pos_list,
                    norm=colors.LogNorm(),
                    cmap='coolwarm')
    
    # Create a colorbar
    fig.colorbar(im, ax=ax, label="Total number of cases")
    
    # Label the plot
    xlab  = "Average additional new positive cases \n"
    xlab += "for each existing positive case over last {} days"
    ax.set_xlabel(xlab.format(N_slope))
    ylab  = "Average percent of tests \n"
    ylab += "that are positive over last {} days"
    ax.set_ylabel(ylab.format(N_avg))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(1.0))
    
    # Create a dividing line
    max_pct_pos_data = max(state_data.items(),
                      key=lambda x: x[1]['PercentPositive'][-1])
    max_pct_pos = max_pct_pos_data[1]['PercentPositive'][-1]
    ax.plot([0.0, 0.0], [0.0, max_pct_pos*1.1], 'k--', alpha=0.3)
    
    # Set limits and tight layout
    ax.set_ylim([0.0, 1.0])
    fig.tight_layout()

def sort_states_by(state_data, key, avg=1):
    '''
    Parameters
    ----------
    state_data : dict
        Dictionary of state data.
    key : str
        Key by which to sort all the states.
    avg : int (optional)
        Number of points over which to average the last data points (Default: 1)

    Returns
    -------
    List of tuples where each tuple contains the state and the value of the key
    for the state

    '''
    return [(kv_pair[0], np.average(kv_pair[1][key][-avg:])) 
                 for kv_pair in sorted(state_data.items(),
                                       key=lambda x : np.average(x[1][key][-avg:]))]

def moving_average(data, N):
    '''Creates a moving average of the data over N points'''
    return np.convolve(data, np.ones((N,))/N, mode='valid')

def moving_average2(data, N):
    '''Creates a moving average of the data over N points'''
    cumsum = np.cumsum(np.insert(data, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)    

class data_by_state(dict):
    '''
    Container for COVID19 data that is organized first by each state and then
    by a dictionary of time series.
    
    Example:
        data = data_by_state(url)
        state = NM
        positive_cases_over_time = data[state]['positive']
    '''
    def __init__(self, url, us_data_url=None):
        '''
        Take the provided URL, organize the data as entries for each state
        '''
        self.raw_data = json.loads(urlopen(url).read())
        self.raw_data_by_state = dict()
        self._store_raw_data_as_dict()
        if us_data_url:
            self.raw_us_data = json.loads(urlopen(us_data_url).read())
            self.raw_data_by_state['US'] = self.raw_us_data
        self._finalize_raw_data_form()
        self.store_time_series_data_sets()
        
    def _store_raw_data_as_dict(self):
        '''
        Store the dataset as a dictionary of arrays for each state. The keys
        in the dictionary are automatically determined from the entries.
        '''
        for entry in self.raw_data:
            state = self._get_state_from_entry(entry)
            try:
                self.raw_data_by_state[state].append(entry)
            except KeyError:
                # This state hasn't been stored yet
                self.raw_data_by_state[state] = [entry]
    
    def _get_state_from_entry(self, entry):
        '''
        Get the state from this entry and throw an error if this entry doesn't
        contain an entry for "state"
        '''
        try:
            state = entry['state']
        except KeyError:
            # This dataset does not have state data
            msg =  'An item in this dataset does not have a "state" field '
            msg += 'so the data set cannot be organized by state.\n'
            msg += 'Available data fields:\n'
            for key in entry.keys():
                msg += '\t{}\n'.format(key)
            raise RuntimeError(msg)
        else:
            return state
    
    def _finalize_raw_data_form(self):
        '''
        If an array, reverse the data. If a single entry, change from a list to
        just that entry.
        '''
        for state, entries in self.raw_data_by_state.items():
            if len(entries) == 1:
                entries = entries[0]
            else:
                entries = entries[::-1]
            self.raw_data_by_state[state] = entries
            
    def store_time_series_data_sets(self):
        '''
        From the raw data organized by state and then by a time series of
        dictionaries, instead organize by state and a dictionary of time
        series for each type of data in the dictionary.
        '''
        for state, entries in self.raw_data_by_state.items():
            try:
                keys = entries.keys()
            except AttributeError:
                # There are multiple entries
                keys = entries[-1].keys()
                # Store the data as a time series for each entry for each state
                self[state] = dict()
                for k in keys:
                    self[state][k] = []
                    for item in entries:
                        try:
                            value = item[k]
                        except KeyError:
                            # This key doesn't exist for this entry, so make
                            # the value zero
                            self[state][k].append(0.)
                        else:
                            if value:
                                self[state][k].append(value)
                            else:
                                self[state][k].append(0.)
                                
                # Now calculate the percent of tests that are positive
                pct_pos = self._compute_percent_positive(state, self[state])
                self[state]['PercentPositive'] = pct_pos
            else:
                # Only one entry that is stored as a dictionary
                self[state] = {k: entries[k] for k in keys}
        
    def _compute_percent_positive(self, state, data):
        '''
        Computes the percentage of tests that are returned positive as a
        function of time.
        '''
        try:
            return_data = [pos/tot if tot > 0 else 0. 
                                      for pos, tot in zip(data['positiveIncrease'],
                                                          data['totalTestResultsIncrease'])]
        except KeyError:
            # This data set doesn't have positive cases
            return
        else:
            return return_data
        
