#terrain
from pathconfig import *
from read_utils import get_terrain
from plot_settings import *

# math utils
import numpy as np

# scipy
from scipy.stats import pearsonr, spearmanr

#matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.lines  as mlines
from matplotlib.colors  import ListedColormap
from matplotlib.colors  import BoundaryNorm
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

#cartopy
import cartopy.crs     as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner  import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature        import ShapelyFeature
from cartopy.io.shapereader import Reader

from metpy.units import units

from tool_utils import classificationofCuSt

# terrain data
terrain = get_terrain(str(TERRAIN))

class Mapsetting:
    '''
    The terrain file and high resolution shape file has existed
    Please download and change the pathconfig if you don't have the file
    Or you can change the file you want to utilize from the terrain
    '''
    def __init__(self):
        self.shape_file  = str(SHAPE)
        
    def Mapset(self, coordinates=(120,122,22,25), mapdefault=False, shapefile=True, radar_loc=True):
        '''
        coordinates: tuple {using -> ()}, setting the fig range
        mapdefault: using cartopy building map
        shapefile: using detailed taiwan shapefile
        '''
        coordinates = coordinates
        myproj = ccrs.PlateCarree()

        #canva size and coastline
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(1,1,1, projection=myproj)
        
        # terrain setting
        # cmap = 'binary'
        # tr = ax.contourf(terrain.lon,terrain.lat,terrain.data, cmap='binary', levels=range(0,4000,200),extend="max")

        # tr = ax.contourf(terrain.lon,terrain.lat,terrain.data, colors=["#ffffff","#ffffff"], levels=range(500,4100,3500),extend="max",zorder=110)
        # ax.contour(terrain.lon,terrain.lat,terrain.data,colors='#616161',levels=[1500])
        # ax.contour(terrain.lon,terrain.lat,terrain.data,colors='#a3a3a3',levels=[500])
        # ax.contour(terrain.lon,terrain.lat,terrain.data,colors='#a3a3a3',levels=[200])

        #shapefile
        if shapefile: 
            shape_file=("/mnt/e/workspace/data/COUNTY_MOI_1090820.shp")                                              #cccaca
            shape_feature = ShapelyFeature(Reader(self.shape_file).geometries(), myproj,facecolor="none", edgecolor='black')
            ax.add_feature(shape_feature, zorder=104, linewidth=1.5)
        
        if mapdefault:
            ax.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
            # ax.add_feature(cfeature.LAND, facecolor='lightgray')
            # ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        
        if radar_loc:
            ax.scatter(120.90746307373, 24.8190879821777, marker='*', color='blue', s=500, transform=ccrs.PlateCarree(), zorder=501)
            # ax.scatter(120.5795363687824, 24.144315378823823, marker='*', color='black', s=500, transform=ccrs.PlateCarree(), zorder=501)
            # ax.scatter(121.40040, 25.00420, marker='*', color='red', s=500, transform=ccrs.PlateCarree(), zorder=501)            
            # # ax.scatter(121.014219, 24.827853, marker='^', color='skyblue', s=500, transform=ccrs.PlateCarree(), zorder=501)
        #xy_tick and range setting
        ax.set_xlim(coordinates[0]-0.1, coordinates[1]+0.1)
        ax.set_ylim(coordinates[2]-0.1, coordinates[3]+0.1)

        lon_step = 0.2; lat_step = 0.2
        xticks = np.arange(120, 122 , lon_step)
        yticks = np.arange(22, 26 , lat_step)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        
        xlabels = [f"{x:.2f}°E" for x in xticks]
        ylabels = [f"{y:.2f}°N" for y in yticks]
        ax.set_xticklabels(xlabels, fontsize=10)
        ax.set_yticklabels(ylabels, fontsize=10)

        ax.set_xlim(coordinates[0]-0.1, coordinates[1]+0.1)
        ax.set_ylim(coordinates[2]-0.1, coordinates[3]+0.1)

        return ax

