import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import gc
import psutil  # 用於監控記憶體使用量
import pandas as pd

from pathconfig import *
from read_utils import *
from plot_utils import *
from plot_settings import *
from tool_utils import utc2lst, obj_analysis, nature_neighbor, get_potential_temp, append_or_fill, get_closest_obs_file

# coord = (120, 121.25, 22.9, 25.2) 22.9, 23.9, 24.7, 24.6, 25.2
coord = (120.30, 121.10, 23.9, 25.1)
target_cities = ['雲林縣', '彰化縣', '臺中市', '南投縣', '桃園市', '苗栗縣', '新竹縣', '新竹市']
# target_cities = ['臺南市']
target_var    = ['STID', 'STNM', 'LAT', 'LON', 'ELEV', 'WDIR', 'WDSD', 'TEMP', 'HUMD', 'PRES', 'CITY', 'WS15M', 'WD15M']
target_lat    = [23.6, 25.2]
target_lon    = [120.00, 121.20]
##############################################################
# for reading the STAOBS and do the nn_interpolate from metpy
##############################################################

# catch the file only start with the specific date and sorted
files_obs   = sorted(list(STA_OBS.glob("20220629*")))
files_obs28 = sorted(list(STA_OBS28.glob("20220628*")))
files_obs10 = sorted(list(STA_OBS2.glob("20220629*")))
files_rain  = sorted(list(RAINS.glob("20220629*")))
# files_cv    = sorted(os.listdir(MOSAIC2D))
files_cv    = sorted(list(SPOL_GRID.glob("*nc")))

# region
'''
for i in range(20, len(files_obs)-65):

    print(f"Processing file: {files_obs[i]}")
    print(f"Processing file: {files_cv[i]}")
    file_obs = str(STA_OBS / files_obs[i])
    file_cv  = str(MOSAIC2D / files_cv[i])

    # read obs data and do nn_interpolation
    fm = fileread(file_obs)
    df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)

    # fr = fileread(file_cv)
    # f  = fr.readCOMPREF2D()
    
    # get lst time
    lst_time = utc2lst(filename=str(files_cv[i]))
    time_str = lst_time[-4::] + "LST" + " " + lst_time[-8:-6] + "/" + \
               lst_time[-6:-4] + "/" + lst_time[0:4]

    # obj_analysis for only data from mdf file
    # no universal version now
    grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev = obj_analysis(df, target_lat=target_lat, target_lon=target_lon)
    grid_T = grid_T - 273.15

    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_OBS(coordinates=coord, lat=grid_lat, lon=grid_lon, var=grid_T, extend="both", cmap=cold_pool_temp, cb_name="DegC", title=None, time_str=time_str, size=17)
    ax       = map_plot.plot_map_OBS(coordinates=coord, lat=df['LAT'].values, lon=df['LON'].values, u=u, v=v, windbar_on=True, title=None, time_str=None, size=17)
    # ax       = map_plot.plot_map_OBS(lat=f.lat, lon=f.lon, var=f.data, threshold=50, contour_on=True, overlay=True, ax=ax, colors="red")
    # ax       = map_plot.plot_map_OBS(lat=f.lat, lon=f.lon, var=f.data, threshold=35, contour_on=True, overlay=True, ax=ax, colors="green")

    map_plot.save_map(ax, filename=f"{lst_time}.png")

    # del fr, df, grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev, ax
    # gc.collect()

    break
'''

# endregion

# region

wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
##############################################################
# for reading the STAOBS and plot diff temp, pres
##############################################################
for i in range(0, len(files_obs)):

    print(f"Processing file: {files_obs[24]}")
    print(f"Processing file: {files_cv[i]}")
    file_cv     = files_cv[i]
    file_obs    = str(STA_OBS / files_obs[i])
    file_obsold = str(STA_OBS / files_obs[24])
    # w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"
    
    closest_obs_file = get_closest_obs_file(file_cv, files_obs)
    closest_rain_file= get_closest_obs_file(file_cv, files_rain)
    print(f"Processing file: {closest_obs_file}")
    print(f"Processing file: {closest_rain_file}")


    # read obs data and do nn_interpolation
    fm = fileread(closest_obs_file)
    df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)

    # fmo= fileread(file_obsold)
    # dfo= fmo.readmdf(filtered_city=target_cities, filtered_var=target_var)
    df["TEMP"] = pd.to_numeric(df["TEMP"], errors="coerce")
    mean_T = (df['TEMP'].mean())

    fmr= fileread(closest_rain_file)
    dfr= fmr.readmdf(filtered_city=target_cities, filtered_var=['STID', 'STNM', 'LAT', 'LON', 'ELEV', 'MIN_10'], filter_on=False)

    fr = fileread(file_cv)
    f  = fr.readSPolgrid(CVon=True)

    # wr = fileread(w_ret_dir)
    # dw = wr.readwretrie_nc(altitude=2)
    
    # get lst time
    lst_time = utc2lst(filename=str(file_cv))
    time_str = f"{lst_time}LST 06/29/2022"

    # title_str= r"$\theta_e$"
    title_str = "Temperature anomaly"
    skip = 6
    # obj_analysis for only data from mdf file
    # no universal version now
    grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev = obj_analysis(df, target_lat=target_lat, target_lon=target_lon)
    # grid_T = grid_T - 273.15

    # grid_To, grid_Td, q, uo, vo, grid_lat, grid_lon, grid_elev = obj_analysis(dfo, target_lat=target_lat, target_lon=target_lon)
    # grid_To= grid_To - 273.15

    diff_T = df['TEMP'].values - mean_T
    # df                              = get_potential_temp(df)
    # potentialT                      = df['Equivalent_potemp'].values 
    known_points                    = np.array(list(zip(df['LAT'].values, df['LON'].values)))
    var_interp, grid_lat, grid_lon  = nature_neighbor(known_points, diff_T, target_lat, target_lon)
    
    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_OBS(coordinates=coord, lat=grid_lat, lon=grid_lon, var=var_interp, extend="both", cmap=cold_pool_temp, levels=np.arange(-5, 1, 1), cb_name="K", title=title_str, time_str=time_str, size=17)
    ax       = map_plot.plot_map_OBS(lat=f.lat, lon=f.lon, var=f.data, threshold=[45], contour_on=True, overlay=True, ax=ax, colors="red")
    # ax       = map_plot.plot_map_OBS(lat=dfr['LAT'].values, lon=dfr['LON'].values, var=dfr['MIN_10'].values, scatter_on=True, overlay=True, ax=ax, colors="blue", zorder=120)
    ax       = map_plot.plot_map_OBS(lat=df['LAT'].values, lon=df['LON'].values, u=u, v=v, windbar_on=True, overlay=True, ax=ax)
    # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[::skip], lon=dw.longitude.values[::skip], u=dw.U.values[0][::skip, ::skip], v=dw.V.values[0][::skip, ::skip], windbar_on=True, overlay=True, ax=ax)
    
    map_plot.save_map(ax, filename=f"DIFFT_{lst_time}.png")

    # del fr, df, grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev, ax
    # gc.collect()

# endregion

