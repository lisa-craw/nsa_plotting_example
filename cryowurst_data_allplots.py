# takes as input the output .csv file from cryowurst_raw_data_process.py (in this directory)
# produces several plots of wurst data:
# wurst_pressure.png = pressure readings from keller sensors on basal wurste
# wurst_voltage.png = tadiran battery voltage on all wurste
# logger_voltage.png = voltage on data logger
# tilt_roll.png = absolute values of tilt and roll from TILT-05 OEM tilt sensor, all wurste
# tilt_roll_depth.png = change in tilt and roll from initial value (colour) over depth and time for all wurste
# temp_depth.png = temperature from TILT-05 OEM tilt sensor (colour) over depth and time for all wurste

# axis and caxis limits will need to be changed as the dataset size increases.

import datetime
from datetime import timezone
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
pd.options.mode.chained_assignment = None  # stop false positive chained assignment warnings
import numpy as np
import matplotlib.dates as mdates
import cmocean
import seaborn as sns
import glob
import os 
#from scipy.interpolate import make_interp_spline

#set current directory as the working directory, and create a /plots/ directory if there 
# isn't one already
working_directory = os.path.dirname(os.path.abspath(__file__))
output_path = working_directory+'/plots/'
if not os.path.exists(output_path):
    os.makedirs(output_path)

#region import data and format datetime
satellite_file = working_directory+'/data/processed/satellite_data_processed.csv'
all_data = pd.read_csv(satellite_file)

good_time=[]
for i in range(0, len(all_data)):
#    all_data['time'][i] = datetime.datetime.strptime(all_data['time'][i], '%Y-%m-%d %H:%M:%S')  
     good_time.append(datetime.datetime.strptime(all_data['time'][i], '%Y-%m-%d %H:%M:%S'))  
all_data['time']=good_time
#endregion

#region combine available files from weather station data
# weather data from Kaskawulsh weather station:
# download latest .txt file from this address, and save in raw data directory 
# https://datagarrison.com/users/300034012631040/300234068884730/
weather_list = glob.glob(working_directory+'/data/raw/300234068884730*.txt')
weather_list.sort()
weather_data = pd.read_csv(weather_list[0], delimiter='\t', header=2, skipfooter=2, engine='python')
for index in range(1, len(weather_list)):
    filename = weather_list[index]
    data = pd.read_csv(filename, delimiter='\t', header=2, skipfooter=2, engine='python')
    weather_data = pd.concat([weather_data, data], ignore_index=True)

good_time=[]
#weather_data['datetime'] = 0
for index in range(len(weather_data['Date_Time'])):
    #weather_data['datetime'][index] = datetime.datetime.strptime(weather_data['Date_Time'][index], '%m/%d/%y %H:%M:%S')
    good_time.append(datetime.datetime.strptime(weather_data['Date_Time'][index], '%m/%d/%y %H:%M:%S'))
weather_data['datetime']=good_time
#endregion

#region data processing
#make sure data are in order of time
all_data = all_data.sort_values(by=['time'])
all_data = all_data.sort_values(by=['time'])

#correct for local pressure, measured by receiver
all_data['pressure']=all_data['pressure']-(all_data['logger_pressure']/1e9)

# add wurst depths to dataframe
all_data['depth'] = np.zeros(len(all_data))
all_data['depth'].loc[all_data['UID']=='cf240002'] = 138
all_data['depth'].loc[all_data['UID']=='cf240004'] = 157.8
all_data['depth'].loc[all_data['UID']=='cf240007'] = 87.19 
all_data['depth'].loc[all_data['UID']=='cf240008'] = 36.89 

#separate out different wurste into separate dataframes
#depth1=138m
wurst2 = all_data[all_data['UID']=='cf240002']
#depth4 = 157.8
wurst4 = all_data[all_data['UID']=='cf240004']
#depth7 = 87.19 
wurst7 = all_data[all_data['UID']=='cf240007']
#depth8 = 36.89
wurst8 = all_data[all_data['UID']=='cf240008']
    
#get change in tilt for each wurst, relative to starting value
wurst2['change_in_pitch']=wurst2['tilt_pitch']-wurst2['tilt_pitch'].values[0]
wurst4['change_in_pitch']=wurst4['tilt_pitch']-wurst4['tilt_pitch'].values[0]
wurst7['change_in_pitch']=wurst7['tilt_pitch']-wurst7['tilt_pitch'].values[0]
wurst8['change_in_pitch']=wurst8['tilt_pitch']-wurst8['tilt_pitch'].values[0]

wurst2['change_in_roll']=wurst2['tilt_roll']-wurst2['tilt_roll'].values[0]
wurst4['change_in_roll']=wurst4['tilt_roll']-wurst4['tilt_roll'].values[0]
wurst7['change_in_roll']=wurst7['tilt_roll']-wurst7['tilt_roll'].values[0]
wurst8['change_in_roll']=wurst8['tilt_roll']-wurst8['tilt_roll'].values[0]

