import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import gc
import glob
import psutil  # 用於監控記憶體使用量

from pathconfig import *
from read_utils import *
from plot_utils import *
from plot_settings import *
from tool_utils import utc2lst, filter_files_by_time, compute_cfad_percentage_RHI, find_RHIline
from pyproj import Geod

files_RHI2 = sorted(list(RHI2.glob("*nc")))
files_RHI0 = sorted(list(RHI0.glob("*nc")))
files_cv    = sorted(list(SPOL_GRID.glob("*nc")))

coord = (120.20, 121.10, 23.8, 25.2)
spol_lat = 24.8190879821777
spol_lon = 120.90746307373

# region
###########################################
# RHI range of calculate the cfads
###########################################
'''
for i in range(18, 20):

    # 18-20: 50-110; 20-22: 40-110
    # file use
    file     = str(files_cv[i])
    print(file)
    
    fileRHI2 = str(files_RHI2[i+19])
    print(fileRHI2)

    fileRHI0 = str(files_RHI0[i])
    print(fileRHI0)

    # fileread
    lst_time = utc2lst(filename=file)
    time_str = f"{lst_time}LST 06/29/2022"

    fr = fileread(file)
    f  = fr.readSPolgrid(CVon=True)

    frhi = fileread(fileRHI0)

    map_plot = Mapplot()
    ax       = map_plot.plot_map_OBS(coordinates=coord, lat=f.lat, lon=f.lon, var=f.data, contour_on=False, extend="neither", cmap=radar_colormap, levels=clevel)
    geod = Geod(ellps="WGS84")
    radii_km = np.arange(10, 111, 10)  # 每10公里一圈，最大到120公里
    angles_deg = np.linspace(160, 250, 200)  # 半圓角度，取更多點使圓平滑
    for angle in range(0, 12):
        sweepnum = "sweep_"+str(angle)
        try:
            ff_rhi   = frhi.readcfradRHI(sweep=sweepnum, var='DBZ')
            anglenew = ff_rhi.angle

            if anglenew < 170 or anglenew > 240:
                continue

            end_lat, end_lon     = find_RHIline(angle=anglenew, range=120)
            end_lat60, end_lon60 = find_RHIline(angle=anglenew, range=30)
            end_lat80, end_lon80 = find_RHIline(angle=anglenew, range=110)
            ax.plot([spol_lon, end_lon], [spol_lat, end_lat], color='black', linestyle='-', transform=ccrs.PlateCarree(), zorder=130)
            # ax.plot([end_lon60, end_lon80], [end_lat60, end_lat80], color='#fffd9c', linestyle='-', linewidth=4, transform=ccrs.PlateCarree(), zorder=130)
            ax.text(end_lon, end_lat, f"{anglenew:.0f}°", fontsize=12, ha='center', va='top', color='black', fontweight='bold', transform=ccrs.PlateCarree(), zorder=130)
        except:
            continue


    for radius in radii_km:
        lats_ring = []
        lons_ring = []
        for az in angles_deg:
            lon, lat, _ = geod.fwd(spol_lon, spol_lat, az, radius * 1000)  # 單位：公尺
            lats_ring.append(lat)
            lons_ring.append(lon)
        ax.plot(lons_ring, lats_ring, linestyle='--', color='black', linewidth=0.8, transform=ccrs.PlateCarree(), zorder=120)

    map_plot.save_map(ax, filename=f"RHI00_range{lst_time}.png")
'''
# endregion


# region
###########################################
# RHI CFADs line_ver
###########################################

varlst   = ["DBZ", "RHOHV", "KDP", "ZDR"]
colorlst = ["#ff8282", "#ffc182", "#fff982", "#dec104", "#9fff82", "#05ab6b", "#82e0ff", 
            "#82b8ff", "#bc82ff", "#420ffa", "#ff82d1", "#8003ad", "#99028a"] 

for i in range(30, 31):

    # 18-20: 50-110; 20-22: 40-110
    # file use
    file     = str(files_cv[i])
    print(file)
    
    fileRHI2 = str(files_RHI2[i+19])
    print(fileRHI2)

    fileRHI0 = str(files_RHI0[i])
    print(fileRHI0)

    # fileread
    lst_time = utc2lst(filename=file)
    time_str = f"{lst_time}LST 06/29/2022"

    fr = fileread(file)
    f  = fr.readSPolgrid(CVon=True)

    frhi = fileread(fileRHI0)
    frhi2 = fileread(fileRHI2)

    rmin=40; rmax=60
    

    for i in range(20, 110, 10):
        rmin = i
        rmax = i + 10

        median_avg = []
        plt.figure(figsize=(5, 8))
        number_c = 0
        for angle in range(0, 12):
            try:
                sweepnum = "sweep_"+str(angle)
                ff_rhi   = frhi.readcfradRHI(sweep=sweepnum, var='RHOHV')
                anglenew = ff_rhi.angle    
            except:
                continue

            if anglenew < 183 or anglenew > 220:
                continue
            number_c = number_c + 1
            R        = ff_rhi.R[:, 0:-1]
            z        = ff_rhi.z[:, 0:-1]
            data     = ff_rhi.data
            # print(np.shape(z), np.shape(R), np.shape(data))

            z_bins, median_profile = compute_median_profile(R, z, data, r_min=rmin, r_max=rmax, percentile=50)
            median_avg.append(median_profile)
            # plt.plot(median_profile[2::], z_bins[2:-1], marker='o', color=colorlst[number_c-1], label=str(anglenew))

        number_c = 12
        for angle in range(0, 12):
            
            try:
                sweepnum = "sweep_"+str(angle)
                ff_rhi   = frhi2.readcfradRHI(sweep=sweepnum, var='RHOHV')
                anglenew = ff_rhi.angle
            except:
                continue

            if anglenew < 183 or anglenew > 220:
                continue
            number_c = number_c - 1
            R        = ff_rhi.R[:, 0:-1]
            z        = ff_rhi.z[:, 0:-1]
            data     = ff_rhi.data
            # print(np.shape(z), np.shape(R), np.shape(data))

            z_bins, median_profile = compute_median_profile(R, z, data, r_min=rmin, r_max=rmax, percentile=50)
            median_avg.append(median_profile)
            # plt.plot(median_profile[2::], z_bins[2:-1], marker='^', color=colorlst[number_c + 1], label=str(anglenew))


        var_avg = np.nanmean(median_avg, axis=0)
        plt.plot(var_avg[2::], z_bins[2:-1], marker='*', color="black", linewidth=2, markersize=10, label="Average value")
        
        plt.xlabel("RHOHV")
        plt.ylabel("Height (km)")
        plt.title(f"Median RHOHV Profile ({str(rmin)}-{str(rmax)} km)")
        plt.grid(True)

        plt.xlim(0.8, 1.05)
        plt.ylim(0, 18)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"/mnt/e/workspace/pic/20220629/CFADanglesRHI/RHIcfads/RHIcfadsRHOHV_{str(rmin)}_{str(rmax)}_median_{lst_time}.png", dpi=300)
        print(f"RHIcfadsDBZ_{str(rmin)}_{str(rmax)}_999per_{lst_time}.png already saved")

# endregion