# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 2020

@author: Jeff Peterson
"""
import numpy as np

def moving_average(data, N):
    '''Creates a moving average of the data over N points'''
    return np.convolve(data, np.ones((N,))/N, mode='valid')