# region
'''
##############################################################
# for reading the STAOBS and plot diff pres and theta
##############################################################
for i in range(56, len(files_obs)-30):

    print(f"Processing file: {files_obs[i]}")
    print(f"Processing file: {files_obs[i-4]}")
    # print(f"Processing file: {files_cv[i]}")
    file_obs    = str(STA_OBS / files_obs[i])
    file_obs2   = str(STA_OBS2 / files_obs10[i])
    print(file_obs2)
    file_obsold = str(STA_OBS / files_obs[i-4])
    # file_cv     = str(MOSAIC2D / files_cv[i])

    # read obs data and do nn_interpolation
    fm = fileread(file_obs)
    df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)
    df = get_potential_temp(df)

    fmo= fileread(file_obsold)
    dfo= fmo.readmdf(filtered_city=target_cities, filtered_var=target_var)
    dfo= get_potential_temp(dfo)

    # f10m = fileread(file_obs2)
    # df10 = f10m.readmdf(filtered_city=target_cities, filtered_var=target_var, set_rename=True)
    # df10 = get_potential_temp(df10)

    fr = fileread(file_cv)
    f  = fr.readSPolgrid()
    
    # get lst time
    lst_time = utc2lst(filename=str(files_obs[i]))
    print(lst_time)
    time_str = lst_time + " LST"
    title_str= "Surface Wind"

    # obj_analysis for only data from mdf file
    # no universal version now
    grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev = obj_analysis(df, target_lat=target_lat, target_lon=target_lon)

    # merged                          = pd.merge(df, dfo, on='STID', suffixes=('', '_dfo'))
    # diff_var                        = merged['PRES'].values - merged['PRES_dfo'].values
    # diff_var                        = np.sqrt(2 * diff_var * 100 / 1)
    # known_points                    = np.array(list(zip(merged['LAT'].values, merged['LON'].values)))
    # var_interp, grid_lat, grid_lon  = nature_neighbor(known_points, diff_var, target_lat, target_lon)


    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_OBS(coordinates=coord, lat=grid_lat, lon=grid_lon, var=grid_T, extend="both", cmap="jet", levels=np.arange(0, 21, 1), cb_name="m/s", title=title_str, time_str=time_str, size=17)
    ax       = map_plot.plot_map_OBS(lat=f.lat, lon=f.lon, var=f.data, threshold=[45], contour_on=True, overlay=True, ax=ax, colors="red")
    # ax       = map_plot.plot_map_OBS(lat=f.lat, lon=f.lon, var=f.data, threshold=35, contour_on=True, overlay=True, ax=ax, colors="green")
    # ax       = map_plot.plot_map_OBS(lat=df['LAT'].values, lon=df['LON'].values, u=u, v=v, threshold=35, windbar_on=True, overlay=True, ax=ax)
    # ax       = map_plot.plot_map_OBS(coordinates=coord, lat=df['LAT'].values, lon=df['LON'].values, u=u, v=v, threshold=35, windbar_on=True, title=title_str, time_str=time_str, size=17)

    # ax       = map_plot.plot_map_OBS(coordinates=coord, lat=df['LAT'].values, lon=df['LON'].values, u=1, v=1, var=df['TEMP'].values, threshold=35, scatter_on=True, title=title_str, time_str=time_str, size=25)
    # ax       = map_plot.plot_map_OBS(lat=df10['LAT'].values, lon=df10['LON'].values, u=1, v=1, var=df['TEMP'].values, threshold=35, scatter_on=True, title=None, time_str=None, size=25, overlay=True, ax=ax)
    map_plot.save_map(ax, filename=f"{lst_time}_station.png")

    # del df, grid_T, grid_Td, q, u, v, grid_lat, grid_lon, grid_elev, ax
    # gc.collect()

'''
# endregion

# region
'''
##############################################################
# for individual analysis pic: delta_theta and delta_p
##############################################################
plotter = Analysisplot(figsize=(10, 10))
ax      = plotter.ax
for i in range(20, len(files_obs)-65):
    
    print(f"Processing file: {files_obs[i-1]}")
    print(f"Processing file: {files_cv[i]}")
    file_obs    = str(STA_OBS / files_obs[i])
    file_obsold = str(STA_OBS / files_obs[i-1])

    # read obs data and do nn_interpolation
    fm = fileread(file_obs)
    df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)
    df = get_potential_temp(df)

    fmo= fileread(file_obsold)
    dfo= fmo.readmdf(filtered_city=target_cities, filtered_var=target_var)
    dfo= get_potential_temp(dfo)
    
    # get title
    title_str= r"Relationship between $\Delta P$ and $\Delta \theta$"

    merged       = pd.merge(df, dfo, on='STID', suffixes=('', '_dfo'))
    diff_var_the = merged['Potential_temp'].values - merged['Potential_temp_dfo'].values
    diff_var_p   = merged['PRES'].values - merged['PRES_dfo'].values
    diff_var_t   = merged['TEMP'].values - merged['TEMP_dfo'].values                   

    # set map and plot
    ax = plotter.plot_ana_scatter(
            x=np.tile(i, len(diff_var_t)), 
            y=diff_var_t, 
            color="black", 
            size=30, 
            alpha=0.7, 
            xlabel= r"$\Delta P$", 
            ylabel= r"$\Delta T$", 
            title=title_str,
            corr_method=None, 
            show_corr=False, 
            xlim=(19,31), ylim=(-5,0), dx=1, dy=0.5,
            overlay=True,  # 關鍵：保持同一張圖
            ax=ax  # 傳入相同的 ax
        )

    plotter.save_map(ax, filename="combined_scatter.png")

    del df, dfo, diff_var_p, diff_var_the
    gc.collect()

    if i >= 30:
        break
'''
# endregion

