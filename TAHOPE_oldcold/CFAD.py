import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import gc
import psutil  # 用於監控記憶體使用量
from matplotlib.colors  import ListedColormap
from matplotlib.colors  import BoundaryNorm
from scipy.interpolate import griddata

from pathconfig import *
from read_utils import *
from plot_utils import *
from plot_settings import *
from tool_utils import utc2lst, filter_files_by_time, calculate_bearing, calvorticity, steiner_conv_strat_classification, compute_cfad_percentage
from tool_utils import classify_steiner_3d
from othsettings import U_matrix, V_matrix

# region

###############################################
# plot CV from mosaic2D GRWIND
###############################################
coord = (120.30, 121.10, 23.8, 25.2)
# read radar file
files = sorted(list(SPOL_GRID.glob("*.nc")))
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))

height = [2.0]
varlst = ["DBZ", "RHOHV", "KDP", "ZDR"]

clevel_DBZ = np.arange(5, 76, 1)
clevel_RHO = np.arange(0.7, 1, 0.01)
clevel_ZDR = np.arange(-0.5, 4.1, 0.1)
clevel_KDP = np.arange(-0.5, 4.1, 0.1)
clevellst = [clevel_DBZ, clevel_RHO, clevel_KDP, clevel_ZDR]

altitudes = np.arange(0, 18.5, 0.5)

colorbar_intervals = [0, 0.1, 0.5, 1, 5, 10, 15, 20, 30]
colorbar_intervals = [0, 0.1, 0.5, 1, 3, 5, 7, 9, 12, 15]
# colorbar_intervals = [0, 0.1, 0.5, 1, 2, 3, 4, 5, 7, 10]
cmap_intervals = ["white", "cyan", "blue", "#6ffa05", "#429602", "#f0fc00", "#fcbe03", "#ff8d03", "red"]
cmap = ListedColormap(cmap_intervals)
cnorm=BoundaryNorm(colorbar_intervals, len(colorbar_intervals))
# cmap = plt.get_cmap('jet')
# cmap.set_under('white')
# norm = BoundaryNorm(colorbar_intervals, ncolors=256, extend='neither')  # 定义色阶

