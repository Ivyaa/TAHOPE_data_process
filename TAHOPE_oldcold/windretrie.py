import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import gc
import psutil  # 用於監控記憶體使用量

from scipy.interpolate import griddata

from pathconfig import *
from read_utils import *
from plot_utils import *
from plot_settings import *
from tool_utils import utc2lst, filter_files_by_time, calculate_bearing, calvorticity, gridding_data
from othsettings import U_matrix, V_matrix

# region

###############################################
# plot CV from mosaic2D GRWIND
###############################################
coord = (120.30, 121.10, 23.9, 25.1)
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
angles= os.listdir("/mnt/e/workspace/pic/20220629/Spol/RHI/")

# 半徑 (km)
radius_km = 120
# 地球半徑（近似值，單位：km）
earth_radius = 6371.0

height = [0.5]
'''
for alt in height:

    for i in range(18, 36):

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid(CVon=True, alt=alt)

        wr = fileread(w_ret_dir)
        dw = wr.readwretrie_nc(altitude=alt)
        # dudx = dw.DUDX.values[0]
        # dvdy = dw.DVDY.values[0]
        # DIV= dudx + dvdy
        U_hvor = (dw.DWDY.values[0] - dw.DVDZ.values[0])/100
        V_hvor = (dw.DUDZ.values[0] - dw.DWDX.values[0])/100
        print(np.nanmax(U_hvor), np.nanmax(V_hvor))

        skip = 6
        # set map and plot
        # Spol loc
        spol_loc = [120.90746307373, 24.8190879821777]
        map_plot = Mapplot()
        ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"{str(alt)} km", time_str=time_str, size=17)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=dw.WSPD.values[0], cmap=wind_speed_cmap, levels=wind_speed_levels, extend="max", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[::skip], lon=dw.longitude.values[::skip], u=dw.U.values[0][::skip, ::skip], v=dw.V.values[0][::skip, ::skip], windbar_on=True, overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=DIV/100, cmap=DIV_cmap, levels=DIV_levels, extend="both", overlay=True, ax=ax)
        ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[::skip], lon=dw.longitude.values[::skip], u=U_hvor[::skip, ::skip], v=V_hvor[::skip, ::skip], windbar_on=True, overlay=True, ax=ax)

        # 繪製角度線
        # lon0, lat0 = spol_loc
        # for angle in angles:
        #     angle = float(angle.split('.')[0])  # 提取角度數值
        #     angle_rad = np.radians(angle)  # 角度轉弧度

        #     # 計算直線終點經緯度（以北為 0°）
        #     lat_end = lat0 + (radius_km / earth_radius) * np.degrees(np.cos(angle_rad))
        #     lon_end = lon0 + (radius_km / (earth_radius * np.cos(np.radians(lat0)))) * np.degrees(np.sin(angle_rad))

        #     # 繪製直線
        #     ax.plot(
        #         [lon0, lon_end],
        #         [lat0, lat_end],
        #         transform=ax.transData,
        #         color="black",
        #         linestyle="-",
        #         linewidth=1,
        #         label=f"Angle {angle}°" if angle == float(angles[0].split('.')[0]) else None,
        #         zorder=500
        #     )

        # 顯示圖例
        map_plot.save_map(ax, filename=f"20220629{lst_time}_{str(alt)}km_hvor.png")

        # release memory
        del fr, f, map_plot, ax, lst_time, time_str
        gc.collect()
'''
# endregion

