from file_paths import *
import csv

def write(name, rows, cols):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"wrote {name}: {len(rows)} rows")

def pct(x):
    return round(x * 100, 1) if isinstance(x, float) else x