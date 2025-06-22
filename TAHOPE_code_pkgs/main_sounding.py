import os
import gc
import pandas as pd

# self-utils
from config.pathconfig     import *
from config.othsettings    import *
from ioread.RadiosondeRead import *
from utils.utc2lst         import *
from plot.skewTplot        import *

Sounding_0625path = str(SOUNDING_CSV)

# read data by using Soundread
data = Soundread(Sounding_0625path)
print(data)
print(np.shape(data.T))

# plot skewT by using skewTplot
SKTplt = SKEWTPLOT(data)
SKTplt.plot_skewT(CAPE_SHADING_ON=False, HOTOGRAGH_ON=False)




# calculate variable by using metpy (or method in the packages)
# write into csv