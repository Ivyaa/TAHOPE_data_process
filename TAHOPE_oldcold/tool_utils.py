import re
import numpy as np

from datetime    import datetime, timedelta
from othsettings import patterns
from pathconfig  import *
# from read_utils  import get_terrain

# scipy
from scipy.spatial import cKDTree
from scipy.interpolate import griddata

# metpy
from metpy.interpolate import natural_neighbor_to_grid
from metpy.calc import wind_components, mixing_ratio_from_relative_humidity, vapor_pressure, dewpoint
from metpy.calc import dewpoint_from_relative_humidity, relative_humidity_from_dewpoint, divergence
from metpy.calc import lat_lon_grid_deltas, potential_temperature, equivalent_potential_temperature
from metpy.calc import wind_direction, wind_speed
from metpy.units import units

# geopy
from geopy.distance import geodesic

# convert utc to lst
def utc2lst(filename):
    '''
    if you need add new type of time patterns
    you can add them to othsettins.py [patterns]
    '''    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.groups()) == 2:  # 處理像 20220629.0000 的格式
                date_part = match.group(1)
                time_part = match.group(2)
                try:
                    time_obj = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
                    time_obj = time_obj + timedelta(hours=8)
                    return time_obj.strftime("%H%M")
                except ValueError:
                    continue
            if len(match.groups()) > 3:
                date1, time1 = match.group(1), match.group(2)
                date2, time2 = match.group(3), match.group(4)
                
                # 解析為 datetime 物件
                dt1 = datetime.strptime(date1 + time1, "%Y%m%d%H%M%S")
                dt2 = datetime.strptime(date2 + time2, "%Y%m%d%H%M%S")
                
                # 計算中間時間
                mid_time = dt1 + (dt2 - dt1) / 2
                mid_time = mid_time + timedelta(hours=8)
                
                return mid_time.strftime("%Y-%m-%dT%H:%M")  # 格式化為字符串
            else:
                time_str = match.group(1)
                try:
                    if '_' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d_%H-%M-%S")
                    elif ':' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    elif '-' in time_str or '/' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d")
                    else:
                        time_obj = datetime.strptime(time_str, "%Y%m%d%H%M")
                    
                    time_obj = time_obj + timedelta(hours=8)
                    return time_obj.strftime("%H%M")
                except ValueError:
                    continue
    
    print("No valid date or time found in filename.")
    return None

def get_closest_obs_file(target_file, obs_files):
    """
    找到與目標檔案時間最近的觀測檔案。
    
    :param target_file: 網格檔案名
    :param obs_files: 所有觀測檔案的列表
    :return: 最近的觀測檔案名
    """
    target_time = datetime.strptime(utc2lst(str(target_file)), "%H%M")
    min_diff = float('inf')
    closest_file = None

    for obs_file in obs_files:
        obs_time_str = utc2lst(str(obs_file))
        obs_time = datetime.strptime(obs_time_str, "%H%M")
        time_diff = abs((obs_time - target_time).total_seconds())

        if time_diff < min_diff:
            min_diff = time_diff
            closest_file = obs_file

    return closest_file

def get_potential_temp(df):

    Temp = df['TEMP'].values + 273.15
    Pres = df['PRES'].values
    HUMD = df["HUMD"].values
    Td   =dewpoint_from_relative_humidity((Temp-273.15) * units.degC, HUMD).magnitude

    theta  = potential_temperature(Pres * units.mbar, Temp * units.kelvin)
    thetae = equivalent_potential_temperature(Pres * units.mbar, (Temp-273.15) * units.degC, Td * units.degC) 
    # print(theta)
    df['Potential_temp'] = theta
    df['Equivalent_potemp'] = thetae

    return df



def filter_files_by_time(files, start_time="0200", end_time="1300"):
    """
    過濾符合時間範圍的檔案。

    Parameters:
    - files (list): 檔案名列表
    - start_time (str): 開始時間 (格式為 HHMM)
    - end_time (str): 結束時間 (格式為 HHMM)

    Returns:
    - list: 符合條件的檔案名列表
    """
    filtered_files = []
    pattern = r"_(\d{6})\.\d+_to_"

    for file in files:
        match = re.search(pattern, file)
        if match:
            time = match.group(1)[:4]  # 提取掃描時間的 HHMM 部分
            if start_time <= time <= end_time:
                filtered_files.append(file)

    return filtered_files

