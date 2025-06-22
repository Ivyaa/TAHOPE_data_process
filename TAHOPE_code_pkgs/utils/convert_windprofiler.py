import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import glob

import pandas as pd
import xarray as xr
import numpy  as np

from datetime          import datetime, timedelta
from config.pathconfig import windprof, windproflst

def process_asd_file(file_path, processed_minutes):
    """
    處理單個 ASD 檔案。如果檔案的時間分已處理過，則跳過。
    
    Parameters:
        file_path (str): ASD 檔案的完整路徑。
        processed_minutes (set): 已處理過的分鐘記錄集合。
    
    Returns:
        DataFrame: 處理過的資料框，或 None 如果該分鐘已處理過。
    """
    # 假設檔案名稱包含時間資訊，例如 `w2022-08-01-10-00_01.asd`
    time_info = file_path.split('/')[-1].split('_')[0]  # 提取時間部分 `w2022-08-01-10-00`
    time_str = time_info[1:]  # 去除 'w'，只取時間字串
    record_time = pd.to_datetime(time_str, format='%Y-%m-%d-%H-%M')

    # 加上 8 小時轉換為 LST
    record_time += pd.Timedelta(hours=8)

    # 檢查該分鐘是否已處理
    if record_time in processed_minutes:
        print(f"跳過已處理的分鐘：{record_time}")
        return None

    # 加入已處理的分鐘集合
    processed_minutes.add(record_time)

    # 讀取並處理檔案
    with open(file_path, 'r') as file:
        content = file.read()

    # 分割區塊
    blocks = content.split('$')
    data_frames = []

    for block in blocks[0:4]:  # 只處理前兩個區塊
        lines = block.strip().split('\n')
        # 找到標題行（以 HT 開頭）
        header_line = next((line for line in lines if line.strip().startswith('HT')), None)
        if not header_line:
            continue

        # 獲取標題和數據部分
        headers = header_line.split()
        data_lines = [line.split() for line in lines[lines.index(header_line) + 1:] if line.strip()]
        
        # 建立 DataFrame
        df = pd.DataFrame(data_lines, columns=headers)
        df_numeric = df.apply(lambda col: pd.to_numeric(col, errors='coerce'))
        df = df_numeric.where(~df_numeric.isna(), df)  # 還原無法轉換的原始值
        df = df.replace(999.9000, np.nan)
        data_frames.append(df)

    # 合併所有區塊
    merged_df = pd.concat(data_frames)
    
    # 新增整數高度欄位
    merged_df['HT_int'] = merged_df['HT'].astype(int)

    # 根據整數高度去重，保留第一筆資料
    merged_df = (
        merged_df
        .drop_duplicates(subset=['HT_int'], keep='last')  # 只考慮整數部分的重複
        .sort_values(by='HT')  # 依照原始高度排序
    )

    # 篩選需要的欄位
    selected_columns = ['HT', 'SPD', 'DIR', 'QC', 'U', 'V', 'W']
    if not set(selected_columns).issubset(merged_df.columns):
        raise ValueError("檔案中缺少必要欄位，無法處理！")

    # 加入時間欄位，將每筆資料標記上對應的時分秒
    merged_df['Time'] = record_time

    # 篩選欄位並返回結果
    result_df = merged_df[['Time'] + selected_columns]  # 時間欄位放在最前面

    return result_df



