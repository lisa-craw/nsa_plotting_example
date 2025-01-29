# converts raw data received from satellite to a .csv of processed values.
# INPUT: log_file_name = location of hex data file as received from satellite. Single file (multiple files will need to be concatenated)
# OUTPUT: output_file_name = location to save processed data as .csv file.

# OUTPUT FILE FORMAT
# Single line header
# as comma separated columns:
# time = date and time of measurement in datetime format
# UID = unique ID of cryowurst (CF + last two digits of year + instrument number)
# tmp_temp = temperature measured by TMP117 sensor in degrees C
# keller_temp = temperature measured by keller sensor in degrees C
# pressure = pressure measured by keller sensor in bar
# imu_x, imu_y, imu_z = x, y and z components of acceleration measured by IMU (CHECK UNITS)
# tilt_pitch = pitch measured by TILT-05 OEM tilt sensor, degrees
# tilt_roll = roll measured by TILT-05 OEM tilt sensor, degrees
# wurst_voltage = battery voltage on wurst tadiran battery, V
# logger_voltage = voltage supplied to data logger at the surface, V


import datetime
import pandas as pd
import numpy as np
import os
import glob
import struct


#region functions
def convert_keller_pressure (raw_pressure):
    # converts Keller digital values to real pressures in bar
    bar_pressure = 0.0

    keller_max_bar = 30 # 100 bar for demo kit sensor - 250 bar for real sensor - 30 bar for Cryowurst 2024
    keller_min_bar = 0 # 0 bar for our sensor - it doesn't go down to vacuum

    pressure_range = keller_max_bar - keller_min_bar

    bar_pressure = ((raw_pressure - 16384) * (pressure_range / 32768)) + keller_min_bar

    return bar_pressure

def convert_keller_temperature (raw_temperature):
    # converts Keller digital values to real temperatures in Celcius
    # reduces precision to 12-bits as recommended by Keller

    celcius_temp = 0.0

    celcius_temp =  (((raw_temperature >> 4) - 24) * 0.05) - 50

    return celcius_temp

#endregion

# set directory locations
# create raw and processed data directories if they don't already exist
working_directory = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(working_directory+'/data/'):
    os.makedirs(working_directory+'/data/')

raw_data_directory = working_directory+'/data/raw/'
if not os.path.exists(raw_data_directory):
    os.makedirs(raw_data_directory)

processed_data_directory = working_directory+'/data/processed/'
if not os.path.exists(processed_data_directory):
    os.makedirs(processed_data_directory)


# load all cloudloop data in the data directory
# this just looks for all .csv files with 'cloudloop' in the name, and adds them to the dataframe
all_data=[]
file_list = glob.glob(raw_data_directory+'*cloudloop*.csv') 
#file = file_list[0]
for file in file_list:
    df = pd.read_csv(file, header=None, usecols=[0])
    df = df.dropna()
    df = df.to_numpy().squeeze()
    all_data = np.concatenate((all_data, df), axis=0)
all_data.squeeze()
 

#region decode data and save to output file

output_file_name = processed_data_directory+'satellite_data_processed.csv'
output_file = open(output_file_name, 'w')
output_file.write('time,UID,tmp_temp,keller_temp,pressure,mag_x,mag_y,mag_z,imu_x,imu_y,imu_z,tilt_x,tilt_y,tilt_z,tilt_pitch,tilt_roll,ec,wurst_voltage,logger_voltage,logger_pressure,logger_temp,channel_number')
output_file.write("\n")