# region
'''
###############################################
# plot CV from mosaic2D SRWIND
###############################################
coord = (120.30, 121.10, 23.9, 25.1)
PPwdir= 321.46; PPwspd = 6.32
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
cnfiles=sorted(list(SPOL_FRAC.glob("2022*")))
height = [2.5]

for alt in height:
    # 12, 36
    for i in range(18, 36):

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        print(f"Processing file: {cnfiles[i-18]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"
        cn_dir   = str(cnfiles[i-18]) + "/output.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid()

        cnn= fileread(cn_dir)
        dn = cnn.readfractl_nc(altitude=alt*1000)

        plotting_CN = dn.conditionNumber.values[0]
        plotting_lat= dn.lat0.values[:,:,0]
        plotting_lon= dn.lon0.values[:,:,0]
        

        wr = fileread(w_ret_dir)
        dw = wr.readwretrie_nc(altitude=alt)
        SR_U = dw.SR_U.values[0]
        SR_V = dw.SR_V.values[0]
        SR_WS= np.sqrt(SR_U ** 2 + SR_V ** 2)

        # interp fractl cn_lat, cn_lon
        CN_interp = gridding_data(target_lat=dw.latitude, target_lon=dw.longitude, origin_lat=plotting_lat, origin_lon=plotting_lon, origin_data=plotting_CN)
        CN_threshold = 10
        SR_WS = np.where(CN_interp < CN_threshold, SR_WS, np.nan)
        SR_U  = np.where(CN_interp < CN_threshold, SR_U, np.nan)
        SR_V  = np.where(CN_interp < CN_threshold, SR_V, np.nan)
        Updrafts  = np.where(CN_interp < CN_threshold, dw.W.values[0], np.nan)
        vor   = np.where(CN_interp < CN_threshold, dw.VOR.values[0], np.nan) /1000

        # print(CN_interp)
        # print(np.shape(dw.SR_U.values[0]))
        

        skip = 6
        # set map and plot
        map_plot = Mapplot()
        ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"{str(dw.altitude.values)} km", time_str=time_str, size=17)
        ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=vor, cmap=VORR_cmap, levels=VORR_levels, extend="max", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=SR_WS, contour_on=True, threshold=[15], colors="#633602", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=SR_WS, contour_on=True, threshold=[14], colors="#ffedcc", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=SR_WS, contour_on=True, threshold=[8], colors="#728944", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=Updrafts, contour_on=True, threshold=[4], colors="#ffd1d1", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[::skip], lon=dw.longitude.values[::skip], u=SR_U[::skip, ::skip], v=SR_V[::skip, ::skip], windbar_on=True, overlay=True, ax=ax)
        # ax       = map_plot.plot_map_prof(start_lat=24.40, start_lon=120.40, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, overlay=True, ax=ax)
        # # ax       = map_plot.plot_map_prof(start_lat=24.65, start_lon=120.52, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, point_str=["B", "B'"], overlay=True, ax=ax)
        # # ax       = map_plot.plot_map_prof(start_lat=24.40, start_lon=120.75, end_lat=24.00, end_lon=120.50, colors="black", linewidth=3, point_str=["C", "C'"], overlay=True, ax=ax)
        # ax       = map_plot.plot_map_prof(start_lat=24.80, start_lon=120.75, end_lat=24.35, end_lon=121.20, colors="black", linewidth=3, point_str=["B", "B'"], overlay=True, ax=ax)
        
        # start_point=[24.8190879821777, 120.90746307373], end_point=[24.06976, 120.87605]
        # ax       = map_plot.plot_map_prof(start_lat=24.7890879821777, start_lon=120.90746307373, end_lat=24.06976, end_lon=120.87605, colors="black", linewidth=3, point_str=["C", "C'"], overlay=True, ax=ax)
        # ax       = map_plot.plot_map_prof(start_lat=24.8490879821777, start_lon=120.90746307373, end_lat=25.15, end_lon=120.90746307373, colors="black", linewidth=3, point_str=["D", "D'"], overlay=True, ax=ax)

        map_plot.save_map(ax, filename=f"20220629{lst_time}_{str(dw.altitude.values)}km_VOR_mask.png")

        # release memory
        del fr, f, map_plot, ax, lst_time, time_str
        gc.collect()
'''
# endregion

# region