#region set default colours for each instrument
#grab colour list from style
colours = sns.color_palette("husl", 8)
wurst2_colour = colours[1]
wurst4_colour = colours[3]
wurst7_colour = colours[6]
wurst8_colour = colours[7]
temp_colour = colours[4]
humidity_colour = colours[5]
colour_adjust = -0.15
wurst4_colour_3 = (colours[3][0]-colour_adjust, colours[3][1]-colour_adjust,colours[3][2]-colour_adjust)
wurst4_colour_2 = (colours[3][0]+colour_adjust, colours[3][1]+colour_adjust,colours[3][2]+colour_adjust)

# define function for converting rgb colours to hex codes (useful for adjusting colours)
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
#endregion
#endregion

#region plotting time!

#formatting settings:
#set how far apart to plot x-axis ticks (can adjust this as more data comes in)
hour_locator = 48 
#set offset to leave a gap at start and end of plot
axis_offset = datetime.timedelta(hours=24)
#set marker size
ms = 3 

#default min and max time on x axis (start of deployment until today)
min_time = datetime.datetime(2024, 7, 22, 12, 0, 0)
max_time = datetime.datetime.now(timezone.utc)

#region plot wurst pressure plus data from weather station
#fig_pressure, (ax_pressure, ax_temperature, ax_humidity) = plt.subplots(3,1, figsize=(12,12), sharex=True)
fig_pressure, (ax_pressure, ax_logger_temperature, ax_air_temperature) = plt.subplots(3,1, figsize=(12,12), sharex=True)
ax_pressure.plot(wurst2['time'], wurst2['pressure'], '.', label='CF240002, 138m', color=wurst2_colour, markersize=ms)
ax_pressure.plot(wurst4['time'], wurst4['pressure'], '.', label='CF240004, 158m', color=wurst4_colour, markersize=ms)
#ax_pressure.set_xlabel('date')
ax_pressure.set_ylabel('pressure, bar')
ax_pressure.set_title('wurst pressure')
ax_pressure.legend(loc='lower right')
ax_pressure.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax_pressure.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax_pressure.set_xlim([min(wurst2['time'])-axis_offset, max(wurst2['time'])+axis_offset])
ax_pressure.set_xlim([min_time, max_time])
ax_pressure.set_ylim([2, 17])
ax_pressure.xaxis.set_tick_params(rotation=90)

#ax_humidity.plot(weather_data['datetime'], weather_data['RH_20339014_%'], '.', color=temp_colour)
##ax_humidity.set_xlabel('date')
#ax_humidity.set_ylabel('humidity, $^{\circ}\,C$')
##ax_humidity.set_ylim([-25,25])
#ax_humidity.set_xlim([min_time, max_time])
#ax_humidity.set_title('relative humidity, %')
#ax_humidity.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
#ax_humidity.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
#ax_humidity.set_xlim([min(wurst2['time'])-axis_offset, max(wurst2['time'])+axis_offset])
#ax_humidity.xaxis.set_tick_params(rotation=90)

#ax_logger_temperature.plot(weather_data['datetime'], weather_data['Temperature_20339014_°C'], '.', color=temp_colour)
ax_logger_temperature.plot(all_data['time'], all_data['logger_temp'], '.', color=temp_colour, markersize=ms)
ax_logger_temperature.set_xlabel('date')
ax_logger_temperature.set_ylabel('temperature, $^{\circ}\,C$')
ax_logger_temperature.set_ylim([-30,30])
ax_logger_temperature.set_xlim([min_time, max_time])
ax_logger_temperature.set_title('datalogger temperature')
ax_logger_temperature.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax_logger_temperature.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax_logger_temperature.set_xlim([min(wurst2['time'])-axis_offset, max(wurst2['time'])+axis_offset])
ax_logger_temperature.xaxis.set_tick_params(rotation=90)

ax_air_temperature.plot(weather_data['datetime'], weather_data['Temperature_20339014_°C'], '.', color=humidity_colour, markersize=ms)
ax_air_temperature.set_xlabel('date')
ax_air_temperature.set_ylabel('temperature, $^{\circ}\,C$')
ax_air_temperature.set_ylim([-30,30])
ax_air_temperature.set_xlim([min_time, max_time])
ax_air_temperature.set_title('air temperature, Kaskawulsh')
ax_air_temperature.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax_air_temperature.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax_air_temperature.set_xlim([min(wurst2['time'])-axis_offset, max(wurst2['time'])+axis_offset])
ax_air_temperature.xaxis.set_tick_params(rotation=90)
plt.tight_layout()
plt.savefig(output_path + 'wurst_pressure.png')
plt.savefig(output_path + 'wurst_pressure.svg', format='svg', dpi=1200)
#endregion