for index in range(len(all_data)):
    # each satellite packet contains multiple cryowurst packets
    satellite_packet = bytes.fromhex(all_data[index])  
    if satellite_packet[0:2] == b'W2':    #decode only wurst packets (not other instruments)
        wurst_packet_length = 62
        n=0
        sat_packet_length = len(satellite_packet)
        
        #decode data from each individual packet
        while n<=sat_packet_length-wurst_packet_length:
            single_packet = satellite_packet[n:n+wurst_packet_length]

            time_binary = int.from_bytes(single_packet[2:6], byteorder = 'little', signed=True)
            time_formatted = datetime.datetime.fromtimestamp(time_binary)

            raw_uid = int.from_bytes(single_packet[21:25], byteorder = 'little', signed=False)

            raw_tmp_temp = int.from_bytes(single_packet[28:30], byteorder = 'little', signed=True)
            
            raw_pressure = int.from_bytes(single_packet[54:56], byteorder = 'little', signed=False)

            raw_keller_temp = int.from_bytes(single_packet[57:59], byteorder = 'little', signed=True)

            raw_mag_x = int.from_bytes(single_packet[30:32], byteorder = 'little', signed=False)
            raw_mag_y = int.from_bytes(single_packet[32:34], byteorder = 'little', signed=False)
            raw_mag_z = int.from_bytes(single_packet[34:36], byteorder = 'little', signed=False)

            raw_imu_x = int.from_bytes(single_packet[36:38], byteorder = 'little', signed=True)
            raw_imu_y = int.from_bytes(single_packet[38:40], byteorder = 'little', signed=True)
            raw_imu_z = int.from_bytes(single_packet[40:42], byteorder = 'little', signed=True)
            
            raw_tilt_x = int.from_bytes(single_packet[42:44], byteorder = 'little', signed=True)
            raw_tilt_y = int.from_bytes(single_packet[44:46], byteorder = 'little', signed=True)
            raw_tilt_z = int.from_bytes(single_packet[46:48], byteorder = 'little', signed=True)

            raw_tilt_pitch = int.from_bytes(single_packet[48:50], byteorder = 'little', signed=True)
            raw_tilt_roll= int.from_bytes(single_packet[50:52], byteorder = 'little', signed=True)
            raw_ec = int.from_bytes(single_packet[52:54], byteorder = 'little', signed=False)

            raw_wurst_voltage = int.from_bytes(single_packet[58:60], byteorder = 'little', signed=True)
            
            raw_logger_voltage = int.from_bytes(single_packet[14:16], byteorder = 'little', signed=True)
            raw_logger_pressure= int.from_bytes(single_packet[10:14], byteorder = 'little', signed=True)
            [raw_logger_temp]= struct.unpack('f', single_packet[6:10])
            channel_number = int.from_bytes(single_packet[16:17], byteorder='little', signed=False)

            #write to file
            output_file.write(str(time_formatted))
            output_file.write(",")
            output_file.write('{0:x}'.format(raw_uid))
            output_file.write(",")
            output_file.write(str(raw_tmp_temp*0.0078125))
            output_file.write(",")
            output_file.write(str(convert_keller_temperature(raw_keller_temp)))
            output_file.write(",")
            output_file.write(str(convert_keller_pressure(raw_pressure)))
            output_file.write(",")
            output_file.write(str(raw_mag_x))
            output_file.write(",")
            output_file.write(str(raw_mag_y))
            output_file.write(",")
            output_file.write(str(raw_mag_z))
            output_file.write(",")
            output_file.write(str(raw_imu_x*(1000/16384)))
            output_file.write(",")
            output_file.write(str(raw_imu_y*(1000/16384)))
            output_file.write(",")
            output_file.write(str(raw_imu_z*(1000/16384)))
            output_file.write(",")
            output_file.write(str(raw_tilt_x))
            output_file.write(",")
            output_file.write(str(raw_tilt_y))
            output_file.write(",")
            output_file.write(str(raw_tilt_z))
            output_file.write(",")
            output_file.write(str(raw_tilt_pitch*0.1))
            output_file.write(",")
            output_file.write(str(raw_tilt_roll*0.1))
            output_file.write(",")
            output_file.write(str(raw_ec))
            output_file.write(",")
            output_file.write(str(raw_wurst_voltage))
            output_file.write(",")
            output_file.write(str(raw_logger_voltage))
            output_file.write(",")
            output_file.write(str(raw_logger_pressure))
            output_file.write(",")
            output_file.write(str(raw_logger_temp))
            output_file.write(",")
            output_file.write(str(channel_number))
            output_file.write("\n")


            n+=wurst_packet_length

print('All done! Processed data saved as '+output_file_name+'.')