import math

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing (azimuth) between two GPS points.
    
    Args:
        lat1, lon1: Latitude and longitude of the first point (in degrees).
        lat2, lon2: Latitude and longitude of the second point (in degrees).

    Returns:
        Bearing in degrees, measured clockwise from north.
    """
    # Convert degrees to radians
    rad_lat1 = math.radians(lat1)
    rad_lon1 = math.radians(lon1)
    rad_lat2 = math.radians(lat2)
    rad_lon2 = math.radians(lon2)

    # Calculate the difference in longitude
    dlon = rad_lon2 - rad_lon1

    # Calculate the components of the bearing
    y = math.sin(dlon) * math.cos(rad_lat2)
    x = math.cos(rad_lat1) * math.sin(rad_lat2) - math.sin(rad_lat1) * math.cos(rad_lat2) * math.cos(dlon)

    # Convert to degrees and normalize to 0-360
    initial_bearing = math.degrees(math.atan2(y, x))
    bearing = (initial_bearing + 360) % 360

    return bearing


# obj_analysis needing
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
terrain = get_terrain(TERRAIN)
# calculate SLP
def calculate_pslv(P, H, T):
    M = H / (18400 * (1 + (T / 273.15)))
    PSLV = P * (10 ** M)
    return PSLV

# calculate R and Te
def calculate_Te_T_R(PSLV, P, T, H):
    Te_T = (T + 273.15) * (PSLV*100 / (P*100)) ** 0.286

    if H == 0:
        R = 0
    else:
        R = (T + 273.15 - Te_T) / H
    return Te_T, R

def nature_neighbor(known_points, known_values, target_lat, target_lon, grid_points=60):

    lat_min, lat_max = np.min(target_lat), np.max(target_lat)
    lon_min, lon_max = np.min(target_lon), np.max(target_lon)

    grid_lon = np.array(np.linspace(lon_min, lon_max, grid_points)) # 100個網格點
    grid_lat = np.array(np.linspace(lat_min, lat_max, grid_points))

    grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)
    # print(known_points[:, 1], known_points[:, 0])
    # print(known_values)
    nn_interp = natural_neighbor_to_grid(known_points[:, 0], known_points[:, 1], known_values, grid_lat, grid_lon)

    return np.array(nn_interp), grid_lat, grid_lon

# objective analysis(df only 1 hr)
def obj_analysis(df, target_lat=[24.35, 25.10], target_lon=[120.65, 121.50]):

    latitudes    = df['LAT'].values
    longitudes   = df['LON'].values
    pressures    = df['PRES'].values
    temperatures = df['TEMP'].values
    RH           = df['HUMD'].values
    elevations   = df['ELEV'].values
    
    # WS15M WD15M
    u, v = wind_components(df['WS15M'].values * units('m/s'), df['WD15M'].values * units.deg)
    q    = mixing_ratio_from_relative_humidity(pressures * units.hPa, temperatures * units.degC, RH).to('g/kg').magnitude
    Td_up= np.array(dewpoint_from_relative_humidity(temperatures * units.degC, RH).magnitude)

    # 計算海平面氣壓、相當溫度、溫度遞減率
    PSLV_values = []
    Te_T_values = []
    R_values = []
    for P, T, H in zip(pressures, temperatures, elevations):
        PSLV = calculate_pslv(P, H, T)
        PSLV_values.append(PSLV)
        
        Te_T, R = calculate_Te_T_R(PSLV, P, T, H)
        Te_T_values.append(Te_T)
        R_values.append(R)
    
    Te_T_values = np.array(Te_T_values)
    R_values    = np.array(R_values)
    PSLV_values = np.array(PSLV_values)
    e           = vapor_pressure(PSLV_values * units.hPa, q * units('g/kg'))
    Td_bottom   = np.array(dewpoint(e).magnitude)

    R_Td_values = np.where(elevations != 0, (Td_up - Td_bottom) / elevations, 0)
    
    # 將資料轉成經緯度和相當溫度、溫度遞減率的點集
    known_points = np.array(list(zip(latitudes, longitudes)))
    # target_lat = [24.35, 25.10]; target_lon = [120.65, 121.50]
    # target_lat = [24.30, 25.10]; target_lon = [120.65, 121.65]
    Te_T_interp, grid_lat, grid_lon = nature_neighbor(known_points, Te_T_values, target_lat, target_lon)
    Td_bottom_interp, _, _          = nature_neighbor(known_points, Td_bottom, target_lat, target_lon)
    R_interp, _, _                  = nature_neighbor(known_points, R_values, target_lat, target_lon)
    R_Td_interp,_,_                 = nature_neighbor(known_points, R_Td_values, target_lat, target_lon)
    
    grid_elevations                 = findSTAheight2D(grid_lat, grid_lon)
    T_interp                        = R_interp * grid_elevations + Te_T_interp
    Td_interp                       = R_Td_interp * grid_elevations + Td_bottom_interp

    # print(Td_interp)
    # u_interp, grid_lat, grid_lon    = nature_neighbor(known_points, u, target_lat, target_lon)
    # v_interp, grid_lat, grid_lon    = nature_neighbor(known_points, v, target_lat, target_lon)

    # p_interp, grid_lat, grid_lon      = nature_neighbor(known_points, pressures, target_lat, target_lon)

    # print(Te_T_interp, grid_lat, grid_lon)
    # mask the the space
    mask = filter_points_by_station_proximity(grid_lat, grid_lon, latitudes, longitudes, radius_km=15)
    T_filtered  = np.where(mask, T_interp, np.nan)
    Td_filtered = np.where(mask, Td_interp, np.nan)

    # p_filtered  = np.where(mask, p_interp, np.nan)

    # u_filtered = np.where(mask, u_interp, np.nan)
    # v_filtered = np.where(mask, v_interp, np.nan)

    return T_filtered, Td_filtered, q, u, v, grid_lat, grid_lon, grid_elevations

def findSTAheight2D(lat_matrix, lon_matrix):
    """
    查找給定網格點的地形高度，利用 KD-Tree 加速最近鄰查找。

    參數:
    - lat_matrix, lon_matrix (2D array): 網格點的緯度和經度。
    - terrain_lat, terrain_lon (1D array): 地形資料的緯度和經度。
    - terrain_data (2D array): 對應的地形高度。

    回傳:
    - height_matrix (2D array): 對應的高度矩陣。
    """
    # 將地形資料展平，構建 KD-Tree
    terrain_coords = np.vstack([terrain.lat.ravel(), terrain.lon.ravel()]).T
    tree = cKDTree(terrain_coords)
    
    # 將網格點展平，批量查找最近鄰
    grid_coords = np.vstack([lat_matrix.ravel(), lon_matrix.ravel()]).T
    _, indices = tree.query(grid_coords)  # 查找最近地形點的索引
    
    # 對應的高度值
    height_flat = terrain.data.ravel()[indices]
    
    # 將結果重新整形回原始網格形狀
    height_matrix = height_flat.reshape(lat_matrix.shape).astype(float)
    height_matrix[height_matrix < 0] = np.nan  # 將負高度設為 NaN
    
    return height_matrix

def haversine(lat1, lon1, lat2, lon2):
    """計算兩點之間的球面距離，輸入緯度和經度以度為單位"""
    R = 6371  # 地球半徑 (km)
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def filter_points_by_station_proximity(grid_lat, grid_lon, station_lats, station_lons, radius_km=5):
    """
    根據測站分布檢查網格點，如果在 radius_km 範圍內無測站，將其標記為 np.nan。

    使用向量化運算加速距離計算，處理 2D 網格。
    """
    # 展平 2D 網格到 1D
    grid_lat_flat = grid_lat.flatten()
    grid_lon_flat = grid_lon.flatten()

    # 初始化布爾遮罩 (1D)
    mask_flat = np.zeros_like(grid_lat_flat, dtype=bool)

    for lat, lon in zip(station_lats, station_lons):
        # 計算每個網格點到該測站的距離
        distances = haversine(grid_lat_flat, grid_lon_flat, lat, lon)

        # 更新遮罩，將距離小於 radius_km 的點設為有效 (True)
        mask_flat = mask_flat | (distances <= radius_km)

    # 將 1D 遮罩恢復為原來的 2D 網格形狀
    mask = mask_flat.reshape(grid_lat.shape)

    return mask

def append_or_fill(data_list, value):
    """
    如果值為空，添加 np.nan；否則添加數據值。
    """
    if len(value) == 0:
        data_list.append(np.array(np.nan))
    else:
        data_list.append(value)

omega = 7.2921e-5 
latitude = 24.3 
latitude_rad = math.radians(latitude)
f = 2 * omega * math.sin(latitude_rad)
f = 6.0016077e-5 # units: s-1
def calvorticity(ds):

    vor = (-ds.DUDY.values + ds.DVDX.values) * (10 ** -5)
    HAD = ds.SR_U.values * forth_cent_diff(var=vor, dx=1) + ds.SR_V.values * forth_cent_diff(var=vor, dy=1)
    VAD = ds.W.values * forth_cent_diff(var=vor, dz=0.5)
    STR = (f + vor) * (ds.DUDX.values * (10 ** -5) + ds.DVDY.values * (10 ** -5))
    TLT = ds.DWDX.values * (10 ** -5) * ds.DVDZ.values * (10 ** -5) - ds.DWDY.values * (10 ** -5) * ds.DUDZ.values * (10 ** -5)
    # print(np.nanmax(vor), np.nanmax(HAD), np.nanmax(VAD), np.nanmax(STR), np.nanmax(STR), np.nanmax(TLT))
    return HAD * 10 ** 6, VAD * 10 ** 6, STR * 10 ** 6 , TLT * 10 ** 6, vor * 10 ** 6

def calrotationalwind(dw, u, v, dx=1000, tol=1e-6):

    vor = np.nan_to_num(dw.VOR.values[0] / 1000000, nan=0.0)
    extented_psi = np.zeros((vor.shape[0]+2, vor.shape[1]+2))

    diff = 9999
    i = 0
    while diff > tol:
        if i%50000 == 0 and i > 0:
            print(i, diff)
        psi  = (extented_psi[:-2,1:-1] + extented_psi[2:,1:-1] + extented_psi[1:-1,:-2] + extented_psi[1:-1,2:] - dx**2 * vor) / 4
        diff = np.nanmax(np.abs(extented_psi[1:-1, 1:-1] - psi))
        extented_psi[1:-1, 1:-1] = psi
        i += 1

    check = (extented_psi[:-2,1:-1] + extented_psi[2:,1:-1] + extented_psi[1:-1,:-2] + extented_psi[1:-1,2:]  - 4 * psi) / dx**2
    rotation_u = -((psi[:, 1::] - psi[:, 0:-1]) / 2000)
    rotation_v = (psi[1::, :] - psi[0:-1, :]) / 2000

    return rotation_u[0:-1, :], rotation_v[:, 0:-1]

def forth_cent_diff(var, dx=None, dy=None, dz=None):
    if dx is not None:
        dvardx                = np.zeros_like(var)
        dvardx[:, :, :, 2:-2] = 4/3 * (var[:, :, :, 3:-1]-var[:, :, :,1:-3]) / 2000 - 1/3 * (var[:, :, :, 4::]-var[:, :, :, 0:-4]) / 4000
        dvardx[:, :, :, 1]    = (var[:, :, :, 2] - var[:, :, :, 0]) / 2000
        dvardx[:, :, :, -2]   = (var[:, :, :, -1] - var[:, :, :, -3]) / 2000
        # dvardx[:, :, :, 1:-1] = (var[:, :, :, 2::]-var[:, :, :, 0:-2]) / 2000
        dvardx[:, :, :, 0]    = (var[:, :, :, 1] - var[:, :, :, 0]) / 1000
        dvardx[:, :, :, -1]   = (var[:, :, :, -1] - var[:, :, :, -2]) / 1000
        # print(np.nanmax(dvardx))
        return np.array(dvardx)
    elif dy is not None:
        dvardy                = np.zeros_like(var)
        dvardy[:, :, 2:-2, :] = 4/3 * (var[:, :, 3:-1, :]-var[:, :, 1:-3, :]) / 2000 - 1/3 * (var[:, :, 4::, :]-var[:, :, 0:-4, :]) / 4000
        dvardy[:, :, 1, :]    = (var[:, :, 2, :] - var[:, :, 0, :]) / 2000
        dvardy[:, :, -2, :]   = (var[:, :, -1, :] - var[:, :, -3, :]) / 2000
        # dvardy[:, :, 1:-1, :] = (var[:, :, 2::, :]-var[:, :, 0:-2, :]) / 2000
        dvardy[:, :, 0, :]    = (var[:, :, 1, :] - var[:, :, 0, :]) / 1000
        dvardy[:, :, -1, :]   = (var[:, :, -1, :] - var[:, :, -2, :]) / 1000
        # print(np.nanmax(dvardy))
        return np.array(dvardy)
    elif dz is not None:
        dvardz                = np.zeros_like(var)
        dvardz[:, 1:-1, :, :] = (var[:, 2::, :, :] - var[:, 0:-2, :, :]) / 1000
        dvardz[:, 0, :, :]    = (var[:, 1, :, :] - var[:, 0, :, :]) / 500
        dvardz[:, -1, :, :]   = (var[:, -1, :, :] - var[:, -2, :, :]) / 500
        # print(np.nanmax(dvardz))
        return np.array(dvardz)


def classificationofCuSt(lat, lon, data):
    # 地球半徑 (km)
    R = 6371

    # 確保 lon 和 lat 是 1D 陣列
    lat = np.asarray(lat)
    lon = np.asarray(lon)

    # 使用 meshgrid 將 lon 和 lat 展開為與 data 一致的 2D 陣列
    lon2d, lat2d = np.meshgrid(lon, lat)

    # 將經緯度轉換為平面坐標
    x = R * np.radians(lon2d) * np.cos(np.radians(lat2d))
    y = R * np.radians(lat2d)

    # 展平座標和數據，用於構建 KDTree
    points = np.column_stack([x.ravel(), y.ravel()])
    data_flat = data.ravel()

    # 構建 KDTree
    tree = cKDTree(points)

    # 初始化結果矩陣
    mask = np.zeros_like(data, dtype=bool)

    # 定義背景回波半徑範圍和對應條件
    radius_ranges = {
        1: (15, 25),
        2: (25, 30),
        3: (30, 35),
        4: (35, 45),
        5: (45, 50),
    }

    # 計算每個點的背景回波
    bg_reflectivity = np.zeros_like(data_flat)
    for idx, point in enumerate(points):
        indices = tree.query_ball_point(point, 11)  # 半徑 11 km

        bg_reflectivity[idx] = np.nanmean(data_flat[indices])
        print(bg_reflectivity)
        if bg_reflectivity[-1] > 15:
            print(bg_reflectivity[-1])
        break
    # 遍歷每個半徑範圍，標記對流區域
    for r, (lower, upper) in radius_ranges.items():
        for idx, point in enumerate(points):
            indices = tree.query_ball_point(point, r)  # 半徑 r km
            mean_ref = bg_reflectivity[idx]
            if mean_ref > 15:
                print(mean_ref)
            if lower <= mean_ref < upper:
                mask.ravel()[indices] = True

    # 加入距離 S-Pol 超過 20 km 的範圍過濾
    s_pol_lat = 24.8190879821777
    s_pol_lon = 120.90746307373
    s_pol_x = R * np.radians(s_pol_lon) * np.cos(np.radians(s_pol_lat))
    s_pol_y = R * np.radians(s_pol_lat)

    # 計算每個點到 S-Pol 的距離
    dist_to_spol = np.sqrt((points[:, 0] - s_pol_x) ** 2 + (points[:, 1] - s_pol_y) ** 2)

    # 找出距離小於 20 km 的點，將這些位置設為 False（不標記）
    mask.ravel()[dist_to_spol < 20] = False

    # 返回標記結果
    return mask.reshape(data.shape)

def steiner_conv_strat_classification(lat, lon, data, mode='small', a=10, b=42.43):
    """
    基於 Steiner et al. (1995) 對回波進行對流/層狀分類
    
    Parameters:
        lat, lon: 1D arrays of latitude and longitude
        data: 2D reflectivity data (dBZ)
        mode: str, one of ['small', 'medium', 'large'], defines convective radius

    Returns:
        convective_mask: Boolean 2D array, True where classified as convective
    """
    
    # 地球半徑 (km)
    R = 6371.0

    # 建立經緯度網格
    lon2d, lat2d = np.meshgrid(lon, lat)

    # 經緯度轉為平面座標 (近似投影)
    x = R * np.radians(lon2d) * np.cos(np.radians(lat2d))
    y = R * np.radians(lat2d)

    # 展平資料
    points = np.column_stack([x.ravel(), y.ravel()])
    data_flat = data.ravel()

    # 建立 KDTree
    tree = cKDTree(points)

    # 初始化背景回波與分類遮罩
    bg_ref = np.full_like(data_flat, np.nan)
    convective_core = np.zeros_like(data_flat, dtype=bool)

    # 計算每個點的背景回波 (11 km 半徑)
    for i, point in enumerate(points):
        indices = tree.query_ball_point(point, 11)
        if len(indices) > 0:
            bg_ref[i] = np.nanmean(data_flat[indices])

    # 用 cosine 函數計算 ΔZ
    with np.errstate(invalid='ignore'):
        delta_Z_thresh = a * np.cos((np.pi * bg_ref) / (2 * b))
        delta_Z_thresh[bg_ref >= b] = 0  # 超過上限則 ΔZ=0
        delta_Z_thresh[bg_ref < 0] = a   # 小於 0 則 ΔZ=a

    # 判斷對流核心點
    with np.errstate(invalid='ignore'):
        convective_core = (data_flat >= 40) #& (data_flat > bg_ref + delta_Z_thresh)

    # 定義對流區擴展半徑（依圖6b模式）
    def get_conv_radius(bg_z):
        if mode == 'large':
            return np.where(bg_z < 20, 5.0, np.where(bg_z < 40, 4.0, 3.0))
        elif mode == 'small':
            return np.where(bg_z < 20, 2.5, np.where(bg_z < 40, 2.0, 1.5))
        else:  # medium (default)
            return np.where(bg_z < 20, 4.0, np.where(bg_z < 40, 3.0, 2.0))

    # 根據對流核心擴展半徑形成 convective mask
    convective_mask = np.zeros_like(data_flat, dtype=bool)
    core_indices = np.where(convective_core)[0]

    for idx in core_indices:
        radius = get_conv_radius(bg_ref[idx])
        neighbors = tree.query_ball_point(points[idx], r=radius)
        convective_mask[neighbors] = True

    # 最終 reshape 回原始 2D 格式
    return convective_mask.reshape(data.shape)

def classify_steiner_3d(reflectivity_3d, z_levels, lat, lon, a=9, b=45):
    """
    根據 Steiner et al. (1995) 方法分類對流 / 層狀 / 弱回波區域，並細分對流型態。
    輸入：
        reflectivity_3d: shape = (nz, ny, nx)，雷達反射率資料 (dBZ)
        z_levels: 高度陣列（km）
        lat, lon: 緯度、經度陣列（一維）
    輸出：
        classification: shape = (ny, nx)，標籤為 'DC', 'MC', 'SC', 'ST', 'WE'
    """
    R_earth = 6371  # km
    nz, ny, nx = reflectivity_3d.shape
    print(reflectivity_3d.shape)

    # 1. 計算每格的最大反射率值
    max_ref = reflectivity_3d[4, :, :]

    # 2. Echo-top height：找每格首次 >=20 dBZ 的高度
    echo_top = np.full((ny, nx), np.nan)
    for j in range(ny):
        for i in range(nx):
            profile = reflectivity_3d[:, j, i]
            above_20 = np.where(profile >= 20)[0]
            if len(above_20) > 0:
                echo_top[j, i] = z_levels[above_20[-1]]
                # if echo_top[j, i] >=10:
                #     print(echo_top[j, i])

    # 3. 經緯度轉平面座標
    lon2d, lat2d = np.meshgrid(lon, lat)
    x = R_earth * np.radians(lon2d) * np.cos(np.radians(lat2d))
    y = R_earth * np.radians(lat2d)
    points = np.column_stack([x.ravel(), y.ravel()])
    max_ref_flat = max_ref.ravel()
    tree = cKDTree(points)

    # 4. 背景反射率 Z_bg（使用 R 計算時，先估一個最大半徑 4 km 掃一遍）
    bg_ref = np.full_like(max_ref_flat, np.nan)
    for i, pt in enumerate(points):
        neighbors = tree.query_ball_point(pt, r=11)  # 依據圖片最大半徑
        if neighbors:
            bg_ref[i] = np.nanmean(max_ref_flat[neighbors])

    # 5. 計算 ΔZ_cc
    with np.errstate(invalid='ignore'):
        delta_z = a * np.cos((np.pi * bg_ref) / (2 * b))
        delta_z[bg_ref >= b] = 0
        delta_z[bg_ref < 0] = a

    # 6. 判斷對流核心點
    core_mask_flat = (max_ref_flat >= 40) | (max_ref_flat > (bg_ref + delta_z))
    core_indices = np.where(core_mask_flat)[0]

    # 7. 依 Z_bg 決定每點的擴展半徑 R
    def get_radius(zbg):
        if zbg < 20:
            return 0.5
        elif zbg < 35:
            return 0.5 + 3.5 * ((zbg - 20) / 15)
        else:
            return 4.0

    # 8. 建立對流區域 mask
    conv_mask_flat = np.zeros_like(max_ref_flat, dtype=bool)
    for idx in core_indices:
        radius = get_radius(bg_ref[idx])
        neighbors = tree.query_ball_point(points[idx], r=radius)
        conv_mask_flat[neighbors] = True
    conv_mask = conv_mask_flat.reshape((ny, nx))

    # 9. 將所有格點分類
    classification = np.full((ny, nx), 'UN', dtype=object)
    for j in range(ny):
        for i in range(nx):
            if conv_mask[j, i]:
                ht = echo_top[j, i]
                if ht is np.nan:
                    classification[j, i] = 'UN'
                elif ht > 10:
                    classification[j, i] = 'DC'
                elif ht >= 5 and ht <= 10:
                    classification[j, i] = 'MC'
                elif ht < 5:
                    classification[j, i] = 'SC'
            else:
                if max_ref[j, i] >= 20:
                    classification[j, i] = 'ST'
                else:
                    classification[j, i] = 'WE'
    return classification


def compute_cfad_percentage(t_var, clevel, dx=1):
    """
    计算CFAD的频率百分比，基于给定的数值区间。
    
    参数:
    - t_var: 输入的时间 × 高度 × 水平 × 50维度的数组 (如: (31, 29, 60, 50))
    - clevel: 用于计算频率的区间列表 (例如：[5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    - dx: 每个区间的宽度 (默认1)
    
    返回:
    - cfad_percentages: 每个区间的频率百分比，形状为 (29, len(clevel) - 1)
    """
    
    # 计算区间的边界
    clevel_edges = np.array(clevel)
    # 计算每个区间的总频率
    cfad_percentages = np.full((t_var.shape[1], len(clevel_edges)-1), np.nan)
    
    # 遍历高度层 (维度1)
    for height_idx in range(t_var.shape[1]):
        # 获取当前高度层的数据
        data_at_height = t_var[:, height_idx, :, :]  # 时间 × 水平 × 50

        # 去除nan值
        data_at_height = np.ma.masked_invalid(data_at_height)

        # 计算每个区间的频率
        for i in range(len(clevel_edges) - 1):
            lower_bound = clevel_edges[i]
            upper_bound = clevel_edges[i + 1]
            
            # 找到在该区间内的值
            in_range = (data_at_height >= lower_bound) & (data_at_height < upper_bound)
            
            # 计算在该区间内的出现频率
            count_in_range = np.sum(in_range, axis=(0, 1, 2))  # 按时间和水平轴统计
            total_count = np.sum(~np.isnan(data_at_height), axis=(0, 1, 2))  # 去除nan的总计数

            # 计算百分比
            if total_count >= 0:
                cfad_percentages[height_idx, i] = (count_in_range / total_count) * 100

    return cfad_percentages

from geopy.distance import distance
from geopy import Point

def find_RHIline(angle, range=120):
    spol_lat = 24.8190879821777
    spol_lon = 120.90746307373

    start_point = Point(spol_lat, spol_lon)
    end_point = distance(kilometers=range).destination(point=start_point, bearing=angle)

    end_lat = end_point.latitude
    end_lon = end_point.longitude

    return end_lat, end_lon


def compute_cfad_percentage_RHI(t_var, z_var, clevel=None, dx=1):
    """
    计算CFAD的频率百分比，基于给定的数值区间。
    
    参数:
    - t_var: 输入的时间 × 高度 × 水平 × 50维度的数组 (如: (31, 29, 60, 50))
    - clevel: 用于计算频率的区间列表 (例如：[5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    - dx: 每个区间的宽度 (默认1)
    
    返回:
    - cfad_percentages: 每个区间的频率百分比，形状为 (29, len(clevel) - 1)
    """
    
    # 计算区间的边界
    clevel_edges = np.array(clevel)
    altitudes    = np.arange(0, 17, 0.5)
    # 计算每个区间的总频率
    cfad_percentages = np.full((len(altitudes), len(clevel_edges)-1), np.nan)
    
    # 遍历高度层 (维度1)
    for height_idx in range(len(altitudes)-1):
        # 获取当前高度层的数据
        height_max = altitudes[height_idx+1]
        height_min = altitudes[height_idx]
        print(height_min, height_max)
        # data_at_height = t_var[:, height_idx, :, :]  # 时间 × 水平 × 50

        # 去除nan值
        t_var = np.array(t_var)  # 確保 t_var 是可索引的
        mask_z = (z_var >= height_max) | (z_var < height_min)
        masked_t_var = np.copy(t_var)
        masked_t_var[mask_z] = np.nan
        data_at_height = np.ma.masked_invalid(masked_t_var)
        # print(np.array(z_var)[mask_z])
        # 计算每个区间的频率
        for i in range(len(clevel_edges) - 1):
            lower_bound = clevel_edges[i]
            upper_bound = clevel_edges[i + 1]
            
            # 找到在该区间内的值
            in_range = (data_at_height >= lower_bound) & (data_at_height < upper_bound)
            
            # 计算在该区间内的出现频率
            count_in_range = np.sum(in_range)  # 按时间和水平轴统计
            total_count = np.sum(~np.isnan(data_at_height))  # 去除nan的总计数

            # 计算百分比
            if total_count >= 0:
                cfad_percentages[height_idx, i] = (count_in_range / total_count) * 100

    return cfad_percentages

def compute_median_profile(R, z, data, r_min, r_max, z_bins=None, percentile=99.9):
    """
    根據距離範圍和高度 bin，計算反射率的中位數垂直剖面

    Parameters
    ----------
    R : np.ndarray
        距離陣列，shape = (n_z, n_r)
    z : np.ndarray
        高度陣列，shape = (n_z, n_r)
    data_DBZ : np.ndarray
        反射率資料，shape = (n_z, n_r)
    r_min : float
        距離下限（km）
    r_max : float
        距離上限（km）
    z_bins : np.ndarray or None
        高度分箱（km），預設為 np.arange(0, 20.5, 0.5)

    Returns
    -------
    z_bin_centers : np.ndarray
        每層高度 bin 的中心高度
    medians : np.ndarray
        每層高度 bin 中的反射率中位數（dBZ）
    """
    if z_bins is None:
        z_bins = np.arange(0, 20.5, 0.5)

    # Step 1: 選定距離區間的 mask
    mask_range = (R >= r_min) & (R < r_max)

    # Step 2: 拉平後過濾高度 & dBZ
    z_flat = z[mask_range]
    data_flat = data[mask_range]

    # Step 3: 對每個 z-bin 計算中位數
    medians = []
    for i in range(len(z_bins) - 1):
        zmin = z_bins[i]
        zmax = z_bins[i+1]
        mask_z = (z_flat >= zmin) & (z_flat < zmax)
        if np.any(mask_z):
            # medians.append(np.nanmedian(data_flat[mask_z]))
            medians.append(np.nanpercentile(data_flat[mask_z], percentile))
        else:
            medians.append(np.nan)

    z_bin_centers = (z_bins[:-1] + z_bins[1:]) / 2
    return z_bins, np.array(medians)

def gridding_data(target_lat, target_lon, origin_lat, origin_lon, origin_data):

    # 先將原始資料中的 nan 改成 -999
    origin_data_filled = np.where(np.isnan(origin_data), -999, origin_data)

    valid_mask = (origin_data_filled != -999) & ~np.isnan(origin_lat) & ~np.isnan(origin_lon)
    points = np.column_stack((
        origin_lat[valid_mask].ravel(),
        origin_lon[valid_mask].ravel()
    ))
    values = origin_data_filled[valid_mask].ravel()

    # 產生目標格點 (dw 是 1D 緯經度)
    lon_grid, lat_grid = np.meshgrid(target_lon, target_lat)

    # 內插
    interp_flat = griddata(points, values, (lat_grid, lon_grid), method='nearest')

    # 將 -999 改回 np.nan
    interp_flat[interp_flat == -999] = np.nan
    interp_data = interp_flat.reshape(lat_grid.shape)

    return interp_data

def mask_ds_by_condition_number(ds, dnn):
    """
    將 dnn.conditionNumber 插值到 ds 的格點，並對所有變數在 conditionNumber > 10 的位置進行遮蔽。
    這個版本假設 ds 和 dnn 有相同的高度層。
    """
    # 取得高度、經緯度資訊
    nz = len(dnn.z0)
    ny, nx = dnn.y0.size, dnn.x0.size

    origin_lat = dnn.lat0.values[:, :, 0, :].transpose(2, 0, 1)  # (z, y, x)
    origin_lon = dnn.lon0.values[:, :, 0, :].transpose(2, 0, 1)
    origin_cn = dnn.conditionNumber.values[0]  # (z, y, x)
    
    target_lat = ds.latitude.values  # (lat,)
    target_lon = ds.longitude.values  # (lon,)
    lon_grid, lat_grid = np.meshgrid(target_lon, target_lat)  # (lat, lon)

    # 建立最終 3D mask (nz, lat, lon)
    cn_mask_3d = np.zeros((nz, len(target_lat), len(target_lon)), dtype=bool)

    for k in range(nz):
        # 每層處理一次
        lat_k = origin_lat[k]
        lon_k = origin_lon[k]
        cn_k = origin_cn[k]

        # nan 替換為 -999，方便插值
        cn_k_filled = np.where(np.isnan(cn_k), -999, cn_k)
        valid_mask = (cn_k_filled != -999) & ~np.isnan(lat_k) & ~np.isnan(lon_k)

        if not np.any(valid_mask):
            cn_mask_3d[k] = False  # 全部有效
            continue

        points = np.column_stack((lat_k[valid_mask].ravel(), lon_k[valid_mask].ravel()))
        values = cn_k_filled[valid_mask].ravel()

        interp_cn = griddata(points, values, (lat_grid, lon_grid), method='nearest')
        interp_cn[interp_cn == -999] = np.nan

        cn_mask_3d[k] = interp_cn > 10

    # 將 mask 套用到 ds 所有變數 (time, altitude, latitude, longitude)
    for var in ds.data_vars:
        if var == "x" or var == "y":
            continue
        if ds[var].ndim == 4:
            data = ds[var].values  # (time, z, lat, lon)
            mask_4d = np.broadcast_to(cn_mask_3d, data.shape)
            ds[var].values = np.where(mask_4d, np.nan, data)

    return ds



    pass



def winddirspd(u, v):

    wdir = wind_direction(u * units('m/s'), v * units('m/s'))
    wspd = wind_speed(u * units('m/s'), v * units('m/s'))

    return wspd, wdir

# only use for Cdir < 180 degree
def findnormalwindspeed(shearwdir, shearwspd, Cdir=141.62):

    normal_wspd = []  # 存放計算結果

    for wdir, wspd in zip(shearwdir, shearwspd):  # 確保 wdir 和 wspd 對應

        if wdir.values >= 180.0:
            Cnew = 180.0 - Cdir
            theta = Cnew + wdir.values - 180.0
        else:
            theta = Cdir - wdir.values
        
        # 轉換角度為弧度
        theta_rad = np.radians(theta)

        # 計算 normal wind speed
        normal_wspd.append(wspd * np.cos(theta_rad))

    return np.abs(np.array(normal_wspd))

def deformation_horizontal_vor(uvor, vvor, theta_deg=132.27):

    # theta_deg = 47.73
    theta_rad = np.radians(theta_deg)

    uvor_newaxis = np.cos(theta_rad) * uvor + np.sin(theta_rad) * vvor  # 新的 x' 方向 (垂直剖線)
    vvor_newaxis = -np.sin(theta_rad) * uvor + np.cos(theta_rad) * vvor  # 新的 y' 方向 (沿剖線)

    return uvor_newaxis, vvor_newaxis


import imageio.v3 as iio
import os

def GIFmake(input_folder, output_gif, duration):
    """
    创建一个 GIF 动画
    :param input_folder: 存放图像文件的文件夹路径
    :param output_gif: 输出 GIF 文件路径
    :param duration: 每帧的持续时间（秒）
    """
    images = []
    for file_name in sorted(os.listdir(input_folder)):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(input_folder, file_name)
            images.append(iio.imread(file_path))
    
    if not images:
        print("没有找到任何图片！请检查文件夹。")
        return

    # 保存 GIF
    iio.imwrite(output_gif, images, duration=duration, loop=0)
    print(f"GIF 已成功保存到 {output_gif}")


# GIFmake(input_folder="/mnt/e/workspace/pic/20220629/GIFmake", output_gif="/mnt/e/workspace/pic/20220629/DIFFT_horavguv.gif", duration=500)