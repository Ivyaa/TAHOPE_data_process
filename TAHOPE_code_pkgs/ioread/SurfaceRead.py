import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy    as np
import pandas   as pd
import xarray   as xr

from config.pathconfig  import *

class SURFOBS:
    '''
    onefile only
    The default of encoding is 'big5' for .mdf file.
    If needed, you can change the method of encoding
    Such as 'utf-8' or 'netcdf4'
    '''
    def __init__(self, file, encoding="big5"):
        self.file     = file
        self.encoding = encoding
    
    def read_mdf(self, skiprows=2, setting_elev=500, encoding=None, filtered_city=None, filtered_stid=None, filtered_var=None, filter_on=True, set_rename=False):
        '''
        read and filter the data you need

        returns:
        - pandas.Dataframe
        '''
        rename_mapping = {
            "H_FX": "WS15M",
            "H_XD": "WD15M"
        }

        if encoding is None:
            encoding = self.encoding
        
        df = pd.read_csv(self.file, sep='\s+', encoding=encoding, skiprows=skiprows)
        
        if set_rename:
            df.rename(columns=rename_mapping, inplace=True)

        if filtered_city is not None:
            filtered_city = filtered_city
            df            = df[df['CITY'].isin(filtered_city)]
        
        if filtered_var is not None:
            filtered_var = filtered_var
            df = df[filtered_var]

        if filtered_stid is not None:
            df = df[df["STID"].isin(filtered_stid)]

        if setting_elev is not None:
            df = df[df["ELEV"] <= setting_elev]

        
        # a filter to delete the nan values
        # (if temp or RH is nan, we don't use the station data)
        if filter_on:
            for column in ['TEMP', 'HUMD', 'WDIR', 'WDSD']:
                if column in df.columns:  # 確保欄位存在於 DataFrame 中
                    df[column] = df[column].apply(lambda x: np.nan if x < -50 else x)
            df = df.dropna(subset=['TEMP', 'HUMD'])
            # C0E730
            # df = df[df["STID"] != "C0E870"]
        
        return df
     
    def read_windprof_nc(self, start_tt="2022-06-29T14:00", end_tt="2022-06-29T20:00"):
        '''
        read windprofiler(nc file)
        How to convert .asd file to nc file
        please find the pkgs in utils/convert_windprofiler.py

        returns: 
        - xarray_dataset
        '''
        ds = xr.open_dataset(self.file, engine="netcdf4")

        # 設定正確的日期和時間範圍
        start_time = np.datetime64(start_tt)
        end_time = np.datetime64(end_tt)

        # 過濾時間範圍（每 10 分鐘）
        ds = ds.sel(time=slice(start_time, end_time)).resample(time="10min").nearest()

        # 限制高度範圍
        # ht_levels = np.arange(250, 7001, 300)
        # ds = ds.sel(ht=ht_levels, method="nearest")  
        # print(ds)
        
        return ds

class get_terrain:
    def __init__(self,file_path):
        self.file_path = file_path
        self.read_data()
        
    def read_data(self):
    # reading data
        data=np.load(self.file_path)
        # declare DEM info
        ll_lon=119.98996209645199
        ur_lat=25.324585249598865
        d_int=0.00018411111058945146
        size=(18764,10979)
        ll_lat=ur_lat-d_int*size[0]
        ur_lon=ll_lon+d_int*size[1]
        x = np.linspace(ll_lon, ur_lon, data.shape[1])
        y = np.linspace(ll_lat, ur_lat, data.shape[0])
        self.lon, self.lat = np.meshgrid(x, y)
        data=np.flipud(data)
        data[np.where(data<0)]=0
        self.data=data