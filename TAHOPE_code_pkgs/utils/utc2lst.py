import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# self-utils
from config.pathconfig    import *
from config.othsettings   import *

# pkgs
from datetime    import datetime, timedelta

def utc2lst(filename):
    '''
    if you need add new type of time patterns
    you can add them to othsettins.py [patterns]
    '''    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.groups()) == 2:  # 處理像 20220629.0000 的格式
                date_part = match.group(1)
                time_part = match.group(2)
                try:
                    time_obj = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
                    time_obj = time_obj + timedelta(hours=8)
                    return time_obj.strftime("%H%M")
                except ValueError:
                    continue
            if len(match.groups()) > 3:
                date1, time1 = match.group(1), match.group(2)
                date2, time2 = match.group(3), match.group(4)
                
                # 解析為 datetime 物件
                dt1 = datetime.strptime(date1 + time1, "%Y%m%d%H%M%S")
                dt2 = datetime.strptime(date2 + time2, "%Y%m%d%H%M%S")
                
                # 計算中間時間
                mid_time = dt1 + (dt2 - dt1) / 2
                mid_time = mid_time + timedelta(hours=8)
                
                return mid_time.strftime("%Y-%m-%dT%H:%M")  # 格式化為字符串
            else:
                time_str = match.group(1)
                try:
                    if '_' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d_%H-%M-%S")
                    elif ':' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    elif '-' in time_str or '/' in time_str:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d")
                    else:
                        time_obj = datetime.strptime(time_str, "%Y%m%d%H%M")
                    
                    time_obj = time_obj + timedelta(hours=8)
                    return time_obj.strftime("%H%M")
                except ValueError:
                    continue
    
    print("No valid date or time found in filename.")
    return None