###############################################
# plot CV from mosaic2D SRWIND profile
###############################################
coord = (120.30, 121.10, 23.8, 24.7)
PPwdir= 321.46; PPwspd = 6.32
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
cnfiles=sorted(list(SPOL_FRAC.glob("2022*")))
height = [1.0, 1.5, 2.0]
elev_plot = np.arange(0, 18.5, 0.5)
terrain = get_terrain(TERRAIN)
for i in range(18, 36):

    print(f"Processing file: {files[i]}")
    print(f"Processing file: {wfiles[i]}")
    print(f"Processing file: {cnfiles[i-18]}")

    # print_memory_usage()

    # convert to file_path(str)
    file_dir = str(files[i])
    w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"
    cn_dir   = str(cnfiles[i-18]) + "/output.nc"

    # get lst time
    lst_time = utc2lst(filename=str(files[i]))
    time_str = f"{lst_time}LST 06/29/2022"

    # need to call object first then 
    # give the other instructions
    # you can read csv, mdf, mosaic2D in this fr object
    # but only one file can be read
    cnn= fileread(cn_dir)
    dn = cnn.readfractl_nc(altitude=None)

    fr = fileread(file_dir)
    ds = fr.readSPolgrid(profile_on=True, end_point=[24.40, 120.40], start_point=[23.9, 120.95])
    
    wr = fileread(w_ret_dir)
    dw = wr.readwretrie_nc(profile_on=True, end_point=[24.41, 120.40], start_point=[23.9, 120.95], mask_CN=True, dn=dn)
    
    # points       = np.column_stack((terrain.lon.flatten(), terrain.lat.flatten()))
    # prof_terrain = griddata(points, terrain.data.flatten(), (dw.longitude.values, dw.latitude.values), method='linear')
    # print(np.shape(dw.DBZ.values))
    skip = 3

    # set map and plot
    # profplot = Profileplot(figsize=(8, 3))
    # ax       = profplot.ax #cmap=radar_colormap, levels=clevel, extend="neither"
    # ax       = profplot.plot_prof_contourf(ax=ax, x=dw.latitude.values, z=elev_plot, var=ds.DBZ.values[0], cmap=radar_cf_cmap, levels=range(45, 55, 8), extend="max")
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot, var=ds.DBZ.values[0], threshold=[15, 25, 35, 45, 50], colors="#a3a3a3", time_str=time_str)    
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot, var=ds.KDP.values[0], threshold=[1.0, 2.0, 3.0], colors="blue", linewidths=2)
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot, var=dw.SR_WS.values[0], threshold=[20], colors="#728994")
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:5], var=dw.SR_WS.values[0, 1:5, :], threshold=[8], colors="#ffedcc")
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[16], colors="#633602")
    # ax       = profplot.plot_prof_wind(ax=ax, x=dw.latitude.values[2::2], z=elev_plot[0:-1:2], u=dw.SR_U.values[0, 0:-1:2, 2::2], v=dw.W.values[0, 0:-1:2, 2::2] * 2 ) # *2
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot, var=dw.W.values[0], threshold=[10], colors="blue")
    # ax       = plot_fill_terrain(ax=ax, R=dw.latitude.values, terrain=prof_terrain)
    
    # profplot.save_map(ax=ax, filename=f"20220629{lst_time}_windretrieUW_prof.png")
    # # ax       = map_plot.plot_map_prof(start_lat=24.40, start_lon=120.40, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, overlay=True, ax=ax)
    # # ax       = map_plot.plot_map_prof(start_lat=24.65, start_lon=120.52, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, point_str=["B", "B'"], overlay=True, ax=ax)
    # # ax       = map_plot.plot_map_prof(start_lat=24.40, start_lon=120.75, end_lat=24.00, end_lon=120.50, colors="black", linewidth=3, point_str=["C", "C'"], overlay=True, ax=ax)
    # # ax       = map_plot.plot_map_prof(start_lat=24.80, start_lon=120.75, end_lat=24.35, end_lon=121.20, colors="black", linewidth=3, point_str=["D", "D'"], overlay=True, ax=ax)

    # profplot = Profileplot(figsize=(8, 3))
    # ax       = profplot.ax
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[16], colors="#633602")
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[10], colors="#ffffff")
    # ax       = profplot.plot_prof_contourf(ax=ax, x=dw.latitude.values, z=elev_plot, var=ds.DBZ.values[0], cmap=radar_colormap, levels=clevel, extend="neither", time_str=time_str)
    # profplot.save_map(ax=ax, filename=f"20220629{lst_time}_windretrieUV_prof.png")

    # profplot = Profileplot(figsize=(8, 3))
    # ax       = profplot.ax
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=ds.KDP.values[0, 1:-1, :], threshold=[1.0, 2.0, 3.0], colors="blue", linewidths=2)
    # # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[10], colors="#ffffff")
    # ax       = profplot.plot_prof_contourf(ax=ax, x=dw.latitude.values, z=elev_plot, var=ds.DBZ.values[0], cmap=radar_colormap, levels=clevel, extend="neither", time_str=time_str)
    # profplot.save_map(ax=ax, filename=f"20220629{lst_time}_windretrieKDP_prof.png")

    # profplot = Profileplot(figsize=(8, 3))
    # ax       = profplot.ax
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=list(np.arange(5, 12, 5)), colors="black", linewidths=1)
    # ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=list(np.arange(-7, -4, 2)), colors="black", linestyles="--", linewidths=1)
    # ax       = profplot.plot_prof_contourf(ax=ax, x=dw.latitude.values, z=elev_plot, var=dw.VOR.values[0]/1000, cmap=VORR_cmap, levels=VORR_levels, extend="both", cb_name="VOR", time_str=time_str)
    # profplot.save_map(ax=ax, filename=f"20220629{lst_time}_windretrieVVOR_prof.png")

    profplot = Profileplot(figsize=(8, 3))
    uvornew, vvornew = deformation_horizontal_vor(dw.UVOR.values[0], dw.VVOR.values[0])
    
    # HHVOR    = np.sqrt(dw.UVOR.values[0]**2 + dw.VVOR.values[0]**2)
    ax       = profplot.ax
    ax       = profplot.plot_prof_contourf(ax=ax, x=dw.latitude.values, z=elev_plot, var=vvornew/10, cmap=W_cmap, levels=np.arange(-4, 5, 1), extend="both", cb_name="Hvor", time_str=time_str)
    ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=list(np.arange(5, 12, 5)), colors="black", linewidths=1)
    ax       = profplot.plot_prof_contour(ax=ax, x=dw.latitude.values, z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=list(np.arange(-7, -4, 2)), colors="black", linestyles="--", linewidths=1)
    # ax       = profplot.plot_prof_wind(ax=ax, x=dw.latitude.values[2::2], z=elev_plot[0:-1:1], u=dw.UVOR.values[0, 0:-1:1, 2::2], v=dw.VOR.values[0, 0:-1:1, 2::2]/1000 )
    profplot.save_map(ax=ax, filename=f"20220629{lst_time}_windretrieWHVOR_prof_U_mask.png")

    # release memory
    # del fr, ax, lst_time, time_str
    # gc.collect()