'''
for var, clevel in zip(varlst, clevellst):
    # if var == "DBZ":
    #     continue
    var_all_matrix = []
    w_all_matrix = []
    for i in range(18,36):
        w_all_matrix = []
        var_all_matrix = []

        # i = 32

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        wfile_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid(CVon=True)

        allf = fr.readSPolgrid(all_data=True)
        data_total = allf['DBZ'].values[0]

        wr = fileread(wfile_dir)
        dw = wr.readwretrie_nc()
        wvalue = dw['W'].values[0]

        if i > 27:
            lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 24.6, 25.2)
            lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
            lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

            mask = np.outer(lat_mask, lon_mask)
        else:
            lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

            lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
            lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

            mask = np.outer(lat_mask, lon_mask)
        
        lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

        lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
        lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

        mask_mannuel = np.outer(lat_mask, lon_mask)
        data_threshold = f.data>=0

        print(np.shape(data_total))
        # filtered_data = np.where(combined_mask, f.data, False)
        final_datamask = classify_steiner_3d(data_total, np.arange(0, 18.5, 0.5), f.lat, f.lon, a=9, b=45)

        label_to_num = {'DC': 5.5, 'MC': 4.5, 'SC': 3.5, 'ST': 2.5, 'WE': 1.5, 'UN': 0.5}
        classification_num = np.vectorize(label_to_num.get)(final_datamask)  # shape = (lat, lon)       
        
        # combined_mask = mask & classification_num & data_threshold
        # combined_mask_sati = ~combined_mask & mask_mannuel & data_threshold
        # filtered_data = np.where(combined_mask, f.data, False)

        allf = fr.readSPolgrid(all_data=True)
        data = allf[var].values[0]
        
        # combined_mask = np.repeat(combined_mask[np.newaxis, :, :], data.shape[0], axis=0)
        # filtered_data = np.where(combined_mask, data, np.nan)
        # filtered_wdata= np.where(combined_mask, wvalue, np.nan)
        # print(np.shape(filtered_data))
        map_plot = Mapplot()
        # ax       = map_plot.plot_map_OBS(coordinates=coord, lat=grid_lat, lon=grid_lon, var=grid_T, extend="both", cmap="jet", levels=np.arange(0, 21, 1), cb_name="m/s", title=title_str, time_str=time_str, size=17)
        ax       = map_plot.plot_map_OBS(coordinates=coord, lat=f.lat, lon=f.lon, var=classification_num, contour_on=False, extend="neither", cmap=cmap_clfi, levels=np.arange(2, 7, 1))
        map_plot.save_map(ax, filename=f"{lst_time}_range_clfi.png")

        # var_all_matrix.append(filtered_data)
        # w_all_matrix.append(filtered_wdata)

        # var_all = np.array(var_all_matrix)
        # # clevel  = np.arange(-10, 21, 1)

        # CFAD_per= compute_cfad_percentage(var_all, clevel, dx=1)
        # print(np.shape(var_all))


        # plt.figure(figsize=(6, 6))
        # X, Y = np.meshgrid(clevel[:], altitudes[2::])  # 网格匹配
        # pcm = plt.contourf(X[:, 1::], Y[:, 1::],  CFAD_per[2::, :], cmap=cmap, norm=cnorm, levels=colorbar_intervals, extend="max")  # 使用自定义norm
        # # ticks=np.arange(0,21,1),
        # plt.colorbar(pcm, ticks=colorbar_intervals, label='Percentage (%)')  # 设置colorbar显示的刻度

        # plt.grid(which='major', axis='x', linestyle='--', color='gray', linewidth=0.5)  # 设置每隔5的网格线
        # plt.grid(which='major', axis='y', linestyle='--', color='gray', linewidth=0.5)

        # plt.xticks(ticks=clevel[::5])
        # plt.yticks(ticks=np.arange(0, 13, 1))
        # plt.xlabel(str(var), fontsize=15)
        # # plt.xlabel("Vertical velocity", fontsize=15)
        # plt.ylabel('Altitude (km)', fontsize=15)
        # plt.ylim(0, 12)
        # plt.title(f'CFADs {var}', loc="left", fontsize=15)
        # # plt.title(f'CFADs units:m/s', loc="left", fontsize=15)
        # plt.savefig(f"/mnt/e/workspace/pic/20220629/{var}_{lst_time}_conv.png", dpi=300)
        # # plt.savefig(f"/mnt/e/workspace/pic/20220629/updrafts_sati_p1.png", dpi=300)
    break
'''
# endregion

# region
'''
for var, clevel in zip(varlst, clevellst):
    # if var == "DBZ":
    #     continue
    valid_strati = []
    valid_conv   = []
    time_label   = []
    for i in range(18,36):


        # i = 32

        print(f"Processing file: {files[i]}")
        print(f"Processing file: {wfiles[i]}")
        # print_memory_usage()

        # convert to file_path(str)
        file_dir = str(files[i])
        wfile_dir= str(wfiles[i]) + "/samurai_XYZ_analysis.nc"

        # get lst time
        lst_time = utc2lst(filename=str(files[i]))
        time_str = f"{lst_time}LST 06/29/2022"

        # need to call object first then 
        # give the other instructions
        # you can read csv, mdf, mosaic2D in this fr object
        # but only one file can be read
        fr = fileread(file_dir)
        f  = fr.readSPolgrid(CVon=True)

        wr = fileread(wfile_dir)
        dw = wr.readwretrie_nc()
        wvalue = dw['W'].values[0]

        if i > 27:
            lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 24.6, 25.2)
            lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
            lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

            mask = np.outer(lat_mask, lon_mask)
        else:
            lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

            lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
            lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

            mask = np.outer(lat_mask, lon_mask)
        
        lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

        lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
        lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

        mask_mannuel = np.outer(lat_mask, lon_mask)
        valid_total  = np.sum(mask_mannuel == True)
        data_threshold = f.data>=0

        
        # filtered_data = np.where(combined_mask, f.data, False)

        final_datamask = steiner_conv_strat_classification(f.lat, f.lon, f.data)

        combined_mask = mask & final_datamask
        combined_mask_sati = ~combined_mask & mask_mannuel & data_threshold
        # filtered_data = np.where(combined_mask, f.data, False)

        # valid_total  = np.sum(mask)
        valid_count  = np.sum((combined_mask_sati  == True) & (~np.isnan(combined_mask_sati )))
        valid_countc = np.sum((combined_mask == True) & (~np.isnan(combined_mask)))
        
        valid_conv.append(valid_countc/(valid_total))
        valid_strati.append(valid_count/(valid_total))
        time_label.append(lst_time)


    fig, ax = plt.subplots(figsize=(10, 5))

    # 畫對流與層狀比例線
    ax.plot(time_label, valid_conv, label="Convective Region", linestyle='-', color='red')
    ax.plot(time_label, valid_strati, label="Stratiform Region", linestyle='--', color='blue')

    # 標籤與格線設定
    ax.set_xlabel("Time Index")
    ax.set_ylabel("Fractional Area")
    ax.set_title("Convective vs. Stratiform Region Proportion Over Time")

    # X 軸刻度設定
    skip = 3
    ax.set_xticks(time_label[::skip])  # 每隔 skip 個標籤顯示
    ax.set_xticklabels(
        [f"{t}" for t in time_label[::skip]],
        rotation=45,
        fontsize=15
    )

    ax.set_ylim(0, 0.5)
    ax.grid(True, linestyle='-')
    ax.legend()
    plt.tight_layout()
    plt.savefig("/mnt/e/workspace/pic/20220629/conv_vs_strati_total.png", dpi=300)
    
    break
'''
# endregions


