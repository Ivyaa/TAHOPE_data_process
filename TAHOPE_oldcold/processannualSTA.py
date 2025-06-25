from read_utils import *
from pathconfig import *

import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

def read_ps01_from_files(annfiles, stno):
    data_list = []
    
    for file in annfiles[1::]:
        # 讀取數據
        df = pd.read_csv(file, sep='\s+', skiprows=100, encoding='utf-8', names=["stno", "yyyymmddhh", "PS01"], usecols=[0, 1, 2])

        # 篩選特定測站並提取 PS01，重命名 yyyymmddhh 為 timestr
        df_filtered = df[(df["stno"] == stno) & (df["PS01"] >= 0) & (df["PS01"] <= 1050)]
        df_filtered = df_filtered[["yyyymmddhh", "PS01"]].rename(columns={"yyyymmddhh": "timestr"})

        # df_filtered = df[df["stno"] == stno][["yyyymmddhh", "PS01"]].rename(columns={"yyyymmddhh": "timestr"})
        
        df_filtered["timestr"] = df_filtered["timestr"].astype(str)  # 確保是字符串
        df_filtered["timestr"] = df_filtered["timestr"].apply(
            lambda x: (pd.to_datetime(x[:8] + "00", format="%Y%m%d%H") + timedelta(days=1)).strftime("%Y%m%d%H") if x[-2:] == "24" else x
        )

        # 將處理後的 timestr 轉換為 datetime 格式，若有錯誤則將錯誤的轉為 NaT
        df_filtered["timestr"] = pd.to_datetime(df_filtered["timestr"], format="%Y%m%d%H", errors="coerce")
        data_list.append(df_filtered)
    
    # 合併所有年份的數據
    result_df = pd.concat(data_list, ignore_index=True)
    return result_df

def interpolate_and_aggregate(df, stno):
    df = df.dropna().sort_values("timestr")  # 移除 NaN 並排序
    df.set_index("timestr", inplace=True)

    # 生成每 10 分鐘的時間索引
    full_time_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="10T")

    # 三次樣條插值
    cs = CubicSpline(df.index.view(int) // 10**9, df["PS01"])
    interpolated_ps01 = cs(full_time_range.view(int) // 10**9)

    # 生成新 DataFrame
    df_interp = pd.DataFrame({"timestr": full_time_range, "PS01": interpolated_ps01})

    # 篩選 6 月 29 日數據
    df_interp["date_str"] = df_interp["timestr"].dt.strftime('%Y%m%d%H%M')  # 202206290000 格式
    df_interp["year"] = df_interp["timestr"].dt.year
    df_interp["time_only"] = df_interp["timestr"].dt.strftime('%H%M')  # 時分 0000, 0010, 0020

    # 只取 6 月 29 日，並確保時間為 10 分鐘間隔
    df_june29 = df_interp[df_interp["timestr"].dt.strftime('%m-%d') == "06-29"]

    # 計算 2013-2022 年的十年平均
    df_filtered = df_june29[df_june29["year"].between(2013, 2022)]
    df_avg = df_filtered.groupby("time_only")["PS01"].mean().reset_index()
    df_avg.rename(columns={"PS01": "ten_year_avg"}, inplace=True)

    return df_avg, df_june29["timestr"].dt.strftime('%Y%m%d%H%M').tolist()

    # # 逐筆儲存每 10 分鐘的數據
    # for _, row in df_interp.iterrows():
    #     timestamp_str = row["timestr"].strftime("%Y%m%d%H%M")  # 檔名時間格式 "YYYYMMDDHHMM"
    #     filename = f"{stno}_{timestamp_str}.txt"
    #     with open(filename, "w") as f:
    #         f.write(f"{row['timestr']}\t{row['yearly_avg']:.2f}\n")

annfiles = sorted(list(STA_ann.glob("*auto_hr.txt")))


stno = "C0E750"
df_ps01 = read_ps01_from_files(annfiles, stno)
result_df, time_list = interpolate_and_aggregate(df_ps01, stno)

print(result_df)

# 逐個 10 分鐘時間點儲存 CSV
for i, row in result_df.iterrows():
    timestamp_str = time_list[i]  # 202206290000 格式
    filename = f"/mnt/e/workspace/data/STAannual/P_annual/{stno}_{timestamp_str}.csv"

    # 轉換成 DataFrame 並儲存
    single_row_df = pd.DataFrame([row])
    single_row_df.to_csv(filename, index=False, encoding="utf-8")

    print(f"已儲存: {filename}")