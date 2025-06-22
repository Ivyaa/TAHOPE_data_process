from pathlib import Path

ROOT     = Path("/mnt/e/workspace/data")
MOSAIC2D = ROOT / "mosaic2D/20220629/"
TERRAIN  = ROOT / "dem_400m_latlon.npy"
SHAPE    = "/mnt/e/workspace/data/COUNTY_MOI_1090820.shp"
CI_LOC   = ROOT / "CI_events_MPD.xlsx"
CI_LOCM2 = ROOT / "CI_events_M2.xlsx"

ana_v4 = ROOT / "ANA_DATA/analysis_04"
RHI2   = Path("/mnt/f/data/spol_20220629/RHI2/")
RHI1   = Path("/mnt/f/data/spol_20220629/RHI1/")
RHI0   = Path("/mnt/f/data/spol_20220629/RHI0/")

SPOL_GRID= Path("/mnt/e/LROSE_RADAR/Spol_grid/20220629/")
SPOL_FRAC= Path("/mnt/e/LROSE_RADAR/samurai/output_fractl/")
SPOL_SUR = Path("/mnt/f/data/spol_20220629/SUR/")
WIND_RETRIEVE = Path("/mnt/e/LROSE_RADAR/samurai/output/") # original is none

STA_OBS  = ROOT / "20220629/STA15m"
STA_OBS28= ROOT / "STA15m"
STA_OBS2 = ROOT / "20220629/STA10m"
RAINS    = ROOT / "STArain/20220629"
STA_WF   = ROOT / "windprof_02/20220629xinwu.nc"
# STA_ann  = ROOT / "STAannual"
STA_ann  = ROOT / "STAannual/P_annual"

windprof = ROOT / "windprof_xinwu"
windproflst = ROOT / "windprof_02"

SOUNDING_TXT = ROOT / "Sounding/data_nonverify/sourcedata/00UTC/46692/46692-2022062500.edt"
SOUNDING_CSV = ROOT / "Sounding/data_verify/46692/00UTC/46692_2022062500.L2.csv"