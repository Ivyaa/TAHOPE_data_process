import os
import re
import struct

import gzip     as gz
import numpy    as np
import pandas   as pd
import xarray   as xr
import xradar   as xd
import datetime as dt

import matplotlib.pyplot as plt

import cartopy.crs     as ccrs
import cartopy.feature as cfeature

from geopy.distance import geodesic
from pyproj         import CRS, Transformer
from pathconfig     import *
from othsettings    import U_matrix, V_matrix, U_matrix_3D, V_matrix_3D
from tool_utils     import *

class fileread:
    '''
    onefile only
    The default of encoding is 'big5' for .mdf file.
    If needed, you can change the method of encoding
    Such as 'utf-8' or 'netcdf4'
    '''
    def __init__(self, file, encoding="big5"):
        self.file     = file
        self.encoding = encoding
    
    def readmdf(self, skiprows=2, encoding=None, filtered_city=None, filtered_var=None, filter_on=True, set_rename=False):
        '''
        read and filter the data you need

        params:
        - file: reading file
        - skiprows: default is 2
        - encoding: default is big5
        - filtered_city: choosing city you want(str list)
        - filtered_var: choosing var you want(str list)

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
        
        # a filter to delete the nan values
        # (if temp or RH is nan, we don't use the station obs)
        if filter_on:
            for column in ['TEMP', 'HUMD', 'WDIR', 'WDSD']:
                if column in df.columns:  # 確保欄位存在於 DataFrame 中
                    df[column] = df[column].apply(lambda x: np.nan if x < -50 else x)
            df = df.dropna(subset=['TEMP', 'HUMD'])
            # C0E730
            df = df[df["STID"] != "C0E870"]
            # df = df[df["STID"].isin(["467490", "C0F9P0", "C0E750", "467571", "467050"])]
            df = df[df["ELEV"] <= 500]
        
        return df
    
    def readcsv(self):
        pass
    
    def readCOMPREF2D(self):
        '''
        reading 2D mosaic radar file 
        return the results concluding lat, lon and refdata
        '''
        f = gz.open(self.file,"rb").read()
        
        #reading time info
        info=np.array(struct.unpack('<9i4s10i',f[0:80]))
        self.yyyy=int(info[0])
        self.mm=  int(info[1])
        self.dd=  int(info[2])
        self.hh=  int(info[3])
        self.mn=  int(info[4])
        self.ss=  int(info[5])
        self.nx=  int(info[6])
        self.ny=  int(info[7])
        self.nz=  int(info[8])
        self.time_str=str(self.yyyy)+str(self.mm).zfill(2)+str(self.dd).zfill(2)+str(self.hh).zfill(2)\
                           +str(self.mn).zfill(2)+str(self.ss).zfill(2)
        self.datetime=dt.datetime.strptime(self.time_str,"%Y%m%d%H%M%S")

        #reading map projection and grid scale
        self.proj=info[9]
        self.map_scale= int(info[10])
        self.projlat1 = int(info[11])
        self.projlat2 = int(info[12])
        self.projlon  = int(info[13])
        self.alon     = int(info[14])
        self.alat     = int(info[15])
        self.xy_scale = int(info[16])
        self.dx       = int(info[17])
        self.dy       = int(info[18])
        self.dxy_scale= int(info[19])
        info=np.array(struct.unpack('<'+str(self.nz+11)+'i20s6s3i',f[80:80+(self.nz+14)*4+26]))
        next_ind=80+self.nz*4
        self.zht=np.array(struct.unpack('<'+str(self.nz)+'i',f[80:next_ind])).astype(np.float32)
        info=np.array(struct.unpack('<11i20s6s3i',f[next_ind:next_ind+14*4+26]))
        self.z_scale=int(info[0])
        self.i_bb_mode=int(info[1])
        self.unkn01=np.array(info[2:10]).astype(np.float32)

        #reading data
        self.varname=str(info[11],'utf-8','ignore').replace('\x00','')
        self.varunit=str(info[12],'utf-8','ignore').replace('\x00','')
        self.var_scale= int(info[13])
        self.missing  = int(info[14])
        self.nradar   = int(info[15])
        next_ind=next_ind+14*4+26
        self.mosradar=re.findall('....',(str(struct.unpack('<'+str(self.nradar*4)+'s', \
                      f[next_ind:next_ind+self.nradar*4])[0],'utf-8','ignore')))
        data_int = struct.unpack(self.nx*self.ny*self.nz*'h', f[-self.nx*self.ny*self.nz*2:])
        data=np.array(data_int).astype(np.float32)/self.var_scale

        #data/lat/lon reshape
        if '30L' in self.file:
          self.file_type='mosaicked refl RWRF'
          self.lon, self.lat = np.load('/home/c052/Pub/anaconda3/envs/plotenv/lib/python3.6/site-packages/cwbplot/sharedata/MREF_lonlat.npy')
        else:  
          if 'CREF' in self.varname:
             self.file_type='CREF'                                       
          elif 'CB' in self.varname:
             self.file_type='QPE'                                       
          elif 'mosaicked refl' in self.varname:
             self.file_type='mosaicked refl'
                                                                        ## (alon,alat)     (alon+dlon,alat)  
          self.ll_lon=self.alon/self.xy_scale                           ##      +---------------+
          self.ur_lat=self.alat/self.xy_scale                           ##      |               |
          self.ur_lon=self.ll_lon+self.dx/self.dxy_scale*(self.nx-1)    ##      |               |  alon=dy/dxy*(ny-1)
          self.ll_lat=self.ur_lat-self.dy/self.dxy_scale*(self.ny-1)    ##      |               |  alat=dx/dxy*(nx-1)
          self.lon_1d = np.linspace(self.ll_lon, self.ur_lon, self.nx)  ##      |               |
          self.lat_1d = np.linspace(self.ll_lat, self.ur_lat, self.ny)  ##      |               |
          self.lat, self.lon= np.meshgrid(self.lat_1d,self.lon_1d)      ##      +---------------+
                                                                        ## (alon,alat-dlat)  (alon+dlon,alat-dlat)   
        if self.nz>1 :
           self.data=(np.reshape(data, (self.nx,self.ny,self.nz), order='F'))
        else:   
           self.data=(np.reshape(data, (self.nx,self.ny), order='F'))
        
        return self
    
    def readcfrad(self, sweep="sweep_0"):
        
        radar = xr.open_dataset(self.file, group=sweep, engine="cfradial1")
        radar = radar.xradar.georeference()
        # print(radar)
        proj_crs = xd.georeference.get_crs(radar)
        cart_crs = ccrs.Projection(proj_crs)

        lat_0, lon_0 = radar.latitude.values, radar.longitude.values
        transformer = Transformer.from_crs(proj_crs, CRS.from_epsg(4326), always_xy=True)
        x_0, y_0 = np.array(radar.x.values), np.array(radar.y.values)
        lon_g, lat_g = transformer.transform(x_0 + lon_0, y_0 + lat_0)
        
        self.radar = radar
        self.lat   = lat_g
        self.lon   = lon_g

        return self
    
    def readcfradRHI(self, sweep="sween_0", var="DBZ"):

        radar = xr.open_dataset(self.file, group=sweep, engine="cfradial1")

        R     = radar.range.values
        elev  = radar.elevation.values
        az    = radar.azimuth.values

        R     = self._interpolate_range_edges(R)
        elev  = self._interpolate_elevation_edges(elev)
        az    = self._interpolate_azimuth_edges(az)

        x, y, z = self.polar_to_cartesian(R, elev, az)

        angle= radar.sweep_fixed_angle.values
        data = radar[var].values
        DBZ  = radar['DBZ'].values
        
        if (89.5 <= angle <= 90.0) or (269.0 <= angle <= 271.0):
            R = np.sqrt(x**2 + y**2) * np.sign(x)
        else:
            R = np.sqrt(x**2 + y**2) * np.sign(y)
        reverse_xaxis = None
        if reverse_xaxis is None:
            # reverse if all distances are nearly negative (allow up to 1 m)
            reverse_xaxis = np.all(R < 1.0)
        if reverse_xaxis:
            R = -R
        
        # mask_detect_dBZ = (R > 120) | (z < 2)
        # mask_detect_dBZ = mask_detect_dBZ[0:-1, :].T
        # data_detect = np.copy(DBZ)
        # data_detect[mask_detect_dBZ] = np.nan
        # mask_above_40 = data_detect >= 40
        # R_has_dBZ_40 = np.any(mask_above_40, axis=0)
        # data[:, ~R_has_dBZ_40] = np.nan

        data[DBZ < 0] = np.nan

        # mask = (R > 120) | (z > 17)
        # R[R > 120] = np.nan
        # z[z > 16]  = np.nan
        # mask       = mask[0:-1, :].T
        # data[mask] = np.nan

        # self.data = data
        
        # self.R    = R.T
        # self.z    = z.T
        
        return RHIData(data, R.T, z.T, angle)
        

    def readSPolgrid(self, alt=None, CVon=True, all_data=False, CVheight=2, profile_on=False, start_point=None, end_point=None):
        
        ds  = xr.open_dataset(self.file, engine="netcdf4")

        lat = ds.y0.values
        lon = ds.x0.values
        elev= ds.z0.values

        if all_data:
            # lon_min, lon_max = 120.30, 121.20
            # lat_min, lat_max = 23.8, 25.2
            # ds = ds.where(
            #     (ds.x0 >= lon_min) & (ds.x0 <= lon_max) &
            #     (ds.y0 >= lat_min) & (ds.y0 <= lat_max),
            #     drop=True
            # )
            return ds

        if profile_on:
            start_lat = start_point[0]
            start_lon = start_point[1]
            end_lat   = end_point[0]
            end_lon   = end_point[1]

            num_points= 100

            lats      = np.linspace(start_lat, end_lat, num_points)
            lons      = np.linspace(start_lon, end_lon, num_points)
            
            # xarray interp for profile
            ds        = ds.interp(y0=("points", lats), x0=("points", lons))
            
            return ds
        elif CVon:
            DBZ_m = ds["DBZ"].values[0]
            # CV    = np.nanmax(DBZ_m[4::, :, :], axis=0)
            CV    = np.nanmax(DBZ_m[4::, :, :], axis=0)
            self.data = CV
            self.lat  = lat
            self.lon  = lon
            self.elev = elev

            return self 
        else:
            ds    = ds.sel(z0=alt)
            CV    = ds["DBZ"].values[0]

            self.data = CV
            self.lat  = lat
            self.lon  = lon
            self.elev = elev

            return self 
    def readwindprof_nc(self):

        ds = xr.open_dataset(self.file, engine="netcdf4")

        # 設定正確的日期和時間範圍
        start_time = np.datetime64("2022-06-29T14:00")
        end_time = np.datetime64("2022-06-29T20:00")

        # 過濾時間範圍（每 10 分鐘）
        ds = ds.sel(time=slice(start_time, end_time)).resample(time="10min").nearest()

        # 限制高度範圍
        # ht_levels = np.arange(250, 7001, 300)
        # ds = ds.sel(ht=ht_levels, method="nearest")  
        print(ds)    
        
        
        return ds
    
    def readwretrie_nc(self, altitude=None, profile_on=False, start_point=None, end_point=None, mask_CN=False, dn=None):
        
        ds  = xr.open_dataset(self.file, engine="netcdf4")
        ds  = ds.where(ds.DBZ > 0)
        
        SR_U = ds.U.values - U_matrix_3D
        SR_V = ds.V.values - V_matrix_3D
        SR_WS= np.sqrt(SR_U ** 2 + SR_V ** 2)

        dudx = ds.DUDX.values
        dvdy = ds.DVDY.values
        DIV  = dudx + dvdy
        U_hvor = (ds.DWDY.values - ds.DVDZ.values)/100
        V_hvor = (ds.DUDZ.values - ds.DWDX.values)/100

        ds["DIV"]  = (("time", "altitude", "latitude", "longitude"), DIV)
        ds["SR_U"] = (("time", "altitude", "latitude", "longitude"), SR_U)
        ds["SR_V"] = (("time", "altitude", "latitude", "longitude"), SR_V)
        ds["SR_WS"] = (("time", "altitude", "latitude", "longitude"), SR_WS)

        HAD, VAD, STR, TLT, vor = calvorticity(ds)

        ds['HAD']  = (("time", "altitude", "latitude", "longitude"), HAD) # 10e-6
        ds['VAD']  = (("time", "altitude", "latitude", "longitude"), VAD) # 10e-6
        ds['STR']  = (("time", "altitude", "latitude", "longitude"), STR) # 10e-6
        ds['TLT']  = (("time", "altitude", "latitude", "longitude"), TLT) # 10e-6
        ds['VOR']  = (("time", "altitude", "latitude", "longitude"), vor) # 10e-6
        ds['UVOR'] =(("time", "altitude", "latitude", "longitude"), U_hvor) #10e-3
        ds['VVOR'] =(("time", "altitude", "latitude", "longitude"), V_hvor) #10e-3
        
        if mask_CN:

            dnn = dn    
            ds  = mask_ds_by_condition_number(ds=ds, dnn=dnn)


        if profile_on:
            start_lat = start_point[0]
            start_lon = start_point[1]
            end_lat   = end_point[0]
            end_lon   = end_point[1]

            num_points= 100

            lats      = np.linspace(start_lat, end_lat, num_points)
            lons      = np.linspace(start_lon, end_lon, num_points)
            
            # xarray interp for profile
            # ds = ds.sel(
            #     latitude=xr.DataArray(lats, dims="points"),
            #     longitude=xr.DataArray(lons, dims="points"),
            #     method="nearest",
            # )
            ds        = ds.interp(latitude=("points", lats), longitude=("points", lons))
            ds = ds.interpolate_na(dim="altitude", method="linear",max_gap=5)
            # ds = ds.interpolate_na(dim="latitude", method="linear",max_gap=10, fill_value="extrapolate")
            # ds = ds.interpolate_na(dim="longitude", method="linear",max_gap=10, fill_value="extrapolate")
            SPol = (24.8190879821777, 120.90746307373)
            distances = np.array([geodesic(SPol, (lat, lon)).km for lat, lon in zip(lats, lons)])

            # 建立 Z_plot
            R_plot = np.tile(distances, (ds.altitude.shape[0], 1))
            
        elif altitude is not None:
            
            ds        = ds.sel(altitude=altitude)
            # return ds
        
            lon_min, lon_max, lat_min, lat_max = (120.20, 121.20, 23.80, 25.20)
            ds = ds.sel(
                    longitude=slice(lon_min, lon_max+1),
                    latitude=slice(lat_min, lat_max+1),
                )

        return ds#, R_plot

    def readfractl_nc(self, altitude=None, profile_on=False, start_point=None, end_point=None):
        
        ds  = xr.open_dataset(self.file, engine="netcdf4")
        ds  = ds.where(ds.DBZ > 0)
        
        if profile_on:
            start_lat = start_point[0]
            start_lon = start_point[1]
            end_lat   = end_point[0]
            end_lon   = end_point[1]

            num_points= 100

            lats      = np.linspace(start_lat, end_lat, num_points)
            lons      = np.linspace(start_lon, end_lon, num_points)
            
            # xarray interp for profile
            # ds = ds.sel(
            #     latitude=xr.DataArray(lats, dims="points"),
            #     longitude=xr.DataArray(lons, dims="points"),
            #     method="nearest",
            # )
            ds        = ds.interp(latitude=("points", lats), longitude=("points", lons))
            ds = ds.interpolate_na(dim="altitude", method="linear",max_gap=5)
            # ds = ds.interpolate_na(dim="latitude", method="linear",max_gap=10, fill_value="extrapolate")
            # ds = ds.interpolate_na(dim="longitude", method="linear",max_gap=10, fill_value="extrapolate")
            SPol = (24.8190879821777, 120.90746307373)
            distances = np.array([geodesic(SPol, (lat, lon)).km for lat, lon in zip(lats, lons)])

            # 建立 Z_plot
            R_plot = np.tile(distances, (ds.altitude.shape[0], 1))
            
        elif altitude is not None:
            
            ds        = ds.sel(z0=altitude)
            # print(ds)
            # return ds

        return ds#, R_plot
    
    def polar_to_cartesian(self, R_un, elev, az):
        """
        將雷達的極座標轉換為笛卡爾座標，資料形狀為 (212, 1999)。

        :param R: numpy array, 雷達量測範圍 (meters)，形狀為 (1999,)
        :param elev: numpy array, 仰角 (degrees)，形狀為 (212,)
        :param az: numpy array, 方位角 (degrees)，形狀為 (212,)
        :return: x, y, z 笛卡爾座標 (numpy arrays, 形狀為 (212, 1999))
        """
        # 創建範圍和仰角的網格
        elevations, ranges = np.meshgrid(elev, R_un/1000)
        azimuths, _        = np.meshgrid(az, R_un/1000)
        
        # 將角度從度轉換為弧度
        theta_e = np.deg2rad(elevations)  # elevation angle in radians.
        theta_a = np.deg2rad(azimuths)  # azimuth angle in radians.
        R = 6371.0 * 1000.0 * 4.0 / 3.0  # effective radius of earth in meters.
        r = ranges * 1000.0  # distances to gates in meters.

        z = (r**2 + R**2 + 2.0 * r * R * np.sin(theta_e)) ** 0.5 - R
        s = R * np.arcsin(r * np.cos(theta_e) / (R + z))  # arc length in m.
        x = s * np.sin(theta_a)
        y = s * np.cos(theta_a)
        
        return x[:, :-1]/1000, y[:, :-1]/1000, z[:, :-1]/1000
    
    def _interpolate_range_edges(self, ranges):
        """Interpolate the edges of the range gates from their centers."""
        edges = np.empty((ranges.shape[0] + 1,), dtype=ranges.dtype)
        edges[1:-1] = (ranges[:-1] + ranges[1:]) / 2.0
        edges[0] = ranges[0] - (ranges[1] - ranges[0]) / 2.0
        edges[-1] = ranges[-1] - (ranges[-2] - ranges[-1]) / 2.0
        edges[edges < 0] = 0  # do not allow range to become negative
        return edges


    def _interpolate_elevation_edges(self, elevations):
        """Interpolate the edges of the elevation angles from their centers."""
        edges = np.empty((elevations.shape[0] + 1,), dtype=elevations.dtype)
        edges[1:-1] = (elevations[:-1] + elevations[1:]) / 2.0
        edges[0] = elevations[0] - (elevations[1] - elevations[0]) / 2.0
        edges[-1] = elevations[-1] - (elevations[-2] - elevations[-1]) / 2.0
        edges[edges > 180] = 180.0  # prevent angles from going below horizon
        edges[edges < 0] = 0.0
        return edges


    def _interpolate_azimuth_edges(self, azimuths):
        """Interpolate the edges of the azimuth angles from their centers."""
        edges = np.empty((azimuths.shape[0] + 1,), dtype=azimuths.dtype)
        # perform interpolation and extrapolation in complex plane to
        # account for periodic nature of azimuth angle.
        azimuths = np.exp(1.0j * np.deg2rad(azimuths))

        edges[1:-1] = np.angle(azimuths[1:] + azimuths[:-1], deg=True)

        half_angle = self._half_angle_complex(azimuths[0], azimuths[1])
        edges[0] = (np.angle(azimuths[0], deg=True) - half_angle) % 360.0

        half_angle = self._half_angle_complex(azimuths[-1], azimuths[-2])
        edges[-1] = (np.angle(azimuths[-1], deg=True) + half_angle) % 360.0

        edges[edges < 0] += 360  # range from [-180, 180] to [0, 360]
        return edges


    def _half_angle_complex(self, complex_angle1, complex_angle2):
        """
        Return half the angle between complex numbers on the unit circle.

        Parameters
        ----------
        complex_angle1, complex_angle2 : complex
            Complex numbers representing unit vectors on the unit circle

        Returns
        -------
        half_angle : float
            Half the angle between the unit vectors in degrees.

        """
        dot_product = np.real(complex_angle1 * np.conj(complex_angle2))
        if dot_product > 1:
            # warnings.warn("dot_product is larger than one.")
            dot_product = 1.0
        full_angle_rad = np.arccos(dot_product)
        half_angle_rad = full_angle_rad / 2.0
        half_angle_deg = np.rad2deg(half_angle_rad)
        return half_angle_deg
        
class RHIData:
    def __init__(self, data, R, z, angle):
        self.data = data
        self.R = R
        self.z = z
        self.angle = angle

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