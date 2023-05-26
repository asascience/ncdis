%DataPrep_RFA.m
% detrend data, find daily max, filter daily max, find 98th percentile
%4/14/2023

%===============================================================

%% DailyMax Function

function [dmax]=DailyMax(t,h)
    %t=time vector, h=hourly sea level data, r=#day/2 filter (ex: if 5-day
    %filter, r=2.5)
    
    %daily data from hourly data
    dh=reshape(h,24,length(h)/24);
    dt=reshape(t,24,length(t)/24);
    [h1 idx]=nanmax(dh);
    tm=nan(length(h1),1);
    for i=1:length(h1)
        t1(i)=dt(idx(i),i);
    end
    dmax=[t1' h1']; %daily max
    
    end

%% Filtered data

function [fdata] = FilterData(dmax,r)
    %dmax = daily max
    %r = filter window
    
    %filter daily data
    dmSort = sortrows(dmax,-2); %sort by highest water level
    for i = 1:length(dmSort)
        if ~isnan(dmSort(i,2))
            id = find(dmSort(:,1) >= dmSort(i,1)-r & dmSort(:,1) <= dmSort(i,1)+r); %indices of all times within window of highest WL
            if length(id)>1
                id1 = find(dmSort(id,2) == nanmax(dmSort(id,2))); % index of max WL
                id(id1)=[];
                dmSort(id,2)=nan; % assign nan to all WL that are not the max within the time frame
            end
        end
    end
    fdata = dmSort(~isnan(dmSort(:,2)),:); %remove nan in filtered data
    
    end

%h1612340.mat is just an example from exiting data files


% Load data
data = load('h1612340.mat');
meta=data.meta;
st=str2num(meta{1}(11:end))
name=meta{2}(12:end)
t=data.T; SL=data.SL/1000; %put data on meters

% Detrend data
tt=[t ones(length(t),1)]; %matrix for regression
b=regress(SL,tt);
slope=b(1)*365.25; %m/yr
yh=tt*b;

%center around 2000
idx = find(t==datenum(2000,7,1,0,0,0)); %find midpoint of the year 2000 (July 1, 2000)
yh = yh - yh(idx); %center around midpoint
h = SL - yh; % detrend timeseries

%calculate daily max
dailyMax=DailyMax(t,h); 

%calculate MHHW over a 19-yr period and put daily max on MHHW datum
%Let's discuss this step.  Likely will use the 1991-2009 period to estimate
%MHHW: average of daily max model reanalysis.

%filter daily max
r=2; %4-day filter: 2 days on each side.
daily_filtered = FilterData(dailyMax,r)
yrs = unique(year(daily_filtered(:,1))); %years of data

%calculate 98th percentile threshold
u=prctile(daily_filtered(:,2),98); 

%exceedences above the threshold
j=find(daily_filtered(:,2)>u);
excess=daily_filtered(daily_filtered(:,2)>u,:); %values above the threshold

exceedance=excess(:,2)-u;  %exceedance used in stationary GPD
lambda =length(exceedance)/length(yrs); %mean #exceedances/yr

figure
plot(dailyMax(:,1),dailyMax(:,2),'-*')
hold
plot(daily_filtered(:,1),daily_filtered(:,2),'*')
plot(excess(:,1),excess(:,2),'o')
v=axis;
plot([v(1) v(2)],[u u],'k-','linewidth',1.5)
legend('Daily Max','Filtered Data','Filtered Data above threshold')
ylabel('Sea Level (m)')
datetick
title(name)
datetick
