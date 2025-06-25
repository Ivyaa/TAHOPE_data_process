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
from tool_utils import utc2lst, filter_files_by_time, compute_cfad_percentage_RHI

# RHI angles
angles   = [229., 225., 221., 217., 213., 209., 205., 201., 197., 193., 189., 185.]
files_cv = sorted(list(RHI2.glob("*nc")))

# region
'''
##############################################################
# for reading the RHI and plot
##############################################################
vars_list = ["RHOHV", "VEL", "DBZ", "ZDR"]
levels_list = [rlevel, vlevel, clevel, zlevel]
cmaps_list  = [RHO_colormap, vel_colormap, radar_colormap, ZDR_colormap]
norms_list  = [rnorm, vnorm, cnorm, znorm]
ticklab_list= [rlevel, vlevel, clevel, zlevel]

# vars_list = ["VEL"]
# levels_list = [vlevel]
# cmaps_list  = [vel_colormap]
# norms_list  = [vnorm]
# ticklab_list= [vlevel]

# vars_list = ["PID"]
# levels_list = [plevel]
# cmaps_list  = [PID_colormap]
# norms_list  = [pnorm]
# ticklab_list= [ptickslab]

# vars_list = ["KDP"]
# levels_list = [klevel]
# cmaps_list  = ["jet"]
# norms_list  = [knorm]
# ticklab_list= [klevel]

for var_name, levels, cmaps, norms, tick_str in zip(vars_list, levels_list, cmaps_list, norms_list, ticklab_list):
             # 14, 36  # 26 46
    if var_name == "VEL":
        extend = "both"
    else:
        extend = "neither"

    for i in range(32, 56):
        
        print(f"Processing file: {files_cv[i]}")
        file_cv     = files_cv[i]

        fr = fileread(file_cv)

        # get lst time
        lst_time = utc2lst(filename=str(file_cv))
        file_name= lst_time[-5:-3] + lst_time[-2::]

        for angle in range(0, 12):
            sweepnum = "sweep_"+str(angle)
            try:
                f    = fr.readcfradRHI(sweep=sweepnum, var=var_name)
                anglenew = f.angle
                print(anglenew)

                title_str = var_name
                time_str  = f"SPol RHI {str(int(anglenew))} Deg " + lst_time
                
                # if anglenew >= 170 and anglenew <= 240:
                if anglenew == 183 or anglenew == 0:
                    plotter = RHIplot(figsize=(8, 4))
                    ax      = plotter.ax

                    plotter.plot_RHI_contourf(ax=ax, R=f.R, z=f.z, var=f.data, cmap=cmaps, levels=levels, norm=norms, cb_name=var_name, extend=extend, title=title_str, time=time_str, ticks_str=tick_str, skip=1)
                    plotter.save_map(ax=ax, filename=f"{file_name}_{var_name}.png", filepath=f"/mnt/e/workspace/pic/20220629/SPol/RHI/{str(int(anglenew))}/{var_name}/")
                    plt.close()
            except:
                print(f"no {sweepnum}")

        # del ax, f
        # gc.collect()
'''
# endregion

