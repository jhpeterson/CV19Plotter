# CV19Plotter
Scripts for visualizing the COVID19 epidemic in the US by plotting data by states.

Run the data.py script to create the plots. It will fetch the latest data sets from the COVID Tracking Project (https://covidtracking.com/) and then plot all the states and a select state compared to a few other states. That state can be changed at the top of the data.py file.

There are two types of plots. The first is a plot of the new cases plotted against existing cases on a log-log scale. If the plot slope is positive, that means that growth is exponential (although if it is getting flatter, the exponential growth is slowing). When exponential growth is haulted, the slope will become negative and a dramatic change in the plot will be visible.

The second type is a scatter plot showing the slope of the above plot for the last 15 days plotted on the x-axis and the percent of new tests that are positive averaged over the past 5 days. For this plot, you want both numbers to be low which means that a state is testing well in addition to bending the curve. If the percentage of tests that are positive is high, it means that the state likely isn't testing a representative population and that there might be a lot more cases lurking out there.
