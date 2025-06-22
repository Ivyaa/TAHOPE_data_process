import numpy as np
from matplotlib.colors  import ListedColormap
from matplotlib.colors  import BoundaryNorm

# radar another contourf
radar_cf_color = ["#e3e3e3"]
radar_cf_cmap  = ListedColormap(radar_cf_color)

# radar ref_max contourf
radar_color =["#84C1FF","#2894FF","#0066CC","#28FF28","#00BB00","#009100",\
            "#F9F900","#FF8000","#FF5151","#EA0000","#AE0000","#FF44FF",\
            "#D200D2","#750075"]
radar_colormap = ListedColormap(radar_color)
clevel =[5,10,15,20,25,30,35,40,45,50,55,60,65,70,75]
cnorm=BoundaryNorm(clevel,len(clevel))

# VEL for contourf
vel_color = [
    # "#0066CC", "#2894FF", "#84C1FF",  # 负值：蓝色
    "#ccfcfa", "#a8f7f3", "#64dde3", "#27abc2", "#2787c2", "#035996", "#02259c", "#1e006b", # 负值：绿色
    "#d4d4d4",                        # 0值：白色
    "#a80000","#fc0303", "#ff7817", "#fc9942", "#ffbf40", "#fce88b", "#f9fcb3" # 正值：黄色
]
vlevel = [-21, -17, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 17]
vel_colormap = ListedColormap(vel_color)
vnorm = BoundaryNorm(vlevel, len(vlevel))

#"#3f7fbf", 
ZDR_color = [
    "#3962ad", "#284efa", "#1c35a6", "#26357a", "#0f1c59", "#6b756f", "#95a2a6",\
    "#51875a", "#309c42", "#619c3a", "#82cc52", "#ccba41", "#f7dc28", "#f7fa37", "#f7b816",\
    "#ff925c", "#eb6f4d"#, "#fc6108", "#fc0808", "#f50a7b", "#fa61ab", "#ff8fd2", "#fcd6c5"
]

zlevel = [-2, -1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1, 1.5, 2, 2.5, 3, 4, 5]
ZDR_colormap = ListedColormap(ZDR_color)
znorm = BoundaryNorm(zlevel, len(ZDR_color))

RHO_color = [
    "#453d69", "#07045c", "#154cd6", "#89d6fa", "#073aa8", "#076b22", "#0aa132", "#98c95b",\
    "#eddc45", "#ecfc0d", "#ff9c6b", "#e3b44f", "#c49329", "#a33e3e", "#b51919", "#f70707",\
    "#d40890"
]

rlevel = [0, 0.7, 0.8, 0.85, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.975, 0.98, 0.995, 1.1]
RHO_colormap = ListedColormap(RHO_color)
rnorm = BoundaryNorm(rlevel, len(RHO_color))

PID_color = [
    "#ffffff", "#dbdbd7", "#fae6cd", "#f59e31", "#ab6d1f", "#fc2323", "#f5fc12", "#0cf728",\
    "#09b809", "#017801", "#05c5fa", "#0289d1", "#5943a3", "#f0c7fc", "#ffa1d1", "#ffffff",\
    "#9e999c", "#bf5093","#1905f7"
]

plevel = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
PID_colormap = ListedColormap(PID_color)
pnorm = BoundaryNorm(plevel, len(PID_color))
ptick = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5]
ptickslab = ["None", "CldDrops", "Drizzle", "LtRain", "ModRain", "HvyRain", "Hail", "RainHail", 
             "GrSmHail", "GrRain", "Drysnow", "WetSnow", "Ice", "Irreglce", "Slw", "Insects", "2ndTrip", "Clutter", "Sature"]

KDP_color = [
    "#3f7fbf", "#3962ad", "#284efa", "#1c35a6", "#26357a", "#0f1c59", "#6b756f", "#95a2a6",\
    "#51875a", "#309c42", "#619c3a", "#82cc52", "#ccba41", "#f7dc28", "#f7fa37", "#f7b816",\
    "#ff925c", "#eb6f4d", "#fc6108", "#fc0808", "#f50a7b", "#fa61ab", "#ff8fd2", "#fcd6c5"
]

klevel = np.arange(-1, 4.1, 0.1)
KDP_colormap = "jet"
knorm = BoundaryNorm(klevel, len(klevel))

import matplotlib.colors as mcolors
# classification
# 對應分類的 colormap（要與圖片一致）
cmap_clfi = mcolors.ListedColormap(['#2794DB', '#FFF7A2', '#FFAE52', '#E60000'])  # NE, WE, ST, SC, MC, DC

# obs temp
cold_pool_temp = "Blues_r"
cold_pool_temp_levels = np.arange(-10., 1, 1)

# obs pressure
cold_pool_p = "Reds"
cold_pool_p_levels = np.arange(0, 3.75, 0.25)

# wretrieve speed
wind_speed_cmap = "Spectral_r" 
wind_speed_levels = np.arange(0, 26, 2)

# DIV
DIV_cmap = "RdYlBu" 
DIV_levels = np.arange(-5, 6, 1)

# vorticity/HAD
VOR_cmap = "RdYlGn_r"
VOR_levels = np.arange(-18, 19, 3)

# VAD
VAD_cmap = "PRGn"
VAD_levels = np.arange(-18, 19, 3)

# STR
STR_cmap = "BrBG"
STR_levels = np.arange(-18, 19, 3)

# TLT
TLT_cmap =  "twilight_shifted"
TLT_levels = np.arange(-18, 19, 3)

# total + vorticity
VOR_cmap = "RdYlGn_r"
VOR_levels = np.arange(-18, 21, 3)

VORR_cmap = "bwr"
VORR_levels = np.arange(-7, 8, 1)

W_cmap = "coolwarm"
W_levels = np.arange(-10, 16, 3)

# WIDTH color
wid_cmap = "RdGy_r"
wid_levels = np.arange(0, 11, 1)

# dictionary of plot_canvas_settings
templates = {
    "default": {
        "title": None,
        "xlabel": None,
        "ylabel": None,
        "title_fontsize": 14,
        "label_fontsize": 12,
        "tick_fontsize": 10,
        "xticks": None,
        "yticks": None,
        "title_loc": "center",
    },
    "map_style": {
        "title": "Temp",
        "xlabel": "Longitude",
        "ylabel": "Latitude",
        "title_fontsize": 16,
        "label_fontsize": 14,
        "tick_fontsize": 12,
        "title_loc": "left",
    }
}
