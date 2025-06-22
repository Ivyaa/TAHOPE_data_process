import os
import gc
import pandas as pd
import matplotlib.pyplot as plt

# self-utils
from config.pathconfig    import *
from config.othsettings   import *
from ioread.SurfaceRead   import *
from utils.utc2lst        import *
from plot.MAPPLOT         import *


coord = (120.30, 121.10, 23.9, 25.1)
target_cities = ['雲林縣', '彰化縣', '臺中市', '南投縣', '桃園市', '苗栗縣', '新竹縣', '新竹市']
# target_cities = ['臺南市']
target_var    = ['STID', 'STNM', 'LAT', 'LON', 'ELEV', 'WDIR', 'WDSD', 'TEMP', 'HUMD', 'PRES', 'CITY', 'WS15M', 'WD15M']
target_lat    = [23.6, 25.2]
target_lon    = [120.00, 121.20]

levels = np.arange(25, 35, 1)
cmap   = plt.get_cmap('jet')
norm   = BoundaryNorm(boundaries=levels, ncolors=cmap.N)
##############################################################
# for reading the STAOBS and draw the spot map (auto-station)
##############################################################

# catch the file only start with the specific date and sorted
files_obs   = sorted(list(STA_OBS.glob("20220629*")))
files_obs10 = sorted(list(STA_OBS2.glob("20220629*")))
files_rain  = sorted(list(RAINS.glob("20220629*")))
# files_cv    = sorted(os.listdir(MOSAIC2D))
# files_cv    = sorted(list(SPOL_GRID.glob("*nc")))
files_obs   = sorted(list(STA_OBS28.glob("20220625*")))

# region

for i in range(20, len(files_obs)-65):

    print(f"Processing file: {files_obs[i]}")
    file_obs = str(STA_OBS / files_obs[i])

    # read obs data and do nn_interpolation
    fm = SURFOBS(file_obs)
    df = fm.read_mdf(filtered_city=target_cities, filtered_var=target_var)
    
    # get lst time (TYPE: hhmm)
    lst_time = utc2lst(filename=str(files_obs[i]))
    # print(lst_time)

    # set map and plot
    map_plot = Mapplot(coordinates=coord)
    ax, sc   = map_plot.plot_map_scatter(lat_ss=df['LAT'].values, lon_ss=df['LON'].values, data_ss=df['TEMP'].values, cmap=cmap, norm=norm)
    
    # set colorbar
    cbar = plt.colorbar(sc, ax=ax, boundaries=levels, ticks=levels, orientation='vertical', shrink=0.8, pad=0.02)
    cbar.set_label("TEMP", fontsize=12)
    
    # set canvas title and others
    templates["map_style"]["time_title"] = f"{lst_time} LST"
    apply_canvas_format(ax, templates["map_style"])

    plt.show()

    break


# endregion

##############################################################
# for reading the STAOBS and do the nn_interpolate from metpy
##############################################################