processed_minutes = set()
# Merge .asd files for a given LST date
def merge_asd_data_for_lst_date(lst_date):
    # 計算 LST 日期對應的 UTC 時間範圍
    lst_start = datetime.strptime(lst_date, '%Y%m%d') - timedelta(hours=8)
    lst_end = lst_start + timedelta(days=1) - timedelta(minutes=10)

    print("UTC 時間範圍:", lst_start.strftime('%Y-%m-%d-%H-%M'), lst_end.strftime('%Y-%m-%d-%H-%M'))

    # 初始化檔案清單
    files = []

    # 確定前一天與當天的資料夾路徑
    prev_day = (lst_start).strftime('%Y%m%d')  # 前一天資料夾
    current_day = lst_date  # 當天資料夾

    prev_day_folder = f"{windprof}/{prev_day}"
    current_day_folder = f"{windprof}/{current_day}"

    # 從 UTC 起始時間到結束時間，逐分鐘生成檔案名稱模式
    current_time = lst_start
    while current_time <= lst_end:
        # 格式化目前時間
        time_pattern = current_time.strftime('%Y-%m-%d-%H-%M')

        # 判斷資料屬於前一天還是當天
        if current_time.strftime('%Y%m%d') == prev_day:  # 屬於前一天
            pattern = f"{prev_day_folder}/w{time_pattern}_*.asd"
        else:  # 屬於當天
            pattern = f"{current_day_folder}/w{time_pattern}_*.asd"

        # 匹配檔案並加入檔案清單
        files.extend(glob.glob(pattern))
        current_time += timedelta(minutes=1)

    # 初始化合併的 DataFrame
    merged_data = pd.DataFrame()
    
    # Process each file and append the data
    for file in files[:]:
        asd_data = process_asd_file(file, processed_minutes)
        
        merged_data = pd.concat([merged_data, asd_data], ignore_index=True)
        # print(merged_data)
    
    save_as_nc_file(merged_data, output_path=str(windproflst) + "/" + str(lst_date) + "xinwutest.nc")
    # return merged_data


def save_as_nc_file(merged_data, output_path):
    """
    將合併的資料儲存為 .nc 文件。
    
    Parameters:
        merged_data (pd.DataFrame): 包含 ['HT', 'SPD', 'DIR', 'QC', 'U', 'V', 'W', 'Time'] 的資料。
        output_path (str): 儲存 .nc 文件的完整路徑。
    """
    if merged_data.empty:
        print("資料為空，無法儲存！")
        return

    # 確認資料包含必要的欄位
    required_columns = ['HT', 'SPD', 'DIR', 'QC', 'U', 'V', 'W', 'Time']
    if not set(required_columns).issubset(merged_data.columns):
        raise ValueError(f"資料缺少必要的欄位：{set(required_columns) - set(merged_data.columns)}")

    # 轉換 Time 欄位為時間格式（如果尚未轉換）
    if not pd.api.types.is_datetime64_any_dtype(merged_data['Time']):
        merged_data['Time'] = pd.to_datetime(merged_data['Time'])

    # 建立 xarray Dataset
    ds = xr.Dataset()

    # 將資料按照 'Time' 和 'HT' 進行排序
    merged_data = merged_data.sort_values(['Time', 'HT']).reset_index(drop=True)

    # 建立時間和高度的索引
    times = merged_data['Time'].drop_duplicates().values
    heights = merged_data['HT'].drop_duplicates().values

    # 將每個變數轉換為二維陣列 (time * ht)
    for var in ['SPD', 'DIR', 'QC', 'U', 'V', 'W']:
        var_matrix = merged_data.pivot(index='Time', columns='HT', values=var)
        ds[var] = (('time', 'ht'), var_matrix.values)

    # 設定時間和高度的座標
    ds = ds.assign_coords(
        time=('time', times),
        ht=('ht', heights)
    )

    # 設定每個變數的屬性
    var_units = {
        'HT': 'meters',
        'SPD': 'm/s',
        'DIR': 'degrees',
        'QC': 'quality_flag',
        'U': 'm/s',
        'V': 'm/s',
        'W': 'm/s'
    }

    for var, unit in var_units.items():
        if var in ds:
            ds[var].attrs['units'] = unit

    # 設定全局屬性
    ds.attrs['description'] = 'Processed ASD Data'

    # 儲存為 .nc 文件

    ds.to_netcdf(output_path)
    print(f"資料已儲存為 {output_path}")

## test the function ##
# file_dates = "20220629"
# merge_asd_data_for_lst_date(file_dates)