# endregion

# region
'''
###############################################
# plot vorticity relatied
###############################################
# 120.30, 121.10, 23.8, 25.1
# 120.50, 121.00, 24.1, 24.5
# 120.70, 121.10, 24.6, 24.9

coord = (120.50, 121.00, 24.1, 24.5)
# PPwdir= 321.46; PPwspd = 6.32
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
height = [1.0, 1.5, 2.0]
elev_plot = np.arange(0, 18.5, 0.5)

for alt in range(5, 6, 1):
    res = []; tlt = []; strr = []
    had = []; vad = []; vorr = []
    new_vor = []; inter_vor = []
    time_label = []
    for i in range(18, 36):
        #18, 36
        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"
        w_ret_dir0= str(wfiles[i+1]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"
        time_label.append(lst_time)

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid(profile_on=False, start_point=[23.9, 120.95], end_point=[24.40, 120.40])

        wr = fileread(w_ret_dir)
        dw = wr.readwretrie_nc()
        
        HAD, VAD, STR, TLT, vor = calvorticity(dw)
        # print(HAD, VAD, STR, TLT)

        wr = fileread(w_ret_dir0)
        dw0 = wr.readwretrie_nc()
        HAD0, VAD0, STR0, TLT0, vor0 = calvorticity(dw0)
        
        total_vor = -(STR + TLT + VAD + HAD)
        
        if i == 21: #21
            final_vor = (vor-vor0)/1440 - total_vor
            diff_vor  = -(vor-vor0)/1440
            new_vor.append(new_vor[-1] + 1440 * (total_vor))
        elif i == 18 : #18
            final_vor = (vor-vor0)/720 - total_vor
            diff_vor  = -(vor-vor0)/720
            new_vor.append(vor)
        else:
            final_vor = (vor-vor0)/720 - total_vor
            diff_vor  = -(vor-vor0)/720
            new_vor.append(new_vor[-1] + 720 * (total_vor))

        inter_vorr = np.array(new_vor[-1])
        print(dw["altitude"].values[alt])
        print((np.nanmean(final_vor[0, alt, :, :])))

        res.append(np.nanmean(final_vor[:, alt, :, :]))
        inter_vor.append(np.nanmean(inter_vorr[:, alt, :, :]))
        vorr.append(np.nanmean(vor[:, alt, :, :]))
        had.append(np.nanmean(-HAD[:, alt, :, :]))
        vad.append(np.nanmean(-VAD[:, alt, :, :]))
        tlt.append(np.nanmean(-TLT[:, alt, :, :]))
        strr.append(np.nanmean(-STR[:, alt, :, :]))
        
        total_item = (-TLT - STR) / 10
        
        # break
        #print(np.nanmax(total_vor))
        vor = vor / 1000
        diff_vor = diff_vor / 10

        map_plot = Mapplot()
        ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"vorticity {str(dw.altitude.values[alt])} km", time_str=time_str, size=17)    
        ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=vor[0, alt, :, :], cmap=VORR_cmap, levels=VORR_levels, extend="both", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=diff_vor[0, alt, :, :], threshold=[0.5, 1.0, 2.0, 3.0], contour_on=True, colors="black", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=diff_vor[0, alt, :, :], threshold=[-3.0, -2.0, -1.0, -0.5], contour_on=True, linestyles='--', colors="black", overlay=True, ax=ax)

        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=total_item[0, alt, :, :], threshold=[0.5, 1.0, 2.0, 3.0], contour_on=True, colors="black", overlay=True, ax=ax)
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=total_item[0, alt, :, :], threshold=[ -3.0, -2.0, -1.0, -0.5], contour_on=True, linestyles='--', colors="black", overlay=True, ax=ax)
        map_plot.save_map(ax=ax, filename=f"vorr_{str(dw.altitude.values[alt])}km_20220629{lst_time}_vor_range0.png")


        # # points       = np.column_stack((terrain.lon.flatten(), terrain.lat.flatten()))
        # # prof_terrain = griddata(points, terrain.data.flatten(), (dw.longitude.values, dw.latitude.values), method='linear')
        
        # # skip = 6
        # # set map and plot
        # #e-5
        # map_plot = Mapplot()
        # ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"HAD {str(dw.altitude.values[alt])} km", time_str=time_str, size=17)    
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=-HAD[0, alt, :, :], cmap=VOR_cmap, levels=VOR_levels, extend="both", overlay=True, ax=ax)
        # map_plot.save_map(ax=ax, filename=f"{str(dw.altitude.values[alt])}km_20220629{lst_time}_HAD.png")

        # #e-5
        # map_plot = Mapplot()
        # ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"VAD {str(dw.altitude.values[alt])} km", time_str=time_str, size=17)    
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=-VAD[0, alt, :, :], cmap=VAD_cmap, levels=VAD_levels, extend="both", overlay=True, ax=ax)
        # map_plot.save_map(ax=ax, filename=f"{str(dw.altitude.values[alt])}km_20220629{lst_time}_VAD.png")

        # #e-5
        # map_plot = Mapplot()
        # ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"STR {str(dw.altitude.values[alt])} km", time_str=time_str, size=17)    
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=-STR[0, alt, :, :], cmap=STR_cmap, levels=STR_levels, extend="both", overlay=True, ax=ax)
        # map_plot.save_map(ax=ax, filename=f"{str(dw.altitude.values[alt])}km_20220629{lst_time}_STR.png")

        # #e-5
        # map_plot = Mapplot()
        # ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"TLT {str(dw.altitude.values[alt])} km", time_str=time_str, size=17)    
        # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=-TLT[0, alt, :, :], cmap=TLT_cmap, levels=TLT_levels, extend="both", overlay=True, ax=ax)
        # map_plot.save_map(ax=ax, filename=f"{str(dw.altitude.values[alt])}km_20220629{lst_time}_TLT.png")


        # # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[::skip], lon=dw.longitude.values[::skip], u=dw.SR_U.values[0, alt, ::skip, ::skip], v=dw.SR_V.values[0, alt, ::skip, ::skip], windbar_on=True, overlay=True, ax=ax)

        # # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=HAD[0, alt, :, :], contour_on=True, threshold=[5], colors="black", overlay=True, ax=ax)
        # # ax       = map_plot.plot_map_OBS(lat=dw.latitude.values, lon=dw.longitude.values, var=SR_WS, contour_on=True, threshold=16, colors="#ffedcc", overlay=True, ax=ax)    # ax       = map_plot.plot_map_prof(start_lat=24.40, start_lon=120.40, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, overlay=True, ax=ax)
        # # ax       = map_plot.plot_map_prof(start_lat=24.65, start_lon=120.47, end_lat=23.9, end_lon=120.95, colors="black", linewidth=3, point_str=["B", "B'"], overlay=True, ax=ax)
        
        # # release memory
        # del fr, ax, lst_time, time_str
        # gc.collect()
    # time_label = range(18, 26)
    fig, ax1 = plt.subplots(figsize=(8, 4))

    # 在第一個 Y 軸上繪製數據
    ax1.plot(time_label, res, '--', label="res")
    ax1.plot(time_label, had, label="HAD")
    ax1.plot(time_label, vad, label="VAD")
    ax1.plot(time_label, tlt, label="TLT")
    ax1.plot(time_label, strr, label="STR")

    ax1.set_xticklabels(time_label, rotation=45)

    ax1.set_xlabel('Time(LST)')
    ax1.set_ylabel('Vorticity Budget $10^{-6}$ s$^{-2}$')
    ax1.legend()
    ax1.grid()

    # 創建第二個 Y 軸
    ax2 = ax1.twinx()

    # 在第二個 Y 軸上繪製 vorr 數據
    ax2.plot(time_label, np.array(vorr)/1000, label="vor", color='black')

    ax2.set_ylabel('Vertical vorticity 10⁻³ s⁻¹')
    # ax2.legend()

    # 保存圖表
    # plt.legend()
    plt.savefig(f"/mnt/e/workspace/pic/20220629/{str(dw.altitude.values[alt])}km_vorticitybudget.png")
    plt.close()
'''
# endregion

