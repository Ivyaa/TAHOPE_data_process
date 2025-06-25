import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import gc
import psutil  # 用於監控記憶體使用量

from pathconfig import *
from read_utils import *
from plot_utils import *
from plot_settings import *
from tool_utils import utc2lst, filter_files_by_time, calculate_bearing, GIFmake

print(calculate_bearing(lat1=24.24, lon1=120.64, lat2=24.40, lon2=120.50))
# # cal memory(just for test)
# # if you want to use it just open it
# process = psutil.Process()

# def print_memory_usage():
#     mem_info = process.memory_info()
#     print(f"Memory usage: {mem_info.rss / 1024 ** 2:.2f} MB") 
coord = (120.30, 121.10, 23.9, 25.1)
# region

###############################################
# plot CV from mosaic2D
###############################################
'''
# read radar file
files = os.listdir(MOSAIC2D)


for file in files[12:80]:
    
    print(f"Processing file: {file}")
    # print_memory_usage()

    # convert to file_path(str)
    file_dir = MOSAIC2D / file
    file_dir = str(file_dir)

    # get lst time
    lst_time = utc2lst(filename=str(file))
    time_str = lst_time[-4::] + "LST" + " " + lst_time[-8:-6] + "/" + \
               lst_time[-6:-4] + "/" + lst_time[0:4]

    # need to call object first then 
    # give the other instructions
    # you can read csv, mdf, mosaic2D in this fr object
    # but only one file can be read
    fr = fileread(file_dir)
    f  = fr.readCOMPREF2D()

    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, title="CV", time_str=time_str, size=17)
    map_plot.save_map(ax, filename=f"{lst_time}.png")
    
    # release memory
    del fr, f, map_plot, ax, lst_time, time_str
    gc.collect()

    # print_memory_usage()
'''
# endregion


# region
'''
#####################################################
# plot PPI any degree from Spol using xradar(xarray)
#####################################################
files = os.listdir(SPOL_SUR)
files = filter_files_by_time(files, end_time="1230")
files = sorted(files)
var   = "WIDTH"
for file in files[31:58]:
    # file = "cfrad.20220629_043650.397_to_20220629_044252.173_SPOL_PrecipSur1_SUR.nc"
    print(f"Processing file: {file}")
    # try:
    # convert to file_path(str)
    file_dir = SPOL_SUR / file
    file_dir = str(file_dir)
    
    # need to call object first then 
    # give the other instructions
    # sweep_0 -> 0.5 degree; sweep_1 -> 1 degree; 
    # sweep_2 -> 1.5 degree; sweep_3 -> 2 degree
    fr = fileread(file_dir)
    f  = fr.readcfrad(sweep="sweep_4")
    Deg= np.round(f.radar['elevation'].values[0], 1)

    # get lst time
    lst_time  = utc2lst(filename=str(file))
    save_str  = lst_time[:-3] + lst_time[-2::]
    title_str = f"SPol {Deg} Deg " + str(lst_time) + \
                "\n" + "reflectivity factor"

    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_PPISPolcontourf(f=f, coordinates=coord, var=var, cmap=wid_cmap, levels=wid_levels, norm=None, title=title_str, time_str=None, size=17)
    map_plot.save_map(ax, filename=f"{save_str}{var}degree3.png")

    del fr, f, lst_time, title_str, save_str, ax
    gc.collect()
    # except: 
    #     print(f"Processing file: {file} no this angle")
'''
# endregion

# region
#########################################################
# plot PPI any degree from Spol using xradar(xarray)
# plot overlay using contourf and contour
# please let overlay=True and let ax=ax(the name you use)
#########################################################
'''
files = os.listdir(SPOL_SUR)
files = filter_files_by_time(files, end_time="1230")

for file in files[:]:
    # file = "cfrad.20220629_043650.397_to_20220629_044252.173_SPOL_PrecipSur1_SUR.nc"
    print(f"Processing file: {file}")
    try:
        # convert to file_path(str)
        file_dir = SPOL_SUR / file
        file_dir = str(file_dir)

        # need to call object first then 
        # give the other instructions
        # sweep_0 -> 0.5 degree; sweep_1 -> 1 degree; 
        # sweep_2 -> 1.5 degree; sweep_3 -> 2 degree
        fr = fileread(file_dir)
        f  = fr.readcfrad(sweep="sweep_0")
        Deg= np.round(f.radar['elevation'].values[0], 1)

        # get lst time
        lst_time  = utc2lst(filename=str(file))
        save_str  = lst_time[:-3] + lst_time[-2::]
        title_str = f"SPol {Deg} Deg " + str(lst_time) + \
                    "\n" + "Radial wind + 45dBZ REF"

        # set map and plot
        map_plot = Mapplot()
        ax       = map_plot.plot_map_PPISPolcontourf(f=f, var="VEL", cmap=vel_colormap, levels=vlevel, norm=vnorm, extend="both", coordinates=coord, title=title_str, time_str=None, size=17)
        # map_plot.save_map(ax, filename=f"{save_str}_VEL.png")
        ax       = map_plot.plot_map_PPISPolcontour(f=f, var="DBZ", colors="black", linewidth=2, coordinates=coord, title=None, time_str=None, overlay=True, ax=ax)
        map_plot.save_map(ax, filename=f"{save_str}.png")

        del fr, f, lst_time, title_str, save_str, ax
        gc.collect()
    except ValueError: 
        print(f"Processing file: {file} no this angle")
        continue
'''
# endregion

# region

###############################################
# plot CV from mosaic2D
###############################################
coord = (120.30, 121.10, 23.8, 25.13)
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))

for file in files[18:36]:
    
    print(f"Processing file: {file}")
    # print_memory_usage()

    # convert to file_path(str)
    file_dir = str(file)

    # get lst time
    lst_time = utc2lst(filename=str(file))
    time_str = f"{lst_time}LST 06/29/2022"

    # need to call object first then 
    # give the other instructions
    # you can read csv, mdf, mosaic2D in this fr object
    # but only one file can be read
    fr = fileread(file_dir)
    f  = fr.readSPolgrid(CVon=False, alt=10.0)

    # set map and plot
    map_plot = Mapplot()
    ax       = map_plot.plot_map_refmax(f=f, coordinates=coord, contour_on=False, title="CV", time_str=time_str, size=17)
    # ax.scatter(120.64, 24.24, marker='.', color='blue', s=500, transform=ccrs.PlateCarree(), zorder=501)
    # ax.scatter(120.50, 24.40, marker='.', color='blue', s=500, transform=ccrs.PlateCarree(), zorder=501)

    map_plot.save_map(ax, filename=f"20220629{lst_time}_10km.png")
    
    # release memory
    del fr, f, map_plot, ax, lst_time, time_str
    gc.collect()
    # print_memory_usage()

# endregion

# region
# GIFmake(input_folder="/mnt/e/workspace/pic/20220629/SPol/PPI/CV2km_allrange/", output_gif="/mnt/e/workspace/pic/20220629/20220629.gif", duration=400)
# endregion
