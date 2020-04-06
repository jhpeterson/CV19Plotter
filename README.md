# CV19Plotter
Scripts for visualizing the COVID19 epidemic in the US by plotting data by states.

Run the data.py script to create the plots. It will fetch the latest data sets from the COVID Tracking Project (https://covidtracking.com/) and then plot all the states and a select state compared to a few other states. That state can be changed at the top of the data.py file.

If the plot slope is positive, that means that growth is exponential (although if it is getting flatter, the exponential growth is slowing). When exponential growth is haulted, the slope will become negative and a dramatic change in the plot will be visible.