class Mapplot:
    '''
    This class utilizes Mapsetting to generate and customize maps for visualization.
    '''
    def __init__(self):
        # initialize mapsettion
        self.map_setting = Mapsetting()

    def plot_map_refmax(self, f, coordinates=None, title=None, time_str=None, mapdefault=False, shapefile=True, contour_on=False, overlay=False, ax=None, cb=None, **kwargs):
        '''
        Plot the map using the Mapsetting class.
        
        Parameters:
        - coordinates: tuple -> 地圖範圍 (min_lon, max_lon, min_lat, max_lat)
        - mapdefault: bool -> 是否使用 Cartopy 的默認圖層
        - shapefile: bool -> 是否加載高分辨率形狀檔案
        '''
        if coordinates is None:
            coordinates = (120, 122, 22, 25)

        if overlay:
            ax = ax
        else:
            # use class Mapsetting to produce basic
            ax = self.map_setting.Mapset(
                coordinates=coordinates, 
                mapdefault=mapdefault, 
                shapefile=shapefile
            )

        if contour_on:
            cl = ax.contour(f.lon, f.lat, f.data
                            ,[45],colors='red',linewidths=3
                            ,zorder=110, **kwargs)
        else:

            cb = ax.contourf(f.lon, f.lat, f.data
                            ,cmap=radar_colormap,levels=clevel,norm=cnorm
                            ,zorder=105, **kwargs)
            # cb = ax.contourf(f.lon, f.lat, f.data
            #                 ,cmap="jet",levels=np.arange(-1, 4.1, 0.1)
            #                 ,zorder=110, **kwargs)

        if cb is not None: #clevel ticks_str
            self.set_colorbar(cb=cb, cb_name="dBZ", ticks_str=clevel)

        # set title
        if title:
            self.set_title(ax, title=title, **kwargs)
        
        # set time title
        if time_str:
            self.set_time_title(ax, time_str=time_str, **kwargs)
        
        
        self.set_grid(ax=ax)
        plt.tight_layout()

        return ax
    
    def plot_map_PPISPolcontourf(self, f, var="DBZ", coordinates=None, title=None, time_str=None, 
                                 cmap=radar_colormap, levels=clevel, norm=cnorm, 
                                 mapdefault=False, shapefile=True, grid_on=True, overlay=False,
                                 extend="both", ax=None, **kwargs):
        
        if coordinates is None:
            coordinates = (120, 122, 22, 25)

        if overlay is False:
            # use class Mapsetting to produce basic
            ax = self.map_setting.Mapset(
                coordinates=coordinates, 
                mapdefault=mapdefault, 
                shapefile=shapefile
            )
        else:
            ax = ax

        cb = ax.contourf(f.lon, f.lat, f.radar[var].values
                            ,cmap=cmap,levels=levels,norm=norm
                            ,extend=extend,zorder=0)

        if cb:
            self.set_colorbar(cb=cb, ticks_str=levels, cb_name=str(var))

        # set title
        if title:
            self.set_title(ax, title=title, **kwargs)
        
        # set time title
        if time_str:
            self.set_time_title(ax, time_str=time_str, **kwargs)

        if grid_on:
            self.set_grid(ax, **kwargs)

        plt.tight_layout()

        return ax
    
    def plot_map_PPISPolcontour(self, f, var="DBZ", coordinates=None, title=None, time_str=None, 
                                 colors="black", linewidth=1,
                                 mapdefault=False, shapefile=True, grid_on=True, overlay=False,
                                 ax=None, **kwargs):
        
        if coordinates is None:
            coordinates = (120, 122, 22, 25)

        if overlay is False:
            # use class Mapsetting to produce basic
            ax = self.map_setting.Mapset(
                coordinates=coordinates, 
                mapdefault=mapdefault, 
                shapefile=shapefile
            )
        else:
            ax = ax

        cr = ax.contour(f.lon, f.lat, f.radar[var].values
                            ,[45],colors=colors,linewidths=linewidth
                            ,zorder=100)

        # set title
        if title:
            self.set_title(ax, title=title, **kwargs)
        
        # set time title
        if time_str:
            self.set_time_title(ax, time_str=time_str, **kwargs)

        if grid_on:
            self.set_grid(ax, **kwargs)

        plt.tight_layout()

        return ax

    def plot_map_OBS(self, lat, lon, var=None, u=None, v=None, threshold=0, coordinates=None, title=None, time_str=None, mapdefault=False, shapefile=True
                     , linestyles='-', colors="red", cmap=cold_pool_temp, levels=cold_pool_temp_levels, zorder=111, contour_on=False, scatter_on=False, windbar_on=False, overlay=False, ax=None, **kwargs):
        '''
        Plot the map using the Mapsetting class.
        
        Parameters:
        - coordinates: tuple -> 地圖範圍 (min_lon, max_lon, min_lat, max_lat)
        - mapdefault: bool -> 是否使用 Cartopy 的默認圖層
        - shapefile: bool -> 是否加載高分辨率形狀檔案
        '''
        if coordinates is None:
            coordinates = (120, 122, 22, 25)

        if overlay:
            ax = ax
        else:
            # use class Mapsetting to produce basic
            ax = self.map_setting.Mapset(
                coordinates=coordinates, 
                mapdefault=mapdefault, 
                shapefile=shapefile
            )

        if scatter_on:
            mask_var = (var >= 5) & (var < 10)
            sc = ax.scatter(lon[mask_var], lat[mask_var], c='#f570fa', s=10, edgecolor='black', zorder=120)

            mask_var = (var >= 10) & (var < 15)
            sc = ax.scatter(lon[mask_var], lat[mask_var], c='#f570fa', s=50, edgecolor='black', zorder=120)

            mask_var = (var >= 15) & (var < 20)
            sc = ax.scatter(lon[mask_var], lat[mask_var], c='#f570fa', s=90, edgecolor='black', zorder=120)

            mask_var = var >= 20
            sc = ax.scatter(lon[mask_var], lat[mask_var], c='#f570fa', s=130, edgecolor='black', zorder=120)
            # sc = ax.scatter(lon, lat, c='red', s=90, zorder=120)

        elif windbar_on:
            u = np.array(u) * units.meter / units.second
            v = np.array(v) * units.meter / units.second

            wind_speed = np.sqrt(u**2 + v**2).magnitude
            mask_high = wind_speed > 8
            # mask_low = ~mask_high
            # ax.barbs(lon[mask_high], lat[mask_high], u[mask_high].magnitude, v[mask_high].magnitude,
            #  length=7, barbcolor='#02a7fa', zorder=103, linewidth=2.5)
            # # 黑色風羽
            # ax.barbs(lon[mask_low], lat[mask_low], u[mask_low].magnitude, v[mask_low].magnitude,
            #  length=7, barbcolor='black', zorder=103, linewidth=2.5)
            # 220/0.25/x=0.275 for retrieve wind ; 50 for station wind
            qv = ax.quiver(lon, lat, u, v, scale=220, scale_units='width', pivot='middle',width=0.005, zorder=121)
            qk = ax.quiverkey(qv, 0.275, 0.9, 10, '10 m/s', labelpos='E', coordinates='figure') #10 × 10⁻³ s⁻¹
            # qv = ax.quiver(lon[mask_high], lat[mask_high], u[mask_high], v[mask_high], scale=150, scale_units='width', color='orange', pivot='middle',width=0.005, zorder=121)
        elif contour_on:
            cr = ax.contour(lon, lat, var
                            ,threshold,colors=colors,linewidths=2
                            ,linestyles=linestyles, zorder=zorder, **kwargs)
            # ax.clabel(cr, inline=True, fmt="%1.1f", fontsize=8)
        else:
            cb = ax.contourf(lon, lat, var
                            ,cmap=cmap,levels=levels
                            ,zorder=108, **kwargs)
            if cb:
                self.set_colorbar(cb=cb, ticks_str=levels, **kwargs)

        

        # set title
        if title:
            self.set_title(ax, title=title, **kwargs)
        
        # set time title
        if time_str:
            self.set_time_title(ax, time_str=time_str, **kwargs)
        self.set_grid(ax=ax, **kwargs)
        plt.tight_layout()

        return ax
    def plot_map_prof(self, start_lat, start_lon, end_lat, end_lon, colors="black", linewidth=3, point_str=["A", "A'"], overlay=True, ax=None):

        ax.plot([start_lon, end_lon], [start_lat, end_lat], linewidth=linewidth, color=colors, zorder=600)

        # 標記起始點 A
        ax.text(
            start_lon,
            start_lat,
            point_str[0],
            fontsize=16,
            fontweight="bold", 
            color="black",
            bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"),
            ha="center",
            va="center",
            zorder=700,
        )

        # 標記終止點 B
        ax.text(
            end_lon,
            end_lat,
            point_str[1],
            fontsize=16,
            fontweight="bold", 
            color="black",
            bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"),
            ha="center",
            va="center",
            zorder=700,
        )
        return ax


    def set_colorbar(self, cb, cb_name=None, ticks_str=None, skip=1, **kwargs):

        clbar = plt.colorbar(cb,fraction=0.034)
        clbar.ax.set_title(cb_name)
        
        # skip the colorbar
        ticks = ticks_str
        clbar.set_ticks(ticks[::skip])
        clbar.ax.set_yticklabels([f"{tick:.1f}" for tick in ticks[::skip]])


    def set_title(self, ax, title=None, size=10, **kwargs):
        
        if title is not None:
            ax.set_title(title, loc="left", fontsize=size)
        
    def set_time_title(self, ax, time_str=None, size=10, **kwargs):

        if time_str is not None:
            ax.set_title(time_str, loc="right", fontsize=size)
    
    def set_grid(self, ax, linestyle="--", color="#cccaca", linewidth=1.5, **kwargs):

        ax.grid(which='major', color=color, linestyle=linestyle, linewidth=linewidth, zorder=1000)


    def save_map(self, ax, filename="output_map.png", filepath="/mnt/e/workspace/pic/20220629/"):
        '''
        Parameters:
        - ax: matplotlib Axes -> save fig
        - filename: str -> name of fig
        - filepath: str -> the path to save fig
        '''
        ax.figure.savefig(filepath + filename, dpi=300)
        plt.close('all')
        print(f"Map saved as {filename}")

