import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# self-utils
from config.pathconfig    import *
from config.othsettings   import *
from ioread.SurfaceRead   import *
from config.plot_settings import *

# matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.lines  as mlines
from matplotlib.colors  import ListedColormap
from matplotlib.colors  import BoundaryNorm
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

# cartopy
import cartopy.crs     as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner  import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature        import ShapelyFeature
from cartopy.io.shapereader import Reader

# terrain data
terrain = get_terrain(str(TERRAIN))

class Mapsetting:
    def __init__(self):
        self.shape_file  = str(SHAPE)

    def plot_terrain(self, ax, terrain, terrain_type):
        def plot_binary():
            return ax.contourf(terrain.lon, terrain.lat, terrain.data,
                               cmap='binary', levels=range(0, 4000, 200), extend="max")

        def plot_contour_value():
            ax.contour(terrain.lon, terrain.lat, terrain.data, colors='#616161', levels=[1500])
            ax.contour(terrain.lon, terrain.lat, terrain.data, colors='#a3a3a3', levels=[500])
            ax.contour(terrain.lon, terrain.lat, terrain.data, colors='#a3a3a3', levels=[200])
            return ax

        def plot_mask_white():
            return ax.contourf(terrain.lon, terrain.lat, terrain.data,
                        colors=["#ffffff", "#ffffff"], levels=range(500, 4100, 3500),
                        extend="max", zorder=110)

        def plot_colored():
            return ax.contourf(terrain.lon, terrain.lat, terrain.data,
                               cmap='terrain', levels=range(0, 4000, 500), extend="max")

        def do_nothing():
            return None

        terrain_methods = {
            'binary': plot_binary,
            'contour_value': plot_contour_value,
            'mask_white': plot_mask_white,
            'colored': plot_colored,
            None: do_nothing,
            'None': do_nothing,
        }

        return terrain_methods.get(terrain_type, do_nothing)()

    def Mapset(self, coordinates=(120,122,22,25), terrain_type="binary", mapdefault=False, shapefile=True, radar_loc=True):
        
        myproj = ccrs.PlateCarree()

        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(1,1,1, projection=myproj)

        # ===== 畫地形 =====
        self.plot_terrain(ax, terrain, terrain_type)

        # ===== 畫 shapefile =====
        if shapefile: 
            shape_feature = ShapelyFeature(Reader(self.shape_file).geometries(), myproj,
                                           facecolor="none", edgecolor='black')
            ax.add_feature(shape_feature, zorder=104, linewidth=1.5)

        if mapdefault:
            ax.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')

        if radar_loc:
            ax.scatter(120.907, 24.819, marker='*', color='blue', s=500,
                       transform=ccrs.PlateCarree(), zorder=501)

        # set ticks
        print(coordinates)
        ax.set_xlim(coordinates[0]-0.1, coordinates[1]+0.1)
        ax.set_ylim(coordinates[2]-0.1, coordinates[3]+0.1)
        lon_step = 0.2
        lat_step = 0.2
        xticks = np.arange(coordinates[0], coordinates[1] + lon_step, lon_step)
        yticks = np.arange(coordinates[2], coordinates[3] + lat_step, lat_step)

        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_xticklabels([f"{x:.2f}°E" for x in xticks], fontsize=10)
        ax.set_yticklabels([f"{y:.2f}°N" for y in yticks], fontsize=10)

        ax.grid(color='gray', linewidth=0.8, linestyle='--', alpha=0.7)

        return ax


class Mapplot:
    '''
    This class utilizes Mapsetting to generate and customize maps for visualization.
    '''
    def __init__(self, coordinates=(120, 122, 22, 25),
                 mapdefault=False, shapefile=True, terrain_type='binary',
                 cb=None, time_lst=None):
        # Initialize settings
        self.coordinates = coordinates
        self.mapdefault = mapdefault
        self.shapefile = shapefile
        self.terrain_type = terrain_type

        # Initialize Mapsetting with terrain
        self.map_setting = Mapsetting()

    def plot_map_scatter(self, lat_ss, lon_ss, data_ss, ax=None, **kwargs):
        '''
        Plot the map using the Mapsetting class.
        '''
        if ax is None:
            print(self.coordinates)
            ax = self.map_setting.Mapset(
                coordinates=self.coordinates,
                mapdefault=self.mapdefault,
                shapefile=self.shapefile,
                terrain_type=self.terrain_type
            )
        else:
            ax = ax

        # draw the scatter plot
        sc = ax.scatter(lon_ss, lat_ss, c=data_ss, transform=ccrs.PlateCarree(), **kwargs)
        
        return ax, sc



def apply_canvas_format(ax, settings):
    """
    function版本，從字典設定套用格式。
    settings範例鍵: title, xlabel, ylabel, title_fontsize, label_fontsize, tick_fontsize, xticks, yticks, title_loc
    """
    if 'title' in settings and settings['title']:
        ax.set_title(settings['title'], fontsize=settings.get('title_fontsize', 14), loc="left")
    if 'time_title' in settings and settings['time_title']:
        ax.set_title(settings['time_title'], fontsize=settings.get('title_fontsize', 14), loc="right")
    if 'xlabel' in settings and settings['xlabel']:
        ax.set_xlabel(settings['xlabel'], fontsize=settings.get('label_fontsize', 12))
    if 'ylabel' in settings and settings['ylabel']:
        ax.set_ylabel(settings['ylabel'], fontsize=settings.get('label_fontsize', 12))
    if 'xticks' in settings and settings['xticks'] is not None:
        ax.set_xticks(settings['xticks'])
    if 'yticks' in settings and settings['yticks'] is not None:
        ax.set_yticks(settings['yticks'])
    ax.tick_params(axis='both', labelsize=settings.get('tick_fontsize', 10))
    return ax