# region

##############################################################
# for individual analysis pic: delta_T varying from time
##############################################################
# plotter = Analysisplot(figsize=(10, 10))
# ax      = plotter.ax
'''
lat_bins = np.arange(22.9, 25.1 + 0.2, 0.2)
# print(lat_bins)
homoller_matrix = []
homoller_matrix2= []
time_label      = []
for i in range(21, len(files_obs)-75):
    
    print(f"Processing file: {files_obs[i-3]}")
    # print(f"Processing file: {files_cv[i]}")
    file_obs    = str(STA_OBS / files_obs[i])
    file_obsold = str(STA_OBS / files_obs[i-3])

    # read obs data and do nn_interpolation
    fm = fileread(file_obs)
    df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)
    df = get_potential_temp(df)

    fmo= fileread(file_obsold)
    dfo= fmo.readmdf(filtered_city=target_cities, filtered_var=target_var)
    dfo= get_potential_temp(dfo)
    
    # get title
    lst_str  = utc2lst(str(files_obs[i]))
    title_str= r"Relationship between $\Delta P$ and $\Delta \theta$"
    time_label.append(lst_str)

    merged       = pd.merge(df, dfo, on='STID', suffixes=('', '_dfo'))  
    merged['diff_var_the'] = merged['Potential_temp'] - merged['Potential_temp_dfo']
    merged['diff_var_p'] = merged['PRES'] - merged['PRES_dfo']
    merged['diff_var_t'] = merged['TEMP'] - merged['TEMP_dfo']    

    filtered = merged[merged['ELEV'] < 1000]               

    #set homoller
    lat_avg = []
    lat_avg2= []
    for j in range(len(lat_bins) - 1):
        lat_min, lat_max = lat_bins[j], lat_bins[j + 1]
        group = filtered[(filtered['LAT'] >= lat_min) & (filtered['LAT'] < lat_max)]
        if not group.empty:
            # 計算平均值或最小值（可修改為其他統計方法）
            value = group['diff_var_t'].min()  # 改成 group['diff_var_the'].min() 如果需要最小值
        else:
            value = np.nan  # 若無數據，填入 NaN
        lat_avg.append(value)

        if not group.empty:
            # 計算平均值或最小值（可修改為其他統計方法）
            value = group['diff_var_p'].mean()  # 改成 group['diff_var_the'].min() 如果需要最小值
        else:
            value = np.nan  # 若無數據，填入 NaN
        lat_avg2.append(value)
    
    # 將當前時間點的結果加入矩陣
    homoller_matrix.append(lat_avg)
    homoller_matrix2.append(lat_avg2)
    del df, dfo
    gc.collect()

# 轉換為 NumPy 矩陣
homoller_matrix  = np.array(homoller_matrix).T  # 轉置，使行是緯度，列是時間
homoller_matrix2 = np.array(homoller_matrix2).T
print(np.shape(homoller_matrix))

plt.figure(figsize=(12, 12))
time_labels = range(21, len(files_obs) - 75)  # 時間標籤

# ct = plt.contour(time_labels, lat_bins[:-1], homoller_matrix2, colors="red", levels=np.arange(0.2, 2.5, 0.2))
# plt.clabel(ct, fmt="%.1f", colors="black",  fontsize=15)

plt.contourf(time_labels[::3], lat_bins[:-1], homoller_matrix[:,::3], cmap='Blues_r', levels=np.arange(-10, -0.5, 0.5), extend="min")
cbar = plt.colorbar(label=r"$\Delta T(K)$")  # 設置顏色條與標籤
cbar.ax.yaxis.label.set_size(20)
cbar.ax.tick_params(labelsize=15)

plt.xlabel('Time (LST)', fontsize=20)
plt.ylabel('Latitude (°)', fontsize=20)

plt.xticks(
    ticks=time_labels[::3],  # 每隔三個顯示一次刻度
    labels=[f"{i}" for i in time_label[::3]], # 顯示時間標籤
    rotation=45,
    fontsize=15
)

# 自訂 y 軸刻度與標籤
plt.yticks(
    ticks=lat_bins[:-1],  # 使用緯度範圍作為刻度
    fontsize=15,
    labels=[f"{lat:.2f}°" for lat in lat_bins[:-1]]  # 格式化緯度標籤
)

# plt.title( r"Hovmöller Diagram: $\Delta T$ by Latitude")
plt.tight_layout()
plt.savefig("/mnt/e/workspace/pic/20220629/delta_T_homoller_min_30mdiff.png", dpi=300)
'''
# endregion

