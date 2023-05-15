# DataPrep_RFA.m
# detrend data, find daily max, filter daily max, find 98th percentile
# 4/14/2023
# conversion to Python by chatGPT https://chat.openai.com

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import datetime as dt

# calculate daily max
def DailyMax(t, h):
    # t=time vector, h=hourly sea level data, r=#day/2 filter (ex: if 5-day filter, r=2.5)

    # daily data from hourly data
    dh = np.reshape(h, (24, int(len(h) / 24)))
    dt = np.reshape(t, (24, int(len(t) / 24)))
    h1 = np.nanmax(dh, axis=0)
    t1 = np.zeros(len(h1))
    for i in range(len(h1)):
        t1[i] = dt[np.argmax(dh[:, i]), i]
    dmax = np.column_stack((t1, h1))  # daily max
    return dmax


# filter daily max
def FilterData(dmax, r):
    # dmax = daily max
    # r = filter window

    # filter daily data
    dmSort = dmax[np.argsort(-dmax[:, 1])]
    for i in range(len(dmSort)):
        if not np.isnan(dmSort[i, 1]):
            id = np.where(np.logical_and(dmSort[:, 0] >= dmSort[i, 0] - r, dmSort[:, 0] <= dmSort[i, 0] + r))[0]
            if len(id) > 1:
                id1 = np.argmax(dmSort[id, 1])
                id = np.delete(id, id1)
                dmSort[id, 1] = np.nan
    fdata = dmSort[~np.isnan(dmSort[:, 1]), :]  # remove nan in filtered data
    return fdata

# h1612340.mat is just an example from exiting data files

# Load data
data = pd.read_csv('1612340_19800101_20221231.csv')
st = data['datetime'].iloc[0] # start year
#name = meta[1][0][11:]  # (JJ) we don't have name
t = data['datetime']
SL = data['hourly_height_STND_meters']

# Detrend data
tt= np.array([t, np.ones((len(t),1))]) # matrix for regression
b = np.linalg.lstsq(tt, SL, rcond=None)[0]
slope = b[0] * 365.25 # m/yr
yh = tt * b

# center around 2000
idx = np.where(t == datetime(2000, 7, 1).toordinal())[0][0] # find midpoint of the year 2000 (July 1, 2000)
yh = yh - yh[idx] # center around midpoint
h = SL - yh # detrend timeseries

dailyMax = DailyMax(t, h)

# calculate MHHW over a 19-yr period and put daily max on MHHW datum
# Let's discuss this step. Likely will use the 1991-2009 period to estimate
# MHHW: average of daily max model reanalysis.

# filter daily max
r = 2 # 4-day filter: 2 days on each side.

daily_filtered = FilterData(dailyMax, r)
yrs = np.unique(np.array([datetime.fromordinal(int(d)).year for d in daily_filtered[:,0]])) # years of data

# calculate 98th percentile threshold
u = np.percentile(daily_filtered[:,1], 98)

# exceedences above the threshold
j = np.where(daily_filtered[:,1] > u)[0]
excess = daily_filtered[daily_filtered[:,1] > u,:] # values above the threshold

exceedance = excess[:,1] - u # exceedance used in stationary GPD
lambda_ = len(exceedance) / len(yrs) # mean #exceedances/yr


###############################################################
# create a figure
fig, ax = plt.subplots()

# plot dailyMax
ax.plot(dailyMax[:,0], dailyMax[:,1], '*-', label='Daily Max')

# plot daily_filtered
ax.plot(daily_filtered[:,0], daily_filtered[:,1], '*', label='Filtered Data')

# plot excess
ax.plot(excess[:,0], excess[:,1], 'o', label='Filtered Data above threshold')

# plot 98th percentile threshold
v = ax.axis()
ax.plot([v[0], v[1]], [u, u], 'k-', linewidth=1.5)

# add legend, ylabel, and datetick
ax.legend()
ax.set_ylabel('Sea Level (m)')
ax.set_title('Title of Dataset')
plt.xticks(rotation=45)
plt.subplots_adjust(bottom=0.2)
plt.show()