# region
'''
##############################################################
# for reading the RHI and plot CFAD
##############################################################
vars_list = ["DBZ", "RHOHV", "VEL", "DBZ", "ZDR"]
levels_list = [clevel, rlevel, vlevel, clevel, zlevel]
cmaps_list  = [radar_colormap, RHO_colormap, vel_colormap, radar_colormap, ZDR_colormap]
norms_list  = [cnorm, rnorm, vnorm, cnorm, znorm]
ticklab_list= [clevel, rlevel, vlevel, clevel, zlevel]

varlst = ["DBZ", "RHOHV", "KDP", "ZDR"]

clevel_DBZ = np.arange(5, 76, 1)
clevel_RHO = np.arange(0.7, 1, 0.01)
clevel_ZDR = np.arange(-0.5, 4.1, 0.1)
clevel_KDP = np.arange(-0.5, 4.1, 0.1)
clevellst = [clevel_DBZ, clevel_RHO, clevel_KDP, clevel_ZDR]

colorbar_intervals1 = [0, 0.1, 0.5, 1, 5, 10, 15, 20, 30]
colorbar_intervals2 = [0, 0.1, 0.5, 1, 3, 5, 7, 9, 12, 15]
cmap_intervals = ["white", "cyan", "blue", "#6ffa05", "#429602", "#f0fc00", "#fcbe03", "#ff8d03", "red"]
cmap = ListedColormap(cmap_intervals)
# cnorm=BoundaryNorm(colorbar_intervals, len(colorbar_intervals))
altitudes    = np.arange(0, 17, 0.5)
for var_name, clevel, cmaps, norms, tick_str in zip(varlst, clevellst, cmaps_list, norms_list, ticklab_list):
             # 14, 36  # 26 46
    cfad_var = []
    z_var    = []

    if var_name == "DBZ":
        colorbar_intervals=colorbar_intervals2
        cnorm=BoundaryNorm(colorbar_intervals, len(colorbar_intervals))
    else:
        colorbar_intervals=colorbar_intervals1
        cnorm=BoundaryNorm(colorbar_intervals, len(colorbar_intervals))

    for i in range(18, 24):
        
        print(f"Processing file: {files_cv[i]}")
        file_cv     = files_cv[i]

        fr = fileread(file_cv)

        # get lst time
        lst_time = utc2lst(filename=str(file_cv))
        file_name= lst_time[-5:-3] + lst_time[-2::]

        for angle in range(0, 12):
            sweepnum = "sweep_"+str(angle)
            # try:
            f    = fr.readcfradRHI(sweep=sweepnum, var=var_name)
            anglenew = f.angle
            print(anglenew)

            title_str = var_name
            time_str  = f"SPol RHI {str(int(anglenew))} Deg " + lst_time
            
            if anglenew >= 170 and anglenew <= 240:
            # if anglenew == 183 or anglenew == 0:
                cfad_var.append(f.data[0:210, 0:1999])
                z_var.append(f.z[0:210, 0:1999])
                    
            # except:
            #     print(f"no {sweepnum}")
    print(np.shape(z_var), np.shape(cfad_var))
    CFAD_per= compute_cfad_percentage_RHI(t_var=cfad_var, z_var=z_var, clevel=clevel)
    print(np.shape(CFAD_per))

    plt.figure(figsize=(6, 6))
    X, Y = np.meshgrid(clevel[:], altitudes[2::])  # 网格匹配
    pcm = plt.contourf(X[:, 1::], Y[:, 1::],  CFAD_per[2::, :], cmap=cmap, norm=cnorm, levels=colorbar_intervals, extend="max")  # 使用自定义norm
    # ticks=np.arange(0,21,1),
    plt.colorbar(pcm, ticks=colorbar_intervals, label='Percentage (%)')  # 设置colorbar显示的刻度

    plt.grid(which='major', axis='x', linestyle='--', color='gray', linewidth=0.5)  # 设置每隔5的网格线
    plt.grid(which='major', axis='y', linestyle='--', color='gray', linewidth=0.5)

    plt.xticks(ticks=clevel[::5])
    plt.yticks(ticks=np.arange(0, 17, 1))
    plt.xlabel(str(var_name), fontsize=15)
    plt.ylabel('Altitude (km)', fontsize=15)
    plt.ylim(0, 16)
    plt.title(f'CFADs {var_name}', loc="left", fontsize=15)
    plt.savefig(f"/mnt/e/workspace/pic/20220629/{var_name}_cfadsecho1RHI40dBZonly.png", dpi=300)
'''
# endregion


# region

##############################################################
# for reading the RHI and plot with windretrie
##############################################################
vars_list = ["RHOHV", "ZDR"]
levels_list = [rlevel, zlevel]
cmaps_list  = [RHO_colormap, ZDR_colormap]
norms_list  = [rnorm, znorm]
ticklab_list= [rlevel, zlevel]

vars_list = ["ZDR"]
levels_list = [zlevel]
cmaps_list  = [ZDR_colormap]
norms_list  = [znorm]
ticklab_list= [zlevel]