# region
'''
####################################################################
# for individual analysis pic: line chart for Pres, Temp, ws, wd
####################################################################
target_STID = ["C0X120", "467480", "C0K440"]
target_STID = ["C0K470", "C0I410", "C0H960", "C0I420"]
target_STID = ["467490", "C0F9P0", "C0E750", "467571", "467050"] #467050
colors_map  = ["red", "blue", "green", "orange", "purple"]
markers     = ["o", "^", "D", "s", "*"]
plotter     = Analysisplot(figsize=(12, 12), nrows=4)
ax          = plotter.ax
ax1         = ax[0]
ax2         = ax[1]
ax3         = ax[2]
ax4         = ax[3]

for STID, color, marker in zip(target_STID, colors_map, markers):
    print(STID)

    time_label = []
    wdir_matrix= []
    wdsp_matrix= []
    temp_matrix= []
    pres_matrix= []

    files_ann  = sorted(list(STA_ann.glob(f"{STID}*")))

    if STID == "467571" or STID == "467050":
        alpha=0.1
    else:
        alpha=1.0
    # alpha= 1.0

    for i in range(42, len(files_obs)-79):
        
        # print(f"Processing file: {files_obs[i-3]}")
        file_obs      = str(STA_OBS / files_obs[i])
        file_obs10    = str(STA_OBS2 / files_obs10[i])
        file_ann      = str(STA_ann / files_ann[i])

        # read obs data and do nn_interpolation
        fm = fileread(file_obs)
        df = fm.readmdf(filtered_city=target_cities, filtered_var=target_var)
        df = get_potential_temp(df)

        fo = fileread(file_obs10)
        dfo= fo.readmdf(filtered_city=target_cities, filtered_var=target_var, set_rename=True)
        dfo= get_potential_temp(dfo)

        dfann = pd.read_csv(file_ann)
        P_ann = dfann['ten_year_avg'].values
        
        merged = pd.concat([df, dfo], axis=0)
        
        df = merged[merged["STID"] == STID]
                
        # get title
        lst_str  = utc2lst(str(files_obs[i]))
        title_str= r"Relationship between $\Delta P$ and $\Delta \theta$"
        

        if len(df["TEMP"].values) != 0:
            time_label.append(lst_str)
            temp_matrix.append(df['TEMP'].values)
            pres_matrix.append(df['PRES'].values-P_ann)
            wdir_matrix.append(df['WDIR'].values)
            wdsp_matrix.append(df['WDSD'].values)        

        del df
        gc.collect()

    plotter.plot_ana_linechart(ax=ax1, x=time_label, y=temp_matrix, ylabel=np.arange(22, 35, 4), color=color, linewidth=2, marker=marker, alpha=alpha, skip=3, title="Temperature")
    plotter.plot_ana_linechart(ax=ax2, x=time_label, y=pres_matrix, ylabel=np.arange(-5, 0.5, 0.5), color=color, linewidth=2, marker=marker, alpha=alpha, skip=3, title="Pressure")
    plotter.plot_ana_linechart(ax=ax3, x=time_label, y=wdir_matrix, ylabel=np.arange(0, 405, 45), color=color, linewidth=2, marker=marker, alpha=alpha, skip=3, title="Wind direction")
    plotter.plot_ana_linechart(ax=ax4, x=time_label, y=wdsp_matrix, ylabel=np.arange(0, 12, 2), color=color, linewidth=2, marker=marker, alpha=alpha, skip=3, title="Wind speed", labelbottom=True)


plt.tight_layout()
plt.savefig("/mnt/e/workspace/pic/20220629/linecharts3_1.png")
'''
# endregion