class Analysisplot:

    def __init__(self, figsize=(10,10), nrows=1, ncols=1):

        self.fig, self.ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

    def plot_ana_scatter(self, x, y, color='blue', size=20, alpha=0.7, xlabel=None, ylabel=None, title=None
                         , corr_method=None, show_corr=False, set_label=True, overlay=True, ax=None
                         , xlim=None, ylim=None, dx=1, dy=1, **kwargs):
        '''
        draw scatter analysis graph and can calculate the R
        
        參數:
        - x: 1D array-like -> x 軸數據
        - y: 1D array-like -> y 軸數據
        - color: str 或 1D array-like -> 點的顏色
        - size: int 或 1D array-like -> 點的大小
        - alpha: float -> 點的透明度 (0~1)
        - xlabel: str -> x 軸標籤
        - ylabel: str -> y 軸標籤
        - title: str -> 圖表標題
        - corr_method: str -> 計算相關性的方法 ('pearson' 或 'spearman')
        - show_corr: bool -> 是否顯示相關係數在圖表中

        返回:
        - corr: float -> 計算的相關係數
        - p_value: float -> p-value
        '''
        # 計算相關係數
        if corr_method == 'pearson':
            corr, p_value = pearsonr(x, y)
        elif corr_method == 'spearman':
            corr, p_value = spearmanr(x, y)
        else:
            show_corr = False

        if overlay:
            ax = ax
        else:
            ax = self.ax

        ax.scatter(x, y, c=color, s=size, alpha=alpha, edgecolor='k')
        ax.grid(True, linestyle='--', alpha=0.5)

        # ax.set_xlim(-5, -0.2)
        # ax.set_ylim(-10, -0.5)

        if set_label:
            self.set_xylim(ax=ax, xlim=xlim, ylim=ylim, dx=dx, dy=dy)

        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12, **kwargs)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12, **kwargs)
        
        if title is not None:
            self.set_title(ax=ax, title=title, size=10)
        
        if show_corr:
            ax.text(0.05, 0.95, f'{corr_method.capitalize()} Corr: {corr:.3f}\nP-value: {p_value:.3e}',
                    transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

        return ax
    
    def plot_ana_linechart(self, ax, x, y, color='red', ylabel=np.arange(0, 100, 5), linewidth=2, skip=2, marker='o', alpha=1.0, labelbottom=False, title=None):

        ax.plot(x, y, linewidth=linewidth, color=color, marker=marker, alpha=alpha, markersize=10)

        if labelbottom is not False:
            ax.set_xticks(x[::skip])  # 每隔 0.5 小時顯示
            ax.set_xticklabels(
                [f"{t}" for t in x[::skip]],  # 每隔 0.5 小時標籤
                rotation=45,
                fontsize=15
            )

            ax.set_yticks(ylabel)  
            ax.set_yticklabels(
                [f"{t}" for t in ylabel],  
                fontsize=15
            )

        else:
            ax.set_xticks(x[::skip])
            ax.tick_params(labelbottom=False)
        
            ax.set_yticks(ylabel)  # 每隔 0.5 小時顯示
            ax.set_yticklabels(
                [f"{t}" for t in ylabel],  # 每隔 0.5 小時標籤
                fontsize=15
            )

        self.set_grid(ax=ax)
        self.set_title(ax=ax, title=title)

        

    def plot_ana_homoller(self, x, y, overlay=False, ax=None):

        if overlay:
            ax = ax
        else:
            ax = self.ax


    def set_title(self, ax, title=None, fontsize=20, **kwargs):
    
        if title is not None:
            ax.set_title(title, loc="left", fontsize=fontsize)
        
    def set_time_title(self, ax, time_str=None, size=10, **kwargs):

        if time_str is not None:
            ax.set_title(time_str, loc="right", fontsize=size)
    
    def set_grid(self, ax, linestyle="--", color="#cccaca", linewidth=1.5, **kwargs):

        ax.grid(which='major', color=color, linestyle=linestyle, linewidth=linewidth)

    def set_xylim(self, ax, xlim=(-7,-0.5), ylim=(-7,-0.5), dx=1, dy=1):
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # 設置 x 軸和 y 軸刻度的間距和起始值
        x_major_locator = MultipleLocator(dx)  # x 軸刻度間距為 0.5
        y_major_locator = MultipleLocator(dy)  # y 軸刻度間距為 1.0

        # 設置刻度
        ax.xaxis.set_major_locator(x_major_locator)
        ax.yaxis.set_major_locator(y_major_locator)

        # 格式化刻度標籤，顯示小數點
        x_major_formatter = FormatStrFormatter('%0.1f')  # 保留 1 位小數
        y_major_formatter = FormatStrFormatter('%0.1f')  # 保留 1 位小數
        ax.xaxis.set_major_formatter(x_major_formatter)
        ax.yaxis.set_major_formatter(y_major_formatter)

    def save_map(self, ax, filename="output_map.png", filepath="/mnt/e/workspace/pic/20220629/"):
        '''
        Parameters:
        - ax: matplotlib Axes -> save fig
        - filename: str -> name of fig
        - filepath: str -> the path to save fig
        '''
        ax.figure.savefig(filepath + filename, dpi=300)
        plt.close('all')
        print(f"Map saved as {filename}")

class RHIplot:

    def __init__(self, figsize=(10,10), nrows=1, ncols=1):

        self.fig, self.ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

    def plot_RHI_contourf(self, ax, R, z, var, cmap="jet", levels=np.arange(1, 10.5, 0.5), norm=None, pcolormesh_on=False, title=None, time=None
                         ,cb_name="DBZ", ticks_str=np.arange(1, 11, 1), **kwargs):

        if pcolormesh_on:
            cf = ax.pcolormesh(R, z, var[:-1, :], cmap=cmap, norm=norm)
        else:
            cf = ax.contourf(R[:, :-1], z[:, :-1], var, cmap=cmap, norm=norm, levels=levels, **kwargs)
        
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 18)

        ax.set_xlabel("Range (km)")
        ax.set_ylabel("Height (km)")

        if cb_name is not None:
            self.set_colorbar(cb=cf, cb_name=cb_name, ticks_str=ticks_str, **kwargs)

        if title is not None:
            self.set_title(ax=ax, title=title, size=10)
        if time is not None:
            self.set_time_title(ax=ax, time_str=time, size=10)

        plt.tight_layout()
        return ax

    def set_colorbar(self, cb, cb_name=None, ticks_str=None, skip=1, **kwargs):

        clbar = plt.colorbar(cb,fraction=0.034)
        clbar.ax.set_title(cb_name)
        
        # skip the colorbar
        ticks = ticks_str
        clbar.set_ticks(ticks[::skip])
        clbar.ax.set_yticklabels([f"{tick:.2f}" for tick in ticks[::skip]])
        # clbar.ax.set_yticklabels(ticks_str)

    def set_title(self, ax, title=None, size=10, **kwargs):
        
        if title is not None:
            ax.set_title(title, loc="left", fontsize=size)
        
    def set_time_title(self, ax, time_str=None, size=10, **kwargs):

        if time_str is not None:
            ax.set_title(time_str, loc="right", fontsize=size)  

    def save_map(self, ax, filename="output_map.png", filepath="/mnt/e/workspace/pic/20220629/"):
        '''
        Parameters:
        - ax: matplotlib Axes -> save fig
        - filename: str -> name of fig
        - filepath: str -> the path to save fig
        '''
        plt.tight_layout()
        ax.figure.savefig(filepath + filename, dpi=300)
        plt.close('all')
        print(f"Map saved as {filename}")

