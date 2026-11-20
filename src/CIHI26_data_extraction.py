import csv
from file_paths import *
from utils import write

'''
CIHI indicator 2026 data file
Whats an indicator: https://www.cihi.ca/en/access-data-and-reports/health-system-performance-measurement/what-is-an-indicator

The complete health indicator data is downloaded from CIHI website, this has indicators, metrics and health system performance indicator for all disease
The specific indicators of interest here is:
    1. 30 day stroke in hospital mortality
    2. Hospitalized Stroke
The specific metric of interest:
    1. ED wait times for physician in initial assessment
'''

WANT = ["Hospitalized Strokes",
        "30-Day Stroke In-Hospital Mortality",
        "Emergency Department Wait Time for Physician Initial Assessment"]

def main():
    rows_hs, rows_mort, rows_wait = [], [], [] #hs: hospitalized strokes, mort: 30 day mortality in hospital, wait: ED wait time
    with open(CIHI_INDICATOR_26_CSV, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["Indicator"] not in WANT:
                continue
            if "Alberta" not in (row["Place or organization"] + " " + row["Province/territory"]):
                continue
            if row["Indicator"] == "Hospitalized Strokes":
                rows_hs.append(row)
            elif row["Indicator"] == "30-Day Stroke In-Hospital Mortality":
                rows_mort.append(row)
            else:
                rows_wait.append(row)
    #print(rows_mort)

    # Hospitalized strokes - Province
    prov_hs = [r for r in rows_hs if r["Reporting level"] == "Province/territory"]
    write("CIHI26_01_hospitalized_strokes_province.csv", prov_hs, ["Time frame", "Metric", "Metric value", "Unit of measure", "Breakdowns", "Breakdown value"])

    # Mortality, here Breakdowns = "Not applicable" is applied to get the provincial total value instead of the metrics split by some breakdown rule (income qintiles etc.)
    prov_m = [r for r in rows_mort if r["Reporting level"] == "Province/territory"]
    tot = [r for r in prov_m if r["Breakdowns"] == "Not applicable"] #total metrics for province 
    tab = {}

    for r in tot:
        tab.setdefault(r["Time frame"], {})[r["Metric"]] = r["Metric value"] # tab = {"2024-2025(timeframe)": {"metric1" : "value1", "metric2": "value2", "metric3":"value3"}, "2025-2026":{k:v, k:v}}
    with open(OUT / "CIHI26_02_mortality_province.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "deaths_numerator", "admissions_denominator", "risk_adjusted_mortality_per_100", "income_rate_ratio", "potential_rate_reduction_income_pct"])
        for y in sorted(tab):
            d = tab[y]
            w.writerow([y, d.get("Numerator", ""), d.get("Denominator", ""), d.get("Risk-adjusted rate", ""), d.get("Rate ratio (income)", ""), d.get("Potential Rate Reduction (Income)", "")])

    #Wait times
    wait = [r for r in rows_wait if r["Reporting level"] == "Province/territory"]
    write("CIHI26_03_ed_wait_p90.csv", wait, ["Time frame", "Metric", "Metric value", "Unit of measure"])

if __name__ == "__main__":
    main()
    

