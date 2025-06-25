patterns = [
        r"(\d{4}[-/]\d{2}[-/]\d{2})",         # yyyy-mm-dd or yyyy/mm/dd
        r"(\d{2}[-/]\d{2}[-/]\d{4})",         # dd-mm-yyyy or dd/mm/yyyy
        r"(\d{4}[-/]\d{2}[-/]\d{2}_\d{2}[-_]\d{2}[-_]\d{2})",  # yyyy-mm-dd_HH-MM-SS
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",  # yyyy-mm-dd HH:MM:SS
        r"(\d{8})\.(\d{4})",                   # 20220629.0000
        r"(\d{8})_(\d{6})\.\d+_to_(\d{8})_(\d{6})\.\d+",
        r"(\d{12})",
        r"(\d{8})\_(\d{6})",
    ]

import numpy as np
from metpy.calc import wind_components
from metpy.units import units

# 矩陣大小
rows, cols = 261, 136

# 傳播方向和速度 #6.32
PPwdir = 141.46 * units.degrees  # 方向 (以北為 0 度，順時針)
PPwspd = 6.32 * units.meters / units.seconds  # 速度

# 計算 U 和 V 分量 (MetPy)
U, V = wind_components(PPwspd, PPwdir)

# 創建矩陣
U_matrix = np.full((rows, cols), U.magnitude)
V_matrix = np.full((rows, cols), V.magnitude) 

U_matrix_3D = np.full((1, 37, rows, cols), U.magnitude)
V_matrix_3D = np.full((1, 37, rows, cols), V.magnitude) 