class Profileplot:

    def __init__(self, figsize=(10,10), nrows=1, ncols=1):

        self.fig, self.ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

    def plot_prof_contourf(self, ax, x, z, var=None, cmap=radar_colormap, levels=clevel, title=None, time_str=None, **kwargs):

        cf = ax.contourf(x, z, var, cmap=cmap, levels=levels, **kwargs)
        
        if cf:
            self.set_colorbar(cb=cf, cb_name="vor", ticks_str=levels)

        if title is not None:
            self.set_title(ax=ax, title=title)
        
        if time_str is not None:
            self.set_time_title(ax=ax, time_str=time_str)

        ax.set_ylim(0, 16)
        plt.tight_layout()
        return ax
    
    def plot_prof_contour(self, ax, x, z, var=None, colors="red", threshold=[20], linewidths=2, linestyles='-', title=None, time_str=None):

        cf = ax.contour(x, z, var, threshold, colors=colors, linewidths=linewidths, linestyles=linestyles)
        if cf:
            self.set_clabel(ax=ax, cf=cf)
        if title is not None:
            self.set_title(ax=ax, title=title)
        
        if time_str is not None:
            self.set_time_title(ax=ax, time_str=time_str)

        ax.set_ylim(0, 12)
         
        plt.tight_layout()
        return ax
    
    def plot_prof_wind(self, ax, x, z, var=None, u=None, v=None, title=None, time_str=None, **kwargs):
        #0.3 0.075, 0.925 #0.155, 0.910
        qv = ax.quiver(x, z, -u, v, scale=0.20, scale_units='dots', pivot='middle',width=0.003, color="black", **kwargs)
        qk = ax.quiverkey(qv, 0.155, 0.925, 10, '10 m/s', labelpos='E', coordinates='figure')
        
        if title is not None:
            self.set_title(ax=ax, title=title)
        
        if time_str is not None:
            self.set_time_title(ax=ax, time_str=time_str)

        ax.set_ylim(0, 12)
        plt.tight_layout()

        return ax
    def set_clabel(self, ax, cf):
        plt.rcParams['font.weight'] = 'bold'
        ax.clabel(cf, inline=True, fmt="%1.1f", fontsize=5)
        plt.rcParams['font.weight'] = 'medium'

    def set_colorbar(self, cb, cb_name=None, ticks_str=None, skip=1, **kwargs):

        clbar = plt.colorbar(cb,fraction=0.034)
        clbar.ax.set_title(cb_name)
        
        # skip the colorbar
        ticks = ticks_str
        clbar.set_ticks(ticks[::skip])
        clbar.ax.set_yticklabels([f"{tick:.2f}" for tick in ticks[::skip]])
        # clbar.ax.set_yticklabels(ticks_str)

    def set_title(self, ax, title=None, size=10, **kwargs):
        
        if title is not None:
            ax.set_title(title, loc="left", fontsize=size)
        
    def set_time_title(self, ax, time_str=None, size=10, **kwargs):

        if time_str is not None:
            ax.set_title(time_str, loc="right", fontsize=size)  

    def save_map(self, ax, filename="output_map.png", filepath="/mnt/e/workspace/pic/20220629/"):
        '''
        Parameters:
        - ax: matplotlib Axes -> save fig
        - filename: str -> name of fig
        - filepath: str -> the path to save fig
        '''
        # ax.invert_xaxis()
        ax.figure.savefig(filepath + filename, dpi=300)
        plt.close('all')
        print(f"Map saved as {filename}")