# region
'''
###############################################
# plot radar hail area and updraft area
###############################################
coord = (120.30, 121.10, 23.8, 24.7)
PPwdir= 321.46; PPwspd = 6.32
lat_min, lat_max = 23.8, 25.2  # 緯度範圍
lon_min, lon_max = 120.2, 121.2
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
height = [1.0, 1.5, 2.0]
elev_plot = np.arange(0, 18.5, 0.5)
time_plot = np.arange(14, 38, 1)

for alt in range(2, 6, 3):
    HRAIN    = []; HAIL       = []; RAINHAIL = []
    W_MAX    = []; TIME       = []
    W_MIN    = []
    W_UPAREA = []; W_H_UPAREA = []
    W_DWAREA = []; W_H_DWAREA = []
    for i in range(14, 38):

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}"
        TIME.append(time_str)

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid(all_data=True)
        f  = f.sel(y0=slice(lat_min, lat_max), x0=slice(lon_min, lon_max)) #lat, lon

        wr = fileread(w_ret_dir)
        dw = wr.readwretrie_nc()
        dw = dw.sel(latitude=slice(lat_min, lat_max), longitude=slice(lon_min, lon_max))

        # area for pcolormesh in background
        WALL = dw.W.values[0]
        W_H_UPAREA.append(np.sum(WALL > 0, axis=(1, 2)))
        W_H_DWAREA.append(np.sum(WALL < 0, axis=(1, 2)))

        PIDALL = f.PID.values[0]
        HAIL_in_range = (PIDALL >= 6) & (PIDALL < 7)
        HAIL.append(np.sum(HAIL_in_range, axis=(1, 2)))

        HRAIN_in_range = (PIDALL >= 5) & (PIDALL < 6)
        HRAIN.append(np.sum(HRAIN_in_range, axis=(1, 2)))

        RAINHAIL_in_range = (PIDALL >= 7) & (PIDALL < 8)
        RAINHAIL.append(np.sum(RAINHAIL_in_range, axis=(1, 2)))       
        
        W = (dw['W'].sel(altitude=alt).values[0])
        latitude = dw['latitude'].values
        longitude = dw['longitude'].values

        W_positive = W[W > 0]
        W_positive = np.nanmax(W_positive)
        # r, c = np.where(W == np.nanmax(W_positive))
        # print(latitude[r], longitude[c])
        W_MAX.append(W_positive)
        W_UPAREA.append(np.sum(W > 0))

        W_negative = W[W < 0]
        W_negative = np.nanmin(W_negative)
        W_MIN.append(W_negative)
        W_DWAREA.append(np.sum(W < 0))
        print(W_MAX[-1], W_MIN[-1])


        # # release memory
        # del fr, ax, lst_time, time_str
        # gc.collect()

    map_plot = Mapplot()
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
    pc = ax.pcolormesh(time_plot, elev_plot, np.array(HRAIN).T, vmin=0, vmax=1500, cmap="hot_r")
    cbar = plt.colorbar(pc, ax=ax, pad=0.15)

    ax.set_ylim(0, 12)
    ax.set_xlabel("Time")
    ax.set_ylabel("Elevation (km)")
    ax.set_xticks(time_plot)  # 对应时间数组的位置
    ax.set_xticklabels(TIME, rotation=45, ha="right")

    ax = plot_ana_chart(ax, W_MAX, np.abs(W_MIN), W_UPAREA, W_DWAREA, elev_plot, time_plot)

    plt.tight_layout()
    map_plot.save_map(ax=ax, filename=f"{str(alt)}km_HRAINW.png")
    break

'''