#region plot voltage on all instruments
fig_wurst_voltage, ax = plt.subplots(figsize=(10,5)) 
ax.plot(wurst2['time'], wurst2['wurst_voltage'], '.', label='CF240002', color=wurst2_colour)
ax.plot(wurst4['time'], wurst4['wurst_voltage'], '.', label='CF240004', color=wurst4_colour)
ax.plot(wurst7['time'], wurst7['wurst_voltage'], '.', label='CF240007', color=wurst7_colour)
ax.plot(wurst8['time'], wurst8['wurst_voltage'], '.', label='CF240008', color=wurst8_colour)
ax.legend()
ax.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax.xaxis.set_tick_params(rotation=90)
plt.title('instrument battery voltage')
plt.xlabel('date')
plt.ylabel('voltage, mA')
plt.tight_layout()
plt.savefig(output_path + 'wurst_voltage.png')
plt.savefig(output_path + 'wurst_voltage.svg', format='svg', dpi=1200)
#endregion

#min_time = datetime.datetime(2024, 11, 7, 0, 0, 0)
#max_time = datetime.datetime(2024, 11, 26, 12, 0, 0)
#region plot voltage on datalogger/receiver
fig_logger_voltage, ax = plt.subplots(figsize=(10,5))
ax.plot(all_data['time'], all_data['logger_voltage']*0.0041-0.3086, '.', color='#4B4E6D')
ax.plot(all_data['time'], all_data['logger_voltage']*0.0041-0.3086, color='#4B4E6D')
#ax.set_ylim([10, 16])
#ax.set_xlim([min_time, max_time])
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax.xaxis.set_tick_params(rotation=90)
plt.title('receiver battery voltage')
plt.xlabel('date')
plt.ylabel('logger voltage, V')
plt.tight_layout()
plt.savefig(output_path + 'logger_voltage.png')
plt.savefig(output_path+'logger_voltage.svg', format='svg', dpi=1200)
#region

#region plot temperature values 
fig_temp_curves, ax_temp_curves = plt.subplots(figsize=(11,5))
ax_temp_curves.plot(wurst8['time'], wurst8['tmp_temp'], '.', color=wurst8_colour, label='cf240008, 37m')
ax_temp_curves.plot(wurst7['time'], wurst7['tmp_temp'], '.', color=wurst7_colour, label='cf240007, 87m')
ax_temp_curves.plot(wurst2['time'], wurst2['tmp_temp'], '.', color=wurst2_colour, label='cf240002, 138m')
ax_temp_curves.plot(wurst4['time'], wurst4['tmp_temp'], '.', color=wurst4_colour, label='cf240004, 158m')
ax_temp_curves.set_xlabel('hours since deployment')
ax_temp_curves.set_ylabel('temperature, $^{\circ}$C')
ax_temp_curves.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax_temp_curves.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax_temp_curves.xaxis.set_tick_params(rotation=90)
ax_temp_curves.set_ylim([-0.2, 0.1])
ax_temp_curves.legend()
plt.title('wurst temperature')
plt.tight_layout()
fig_temp_curves.savefig(output_path+'temp_curves_together.svg', format='svg', dpi=1200)
fig_temp_curves.savefig(output_path+'temp_curves_together.png')
#endregion

#region plot temperature as color over depth and time
cmap=cmocean.cm.thermal
vmin = -0.2 
vmax = 0.0
fig_change_in_tilt, ax_temp = plt.subplots()
mappable = ax_temp.scatter(wurst2['time'], wurst2['depth'], 10, wurst2['tmp_temp'], cmap=cmap, vmin=vmin, vmax=vmax)
ax_temp.scatter(wurst4['time'], wurst4['depth'], 10, wurst4['tmp_temp'], cmap=cmap, vmin=vmin, vmax=vmax)
ax_temp.scatter(wurst7['time'], wurst7['depth'], 10, wurst7['tmp_temp'], cmap=cmap, vmin=vmin, vmax=vmax)
ax_temp.scatter(wurst8['time'], wurst8['depth'], 10, wurst8['tmp_temp'], cmap=cmap, vmin=vmin, vmax=vmax)
ax_temp.invert_yaxis()
ax_temp.set_title('temperature, degrees')
ax_temp.xaxis.set_major_locator(mdates.HourLocator(interval=hour_locator))
ax_temp.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
ax_temp.xaxis.set_tick_params(rotation=90)
plt.colorbar(mappable)
ax_temp.set_xlabel('date')
ax_temp.set_ylabel('depth, m')
plt.tight_layout()
plt.savefig(output_path + 'temp_depth.png')
plt.savefig(output_path + 'temp_depth.svg', format='svg', dpi=1200)
#endregion