def plot_fill_terrain(ax, R, terrain, color="black"):

    ax.plot(R, terrain/1000, color=color)
    ax.fill_between(R, terrain/1000, 0, color=color, zorder=1000)

    return ax

def plot_ana_chart(ax, W_MAX, W_MIN, W_UPAREA, W_DWAREA, elev_plot, time_plot):

    # 創建第一條右側 Y 軸
    ax1 = ax.twinx()  # 與主圖共用 X 軸
    ax1.set_ylabel("Updraft/Downdraft Area (km²)", color="blue")
    ax1.spines["right"].set_position(("axes", 1.10))

    # 繪製藍色折線（上升氣流實線，下降氣流虛線）
    ax1.plot(time_plot, W_UPAREA, "b-", linewidth=2, label="Updraft Area")
    ax1.plot(time_plot, W_DWAREA, "b--", linewidth=2, label="Downdraft Area")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_ylim(0, 5000)  # 設置範圍

    # 創建第二條右側 Y 軸
    def scale_to_area(value):
        """將主軸數據縮放到第二軸範圍 (0-20)。"""
        return value / 333.3

    def scale_to_range(value):
        """將第二軸數據還原到主軸範圍 (0-4000)。"""
        return value * 333.3

    ax2 = ax1.secondary_yaxis("right", functions=(scale_to_area, scale_to_range))
    ax2.spines["right"].set_position(("axes", 1.5))  # 偏移第二條 Y 軸
    ax2.set_frame_on(True)  # 顯示第二條 Y 軸
    ax2.set_ylabel("Maximum Updraft/Downdraft (m/s)", color="magenta")
    ax2.tick_params(axis="y", labelcolor="magenta")

    # 繪製桃紅色折線（上升氣流實線，下降氣流虛線）
    W_MAX_scale = np.array(W_MAX) * 333.3
    ax1.plot(time_plot, W_MAX_scale, "m-", linewidth=2, label="Max Updraft (scaled)")  # 按比例縮放繪製
    ax1.plot(time_plot, W_MIN * 200, "m--", linewidth=2, label="Max Downdraft (scaled)")  # 按比例縮放繪製

    return ax