# endregion

# region

#############################################
# wind shear for RKW theory
#############################################
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

'''
# read ncfile
file = str(STA_WF)
wprf = fileread(file)
ds   = wprf.readwindprof_nc()

time_grid, height_grid = np.meshgrid(ds.time, ds.ht, indexing="ij")
u = ds.U.values  # 東西向風速
v = ds.V.values  # 南北向風速

# 計算風速
spd = np.sqrt(u**2 + v**2)

# 設定顏色映射
norm = mcolors.Normalize(vmin=np.nanmin(spd), vmax=np.nanmax(spd))
cmap = plt.get_cmap("rainbow")  # 或 "jet", "viridis" 等其他 colormap
colors = cmap(norm(spd))

# 繪圖
height_step = 5
time_step   = 2
fig, ax = plt.subplots(figsize=(14, 7))
for i in range(1, time_grid.shape[0], time_step):  # 遍歷時間
    
    for j in range(3, height_grid.shape[1]):  # 遍歷高度
        if height_grid[0, j] <= 3000:
            if j % 8 != 0:  # 低層每 15 個取 1
                continue
        else:
            if j % 2 != 0:  # 高層每 5 個取 1
                continue
        
        color = cmap(norm(spd[i, j]))  # 根據風速設定顏色
        ax.barbs(time_grid[i, j], height_grid[i, j], u[i, j], v[i, j], 
                 length=7, linewidth=2, barbcolor=color)

# 加入 colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Speed [m/s]')

time_idx = pd.to_datetime(ds.time.values)  # 使用 pandas.to_datetime 轉換為 datetime
formatted_time = time_idx.strftime('%H:%M')  # 轉換為 'HH:MM' 格式

# 設置 X 軸刻度，將時間轉換為 datetime 格式
ax.set_xticks(time_idx[::4])  # 每隔兩個點設置一個刻度
ax.set_ylim(0, 7000)

# 格式化 X 軸的刻度顯示
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

ax.set_xlabel("Time")
ax.set_ylabel("Height (m)")
ax.set_title("Wind Profile (2022-06-29 14:00 - 20:00)")
# ax.set_xticks(formatted_time)  # 減少 X 軸刻度
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig("/mnt/e/workspace/pic/20220629/windprofxinwu.png", dpi=300)
'''
# endregion

