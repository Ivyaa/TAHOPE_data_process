import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy    as np
import pandas   as pd
import xarray   as xr

from config.pathconfig  import *

#metpy
from metpy import calc as cc
from metpy.units import units
from metpy.calc import mixing_ratio_from_relative_humidity, dewpoint_from_relative_humidity, equivalent_potential_temperature
from metpy.calc import wind_components, virtual_temperature_from_dewpoint

class Soundread:
    '''
    read sounding data (txt and csv)
    return: object
    '''
    
    def __init__(self,file,SMOOTH_ON=False):
        self.file = file
        self.read_file(SMOOTH_ON=SMOOTH_ON)
    
    def read_file(self, SMOOTH_ON):
        
        # 检查文件后缀
        if self.file.endswith('.txt'):
            self.read_txt(SMOOTH_ON)
        elif self.file.endswith('.csv'):
            self.read_csv(SMOOTH_ON)
        else:
            print("Unsupported file format.")
            
            
    #台灣附近區域所獲取探空之txt資料讀取
    def read_txt(self, SMOOTH_ON):
        column_names = ["Time", "P", "Height", "T", "Td", "RH", "WD", "WS", "Lat", "Lon"]
        df = pd.read_csv(self.file, delimiter=' ',skiprows=1,header=None,names=column_names, skipinitialspace=True, na_values=["-999.00"])
        
        p_index = df.index[df["P"] > 110].tolist()
        df = df.loc[p_index]
        
        height = df["Height"].astype(float)
        p  = df["P"].astype(float); T  = df["T"].astype(float); Td = df["Td"].astype(float); rh = df["RH"].astype(float)
        ws = df["WS"].astype(float)       ; wd = df["WD"].astype(float)
        
        height_array = np.array(height)
        p_array = np.array(p); T_array = np.array(T); Td_array = np.array(Td); rh_array = np.array(rh)
        ws_array = np.array(ws); wd_array = np.array(wd)
        
        u, v = cc.wind_components(ws_array * units('m/s'), wd_array * units.deg)
        
        u_array = np.round(u.magnitude,2)
        v_array = np.round(v.magnitude,2)
        
        if SMOOTH_ON:
            smooth_cols     = ["T", "Td", "RH"]
            df[smooth_cols] = df[smooth_cols].rolling(window=3, center=True, min_periods=1).mean()

            skip=1
        else:
            skip=2

        # skip = 2
        self.H  = height_array[0:-1:skip]
        self.P  = p_array[0:-1:skip]
        self.T  = T_array[0:-1:skip]
        self.Td = Td_array[0:-1:skip]
        self.RH = rh_array[0:-1:skip]
        self.U  = u_array[0:-1:skip]
        self.V  = v_array[0:-1:skip]
        self.ws = ws_array[0:-1:skip]
        self.wd = wd_array[0:-1:skip]
        

    #TAHOPE verifying data
    def read_csv(self, SMOOTH_ON):
        column_names = ["Field", "Time", "P", "T", "RH", "WS", "WD", "Lat", "Lon", "Height", "GPS_Altitude", "Td", "U", "V", "Ascent"]
        df = pd.read_csv(self.file, delimiter=',',skiprows=46,header=None,names=column_names, skipinitialspace=True, na_values=["NaN"])
        
        p_index = df.index[df["P"] > 110].tolist()
        df = df.loc[p_index]
        
        height = df["Height"].astype(float)
        p  = df["P"].astype(float); T  = df["T"].astype(float); Td = df["Td"].astype(float); rh = df["RH"].astype(float)
        u  = df["U"].astype(float); v  = df["V"].astype(float); ws = df["WS"].astype(float)       ; wd = df["WD"].astype(float)
        
        height_array = np.array(height)
        p_array = np.array(p); T_array = np.array(T); Td_array = np.array(Td); rh_array = np.array(rh)
        u_array = np.array(u); v_array = np.array(v); ws_array = np.array(ws); wd_array = np.array(wd)

        if SMOOTH_ON:
            smooth_cols     = ["T", "Td", "RH"]
            df[smooth_cols] = df[smooth_cols].rolling(window=3, center=True, min_periods=1).mean()

            skip=1
        else:
            skip=2

        # skip = 2
        self.H  = height_array[0:-1:skip]
        self.P  = p_array[0:-1:skip]
        self.T  = T_array[0:-1:skip]
        self.Td = Td_array[0:-1:skip]
        self.RH = rh_array[0:-1:skip]
        self.U  = u_array[0:-1:skip]
        self.V  = v_array[0:-1:skip]
        self.ws = ws_array[0:-1:skip]
        self.wd = wd_array[0:-1:skip]

## test Soundread
# data = Soundread(str(SOUNDING_CSV), SMOOTH_ON=False)
# print(np.shape(data.T))