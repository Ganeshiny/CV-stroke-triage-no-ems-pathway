'''
Details in wait time: https://www.albertahealthservices.ca/waittimes/waittimes.aspx

Data downloaded from  : https://alberta.io/data/er-wait-times.csv

Description: Hourly snapshot of the estimated wait at every AHS emergency department and urgent care centre that publishes one.
'''

import csv, statistics
from collections import defaultdict
from file_paths import *
from statistics import median as st_median

def main():
    obs = []  # (wait_minutes, city, facility)
    with open(AB_WAITTIME_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["type"] == "Emergency" and r["is_open"] == "true":
                try:
                    obs.append((int(r["wait_minutes"]), r["city"], r["facility"]))
                except ValueError:
                    pass 
    
    waits = sorted(w for w, _, _ in obs)
    n = len(waits)
    
    stats = [
        ("n_hourly_snapshots", n),
        ("n_facilities", len({f for _, _, f in obs})),
        ("median_wait_min", st_median(waits)),
        ("pct_snapshots_over_4h", round(100 * sum(1 for w in waits if w > 240) / n, 1)),
    ]
    with open(OUT / "AB_WAITTIME_01_wait_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["stat", "value"]); w.writerows(stats)

if __name__ == "__main__":
    main()