# region
'''
###################################################
# Kirshboum, 2014 radar analysis
###################################################

# for var, clevel in zip(varlst, clevellst):
#     # if var != "DBZ":
#     #     continue
var_all_DBZ = []
var_all_ZDR = []
for i in range(26,36):

    # i = 32
    # var_all_DBZ = []
    # var_all_ZDR = []
    print(f"Processing file: {files[i]}")
    print(f"Processing file: {wfiles[i]}")
    # print_memory_usage()

    # convert to file_path(str)
    file_dir = str(files[i])

    # get lst time
    lst_time = utc2lst(filename=str(files[i]))
    time_str = f"{lst_time}LST 06/29/2022"

    # need to call object first then 
    # give the other instructions
    # you can read csv, mdf, mosaic2D in this fr object
    # but only one file can be read
    fr = fileread(file_dir)
    f  = fr.readSPolgrid(CVon=True)

    if i > 27:
        lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 24.6, 25.2)
        lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
        lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

        mask = np.outer(lat_mask, lon_mask)
    else:
        lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

        lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
        lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

        mask = np.outer(lat_mask, lon_mask)
    
    lon_min, lon_max, lat_min, lat_max = (120.30, 121.20, 23.8, 25.2)

    lat_mask = (f.lat >= lat_min) & (f.lat <= lat_max)
    lon_mask = (f.lon >= lon_min) & (f.lon <= lon_max)

    mask_mannuel = np.outer(lat_mask, lon_mask)
    data_threshold = f.data>=0

    
    # filtered_data = np.where(combined_mask, f.data, False)

    final_datamask = steiner_conv_strat_classification(f.lat, f.lon, f.data)

    combined_mask = mask & final_datamask
    combined_mask_sati = ~combined_mask & mask_mannuel & data_threshold
    # filtered_data = np.where(combined_mask, f.data, False)

    # DBZ
    allf = fr.readSPolgrid(all_data=True)
    data = allf["DBZ"].values[0]
    combined_mask = np.repeat(combined_mask_sati[np.newaxis, :, :], data.shape[0], axis=0)
    filtered_data = np.where(combined_mask, data, np.nan)
    var_all_DBZ.append(filtered_data)

    # ZDR
    allfz = fr.readSPolgrid(all_data=True)
    data = allfz["ZDR"].values[0]
    # combined_mask = np.repeat(combined_mask[np.newaxis, :, :], data.shape[0], axis=0)
    filtered_data = np.where(combined_mask, data, np.nan)
    var_all_ZDR.append(filtered_data)

var_DBZ = np.array(var_all_DBZ)
var_ZDR = np.array(var_all_ZDR)

diff_DBZ = -var_DBZ[:, 6, :, :] + var_DBZ[:, 3, :, :]
diff_ZDR = -var_ZDR[:, 6, :, :] + var_ZDR[:, 3, :, :]

diff_DBZ = diff_DBZ.flatten()  # DBZ 差值，轉為 1D
diff_ZDR = diff_ZDR.flatten()  # ZDR 差值，轉為 1D

# 定義網格範圍與間隔
dbz_bins = np.arange(-10, 12, 2)  # DBZ 差值範圍 -10 到 10，步長 1
zdr_bins = np.arange(-1.5, 1.7, 0.2)  # ZDR 差值範圍 -1.5 到 1.5，步長 0.1

# 計算 2D 直方圖 (頻率)
hist, xedges, yedges = np.histogram2d(diff_DBZ, diff_ZDR, bins=[dbz_bins, zdr_bins])

# 正規化頻率成百分比
hist_percentage = (hist / np.sum(hist)) * 100  # 轉換為百分比
print(np.nanmin(hist_percentage)) 
# 繪製頻率分布圖
plt.figure(figsize=(8, 6))

# 使用 pcolormesh 繪製網格資料
X, Y = np.meshgrid(xedges[:], yedges[:])  # 定義 X, Y 網格
plt.pcolormesh(X, Y, hist_percentage.T, cmap=cmap, shading='flat', norm=cnorm)

# 添加顏色條 (Colorbar)
plt.colorbar(label='PDF (%)')

# 添加標註與標籤
plt.xlabel(r'$\Delta DBZ$ (dBZ)', fontsize=14)
plt.ylabel(r'$\Delta Z_{DR}$', fontsize=14)
plt.title('PDF of DBZ and ZDR Differences', fontsize=16)

# 添加坐標軸網格線
plt.axhline(0, color='k', linestyle='--', linewidth=0.8)  # 水平中心線
plt.axvline(0, color='k', linestyle='--', linewidth=0.8)  # 垂直中心線
plt.grid(color='gray', linestyle='--', linewidth=0.5)

# 顯示圖形
plt.savefig(f"/mnt/e/workspace/pic/20220629/all_histogram_sati2.png", dpi=300)
'''
# endregion