# region
# wind shear
'''
# read ncfile
file = str(STA_WF)
wprf = fileread(file)
ds   = wprf.readwindprof_nc()

u_100m= ds.U.sel(ht=100,  method="nearest"); v_100m= ds.V.sel(ht=100,  method="nearest")
u_100m= ds.U.sel(ht=slice(100, 1000)).mean(dim="ht")
v_100m= ds.V.sel(ht=slice(100, 1000)).mean(dim="ht")
u_2km = ds.U.sel(ht=2000, method="nearest"); v_2km = ds.V.sel(ht=2000, method="nearest")
u_3km = ds.U.sel(ht=3000, method="nearest"); v_3km = ds.V.sel(ht=3000, method="nearest")
u_5km = ds.U.sel(ht=5000, method="nearest"); v_5km = ds.V.sel(ht=5000, method="nearest")

ushear_2km = u_2km - u_100m; vshear_2km = v_2km - v_100m
ushear_3km = u_3km - u_100m; vshear_3km = v_3km - v_100m
ushear_5km = u_5km - u_100m; vshear_5km = v_5km - v_100m
ushear_35  = u_5km - u_3km ; vshear_35  = v_5km - v_3km

ushear_t   = np.vstack([ushear_2km, ushear_3km, ushear_5km])
vshear_t   = np.vstack([vshear_2km, vshear_3km, vshear_5km])



# time_grid, height_grid = np.meshgrid(ds.time, np.array([2000, 3000, 5000]), indexing="ij")

# fig, ax = plt.subplots(figsize=(14, 7))
# qv = ax.quiver(time_grid, height_grid, ushear_t, vshear_t, scale=180, width=0.005)
# qk = ax.quiverkey(qv, 0.175, 0.9, 10, '10 m/s', labelpos='E', coordinates='figure')

time_idx = pd.to_datetime(ds.time.values)  # 使用 pandas.to_datetime 轉換為 datetime
formatted_time = time_idx.strftime('%H%M')  # 轉換為 'HH:MM' 格式

# # 設置 X 軸刻度，將時間轉換為 datetime 格式
# ax.set_xticks(time_idx[::2])  # 每隔兩個點設置一個刻度

# # 格式化 X 軸的刻度顯示
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# ax.set_ylabel("Height (m)", fontsize=15)
# ax.tick_params(axis="x", labelsize=15)
# ax.tick_params(axis="y", labelsize=15)
# ax.set_ylim(0, 7000)
# ax.set_title("Wind Profile (2022-06-29 14:00 - 20:00)")
# # ax.set_xticks(formatted_time)  # 減少 X 軸刻度
# ax.tick_params(axis="x", rotation=45)
# plt.tight_layout()
# plt.savefig("/mnt/e/workspace/pic/20220629/windshear.png", dpi=300)

from metpy.plots import Hodograph
from metpy.units import units
heights = np.array([100, 2000, 3000, 5000])  # 高度 (m)

for i in range(len(ds.time)):
    u_wind = np.array([u_100m[i], u_2km[i], u_3km[i], u_5km[i]]) * units.meter / units.second
    v_wind = np.array([v_100m[i], v_2km[i], v_3km[i], v_5km[i]]) * units.meter / units.second
    time = formatted_time[i]
    print(u_wind, v_wind)
    fig, ax = plt.subplots(figsize=(6, 6))

    # 創建 Hodograph 物件
    hod = Hodograph(ax, component_range=10)  # 設定範圍
    hod.add_grid(increment=2, ls='-', lw=1.5, alpha=0.5)
    hod.add_grid(increment=1, ls='--', lw=1, alpha=0.2)

    hod.ax.set_box_aspect(1)
    hod.ax.set_yticklabels([])
    hod.ax.set_xticklabels([])
    hod.ax.set_xticks([])
    hod.ax.set_yticks([])
    hod.ax.set_xlabel(' ')
    hod.ax.set_ylabel(' ')

    plt.xticks(np.arange(0, 0, 1))
    plt.yticks(np.arange(0, 0, 1))
    for i in range(2, 12, 2):
        hod.ax.annotate(str(i), (i, 0), xytext=(0, 2), textcoords='offset pixels',
                    clip_on=True, fontsize=12, weight='bold', alpha=0.3, zorder=0)
    for i in range(2, 12, 2):
        hod.ax.annotate(str(i), (0, i), xytext=(0, 2), textcoords='offset pixels',
                    clip_on=True, fontsize=12, weight='bold', alpha=0.3, zorder=0)

    # 繪製 Hodograph
    hod.plot_colormapped(u_wind, v_wind, heights, cmap="rainbow")
    ax.set_title(f"{time} LST")

    # 顯示圖表
    plt.savefig(f"/mnt/e/workspace/pic/20220629/windrose{time}.png", dpi=300)



# C/delta_u
C_phase1 = 6.32
C_phase2 = 11.1

wspd2km, wdir2km = winddirspd(ushear_2km, vshear_2km)
nwspd2km         = findnormalwindspeed(shearwdir=wdir2km, shearwspd=wspd2km, Cdir=141.62)

wspd3km, wdir3km = winddirspd(ushear_3km, vshear_3km)
nwspd3km         = findnormalwindspeed(shearwdir=wdir3km, shearwspd=wspd3km, Cdir=141.62)

wspd5km, wdir5km = winddirspd(ushear_5km, vshear_5km)
nwspd5km         = findnormalwindspeed(shearwdir=wdir5km, shearwspd=wspd5km, Cdir=141.62)

print(vshear_2km, vshear_3km, vshear_5km)

delta_u2km = np.sqrt(vshear_2km**2)
delta_u3km = np.sqrt(vshear_3km**2)
delta_u5km = np.sqrt(vshear_5km**2)

fig, ax = plt.subplots(figsize=(8, 4))
# ax.plot(time_idx, np.repeat(C_phase2, 37), label="C")
ax.plot(time_idx, nwspd2km , label=r'$\Delta U_{\max 2km}$')
ax.plot(time_idx, nwspd3km , label=r'$\Delta U_{\max 3km}$')
ax.plot(time_idx, nwspd5km , label='$\Delta U_{\max 5km}$')

time_idx = pd.to_datetime(ds.time.values)  # 使用 pandas.to_datetime 轉換為 datetime
formatted_time = time_idx.strftime('%H:%M')  # 轉換為 'HH:MM' 格式

# 設置 X 軸刻度，將時間轉換為 datetime 格式
ax.set_xticks(time_idx[::2])  # 每隔兩個點設置一個刻度
ax.grid()

# 格式化 X 軸的刻度顯示
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

ax.set_ylim(0,12)
ax.tick_params(axis="x", labelsize=15)
ax.tick_params(axis="y", labelsize=15)
ax.set_title("Wind Profile (2022-06-29 14:00 - 20:00)")
# ax.set_xticks(formatted_time)  # 減少 X 軸刻度
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.legend()
plt.savefig("/mnt/e/workspace/pic/20220629/RKWnormalUV_XINWU.png", dpi=300)
'''
# endregion