# vars_list = ["VEL"]
# levels_list = [vlevel]
# cmaps_list  = [vel_colormap]
# norms_list  = [vnorm]
# ticklab_list= [vlevel]

# vars_list = ["DBZ"]
# levels_list = [clevel]
# cmaps_list  = [radar_colormap]
# norms_list  = [cnorm]
# ticklab_list= [clevel]

# vars_list = ["PID"]
# levels_list = [plevel]
# cmaps_list  = [PID_colormap]
# norms_list  = [pnorm]
# ticklab_list= [ptickslab]

# vars_list = ["KDP"]
# levels_list = [klevel]
# cmaps_list  = ["jet"]
# norms_list  = [knorm]
# ticklab_list= [klevel]


wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
elev_plot = np.arange(0, 18.5, 0.5)
for var_name, levels, cmaps, norms, tick_str in zip(vars_list, levels_list, cmaps_list, norms_list, ticklab_list):
             # 14, 36  # 26 46
    if var_name == "VEL":
        extend = "both"
    else:
        extend = "neither"

    for i in range(38, 60):
        
        print(f"Processing file: {files_cv[i]}")
        print(f"Processing file: {wfiles[i-19]}")
        file_cv     = files_cv[i]
        w_ret_dir   = str(wfiles[i-19]) + "/samurai_XYZ_analysis.nc"

        fr = fileread(file_cv)
        wr = fileread(w_ret_dir) #120.90746307373, 24.8190879821777 
        dw, R_plot = wr.readwretrie_nc(profile_on=True, start_point=[24.8190879821777, 120.90746307373], end_point=[25.2, 120.90746307373])

        # get lst time
        lst_time = utc2lst(filename=str(file_cv))
        file_name= lst_time[-5:-3] + lst_time[-2::]

        # for angle in range(0, 12): # 10->183, 6->0 degree
        angle = 10
        sweepnum = "sweep_"+str(angle)

        f    = fr.readcfradRHI(sweep=sweepnum, var=var_name)
        fkdp = fr.readcfradRHI(sweep=sweepnum, var="KDP")
        anglenew = f.angle
        print(anglenew)

        title_str = var_name
        time_str  = f"SPol RHI {str(int(anglenew))} Deg " + lst_time
        
        # if anglenew >= 170 and anglenew <= 240:
        if anglenew == 183 or anglenew == 0:
            plotter = RHIplot(figsize=(8, 3))
            profplot = Profileplot(figsize=(8, 3))
            ax      = plotter.ax

            ax       = plotter.plot_RHI_contourf(ax=ax, R=f.R, z=f.z, var=f.data, cmap=cmaps, levels=levels, norm=norms, cb_name="ZDR", pcolormesh_on=False, extend=extend, title=None, time=time_str, ticks_str=tick_str, skip=1)
            # ax       = profplot.plot_prof_wind(ax=ax, x=R_plot[0, ::4], z=elev_plot[0:-1:2], u=-dw.SR_V.values[0, 0:-1:2, ::4], v=dw.W.values[0, 0:-1:2, ::4]*2)
            # ax       = profplot.plot_prof_contour(ax=ax, x=f.R[:, :-1], z=f.z[:, :-1], var=fkdp.data, threshold=[1.0, 2.0, 3.0], colors="blue", linewidths=1)
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[10], colors="#633602")
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.SR_WS.values[0, 1:-1, :], threshold=[6], colors="#ffffff")
            # ax       = profplot.plot_prof_wind(ax=ax, x=R_plot[0, ::2], z=elev_plot[0:-1], u=-dw.UVOR.values[0, 0:-1, ::2], v=dw.VVOR.values[0, 0:-1, ::2])
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=[5, 10, 15], linewidths=1.5, colors="gray")
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=[-7, -5, -1], linestyles="--", linewidths=1.5, colors="gray")
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=[5, 10, 15], linewidths=1.5, colors="black")
            # ax       = profplot.plot_prof_contour(ax=ax, x=R_plot[0, :], z=elev_plot[1:-1], var=dw.W.values[0, 1:-1, :], threshold=[-7, -5, -1], linestyles="--", linewidths=1.5, colors="black")


            ax.set_xlim(0, 80)
            ax.set_ylim(0, 16)
            profplot.save_map(ax=ax, filename=f"{file_name}_{var_name}.png", filepath=f"/mnt/e/workspace/pic/20220629/{str(int(anglenew))}_{var_name}.png")
            plt.close()


        # del ax, f
        # gc.collect()

