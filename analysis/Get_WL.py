import numpy, pandas as pd, json, requests, time
import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime
import myUtils



datum = str(input('Please enter Datum (The default Datum is STND, press **Enter** to use default) : ')) or 'STND'
time_zone = str(input('Please enter Time Zone (The default time zone is GMT, press **Enter** to use default) : ')) or 'GMT'
units = str(input('Please enter Time Zone (The default unit is Metric, press **Enter** to use default) : ')) or 'Metric'
interval= str(input('Please enter Interval (The default inerval is h for hourly height, press **Enter** to use default) : ')) or 'h'
station = str(input('Please enter Station ID : '))
begin_date = str(input('Please enter Begin Date (eg 20010101) : '))
end_date = str(input('Please enter End Date (eg 20011231) : '))
product = str(input('Please enter product (The default inerval is hourly_height, press **Enter** to use default) : ')) or 'hourly_height'
product1 = 'predictions'


#This function will creat a list of date ranges 
def timestep(product, begin_date, end_date):
    #convert start date and end date into YYYYMMDD format
    start_date = datetime.strptime(begin_date,'%Y%m%d')
    end_date = datetime.strptime(end_date,'%Y%m%d')
    
    if (product == 'one_minute_water_level'):
        step = dt.timedelta(days = 5)
    elif (product == 'hourly_height') or (product == 'high_low') or product == 'predictions':
        step = dt.timedelta(days = 365)
    elif (product == 'daily_mean') or (product == 'monthly_mean'):
        step = dt.timedelta(days = 10 * 365)
    else:
        step = dt.timedelta(days=31)
    print(step)
    
    #initiate date range
    dateRange = [start_date, end_date]
    
    startDate = [dateRange[0]]
    endDate=[dateRange[1]]
    
    #store start dates in the list 
    while (startDate[-1] < dateRange[1]):
        startDate.append(startDate[-1] + step)
    
    #remove start date from list is greater than end date   
    if startDate[-1]>dateRange[1]:
        startDate.remove(startDate[-1])

       
    print(dateRange)
    
    return startDate, step 


 #Iterate through each time step to retrieve observed and predicted data and calculate the residuals 
startDate, step = timestep(product, begin_date, end_date)
#startDate, step (for testing)

#initiate an empty list to store data frames  
stn_WL = []

for d in startDate:
            d2 = d + step - dt.timedelta(hours=1)
            d = datetime.strptime(str(d),'%Y-%m-%d %H:%M:%S')
            d = d.strftime('%Y%m%d')
            d2 = datetime.strptime(str(d2),'%Y-%m-%d %H:%M:%S')
            d2 = d2.strftime('%Y%m%d')
            if d2 > end_date:
                d2 = end_date
            #print(d, d2) #for testing only


            print("\nRetrieving data for " + station + " from " + begin_date + " to " + end_date)


            #Get water level Observations 
            try:
                content = myUtils.pull_obs (d, d2, station, product, datum, time_zone, interval, units)
                wl_obs_df = myUtils.massage_data (content)
                wl_obs_df = wl_obs_df.rename(columns={"observed": "Hourlyobs"})
            except:  
                print("No data found for station.")
                wl_obs_df = pd.DataFrame()
                #print(wl_obs_df) #for testing only      
            
            #append each DataFrame in to a list
            stn_WL.append(wl_obs_df)
            #print(stn_WL) # for testing only 

#merge the list of DataFrames into a single big DataFrame
all_WL_df = pd.concat(stn_WL, axis=0, ignore_index = False)
#all_WL_df #uncomment for testing

#export data in a csv format 
all_WL_df.to_csv(station + '_' + begin_date + '_' + end_date +'.csv', index=True)
print('\x1b[1;31m'+'Done retrieving data, please check csv output'+'\x1b[0m')