# region

import matplotlib.pyplot as plt
from matplotlib import colormaps  # 新方式取 colormap

percentile_dbz_list = []
percentile_zdr_list = []
time_list = []

for i in range(18, 36):
    print(f"Processing file: {files[i]}")
    
    file_dir = str(files[i])
    lst_time = utc2lst(filename=file_dir)
    time_str = f"{lst_time}LST 06/29/2022"

    fr = fileread(file_dir)
    f  = fr.readSPolgrid(CVon=True)

    allf  = fr.readSPolgrid(all_data=True)
    dbz   = allf["DBZ"].values[0]
    zdr   = allf["ZDR"].values[0]

    diff_DBZ = -dbz[6, :, :] + dbz[3, :, :]
    diff_ZDR = -zdr[6, :, :] + zdr[3, :, :]

    # 使用 90 百分位數
    p90_dbz = np.nanmean(diff_DBZ)
    p90_zdr = np.nanmean(diff_ZDR)

    p90_dbz = np.percentile(diff_DBZ, 50)
    p90_zdr = np.percentile(diff_ZDR, 50)

    percentile_dbz_list.append(p90_dbz)
    percentile_zdr_list.append(p90_zdr)
    time_list.append(lst_time)

# --- 畫圖，每個點單獨 scatter 並有 legend ---
plt.figure(figsize=(10, 7))

# 使用新版 colormap API 並重取樣顏色數量
cmap = colormaps.get_cmap('tab20').resampled(len(time_list))

for idx, (x, y, t) in enumerate(zip(percentile_dbz_list, percentile_zdr_list, time_list)):
    plt.scatter(x, y, color=cmap(idx), label=f"{t}LST", s=100)

plt.axhline(0, color='k', linestyle='--', linewidth=0.8)
plt.axvline(0, color='k', linestyle='--', linewidth=0.8)
plt.grid(True, linestyle='--', alpha=0.6)

plt.xlabel(r'Mean $\Delta DBZ$ (dBZ)', fontsize=14)
plt.ylabel(r'Mean $\Delta ZDR$', fontsize=14)
plt.title('Mean of ΔDBZ vs ΔZDR per Time', fontsize=16)

# plt.xlim(-10, 10)
# plt.ylim(-1.5, 1.5)

# 顯示圖例，每個時間一個
plt.legend(title='LST Time', loc='upper right', fontsize=15)

plt.tight_layout()
plt.savefig("/mnt/e/workspace/pic/20220629/median_scatter_per_time_legend.png", dpi=300)

# endregion