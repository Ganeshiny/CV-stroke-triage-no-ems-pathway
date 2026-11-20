from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
OUT = HERE / "results"

OUT.mkdir(exist_ok = True)

CIHI_INDICATOR_26_CSV = DATA / "CIHI_health_indicators_2026" / "indicator-library-all-indicator-data-en (1).csv"
CIHI_AMBULANCE_16_XLSX = DATA / "CIHI_ambulance_use_2016" / "ambulance-use-data-tables-en.xlsx"
CSHS_XLSX = DATA / "CSHS" / "823-cost-of-a-standard-hospital-stay-data-table-en.xlsx"
AB_WAITTIME_CSV = DATA / "Alberta.io_wait_times" / "alberta-io-er-wait-times-2026-11-10-to-2026-11-16.csv"
STATSCAN_CSV = DATA / "Health_indicator_stats_StatCAN" / "1310090501-eng.csv"