# region
'''
###############################################
# plot CV from mosaic2D SRWIND rotational wind
###############################################
coord = (120.30, 121.10, 23.9, 25.1)
PPwdir= 321.46; PPwspd = 6.32
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
height = [2.5]

for alt in height:
    for i in range(12, 36):

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        w_ret_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid()

        wr = fileread(w_ret_dir)
        dw = wr.readwretrie_nc(altitude=alt)
        SR_U = dw.SR_U.values[0]
        SR_V = dw.SR_V.values[0]
        SR_WS= np.sqrt(SR_U ** 2 + SR_V ** 2)
        rotation_u, rotation_v = calrotationalwind(dw=dw, u=SR_U, v=SR_V, dx=1000, tol=1e-6)
        rotation_WS            = np.sqrt(rotation_u ** 2 + rotation_v ** 2)

        skip = 5
        map_plot = Mapplot()
        ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=True, title=f"{str(dw.altitude.values)} km", time_str=time_str, size=17)
        ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[0:-1], lon=dw.longitude.values[0:-1], var=rotation_WS, cmap="Reds", levels=np.arange(5, 13, 1), extend="max", overlay=True, ax=ax)
        ax       = map_plot.plot_map_OBS(lat=dw.latitude.values[0:-1:skip], lon=dw.longitude.values[0:-1:skip], u=rotation_u[::skip, ::skip], v=rotation_v[::skip, ::skip], windbar_on=True, overlay=True, ax=ax)
        map_plot.save_map(ax, filename=f"20220629{lst_time}_{str(dw.altitude.values)}km_SRROTATE.png")

'''
# endregion