# endregion

# region
'''
wfiles= sorted(list(WIND_RETRIEVE.glob("2022*")))
elev_plot = np.arange(0, 18.5, 0.5)
for var_name, levels, cmaps, norms, tick_str in zip(vars_list, levels_list, cmaps_list, norms_list, ticklab_list):
             # 14, 36  # 26 46
    if var_name == "VEL":
        extend = "both"
    else:
        extend = "neither"

    for i in range(38, 56):
        
        print(f"Processing file: {files_cv[i]}")
        print(f"Processing file: {wfiles[i-19]}")
        file_cv     = files_cv[i]
        w_ret_dir   = str(wfiles[i-19]) + "/samurai_XYZ_analysis.nc"

        fr = fileread(file_cv)
        wr = fileread(w_ret_dir) #120.90746307373, 24.8190879821777 
        dw, R_plot = wr.readwretrie_nc(profile_on=True, start_point=[24.8190879821777, 120.90746307373], end_point=[24.06976, 120.87605])

        # get lst time
        lst_time = utc2lst(filename=str(file_cv))
        file_name= lst_time[-5:-3] + lst_time[-2::]
        time_str  = f"SPol RHI " + lst_time

        sweep183 = "sweep_10"
        sweep0 = "sweep_6"

        f183 = fr.readcfradRHI(sweep=sweep183, var=var_name)
        f0 = fr.readcfradRHI(sweep=sweep0, var=var_name)

        # 反轉 183 度的 RHI，使其對應 -x 軸
        R_183 = -f183.R[:, ::-1]  # 反轉 R，使其從 0 到 -80
        data_183 = f183.data[:, ::-1]  # 反轉資料

        # 0 度的 RHI 保持不變
        R_0 = f0.R
        data_0 = f0.data


        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 4), sharey=True)  # 左右兩個子圖，共享 y 軸
        plt.subplots_adjust(wspace=0)
        # 繪製 183 度 RHI（左半邊）
        plotter = RHIplot(figsize=(12, 4))
        ax1 = plotter.plot_RHI_contourf(
            ax=ax1, 
            R=R_183, 
            z=f183.z[:, ::-1],  # 183 度的 z 軸
            var=data_183+11.1, 
            cmap=cmaps, 
            levels=levels, 
            norm=norms, 
            cb_name=None, 
            extend=extend, 
            title=None, 
            time=None, 
            ticks_str=tick_str, 
            skip=1
        )
        ax1.set_xlim(-80, 0)  # 設定 x 軸為負值

        # 繪製 0 度 RHI（右半邊）
        plotter.plot_RHI_contourf(
            ax=ax2, 
            R=R_0, 
            z=f0.z,  # 0 度的 z 軸
            var=-data_0+11.1, 
            cmap=cmaps, 
            levels=levels, 
            norm=norms, 
            cb_name=None, 
            extend=extend, 
            title=None, 
            time=None, 
            ticks_str=tick_str, 
            skip=1
        )
        ax2.set_xlim(0, 80)  # 設定 x 軸為正值

        # 設定 y 軸範圍，確保兩張圖對齊
        ax1.set_ylim(0, 16)

        # 設定主標題
        # fig.suptitle(f"SPol RHI {var_name}", fontsize=12)
        fig.suptitle(f"{lst_time}", fontsize=20)

        # 存圖
        file_name = lst_time[-5:-3] + lst_time[-2::]
        plt.tight_layout()
        ax1.figure.savefig(f"/mnt/e/workspace/pic/20220629/{lst_time[-5::]}{var_name}_Combined.png", dpi=300, bbox_inches="tight")
        ax2.figure.savefig(f"/mnt/e/workspace/pic/20220629/{lst_time[-5::]}{var_name}_Combined.png", dpi=300, bbox_inches="tight")

        plt.close()
    break

'''
# endregion