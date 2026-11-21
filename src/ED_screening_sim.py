'''
Does CV-based facial-video screening at ED triage address 
(a) missed diagnosis and 
(b) door-to-recognition delay for self-presenting stroke patients 
at the published performance of Face-FAST and DeepStroke?

2 arm: baseline, CV


'''

import csv, statistics
from collections import defaultdict
from file_paths import *
from statistics import median as st_median
from utils import st_median
import csv, math, os
import csv, os
import numpy as np

#================= baseline arm =======================================
#  population
ADMISSIONS = 4011                 # observed: CIHI 30-day stroke mortality denominator, 2025-26 (script 01)
SELF_PRESENT_SHARE = 0.367        # observed: CIHI ambulance-use data, Alberta 2014-15 (script 03)
COHORT_SELFPRESENTING = round(ADMISSIONS * SELF_PRESENT_SHARE)   # 1,472 per year

# door-to-recognition baseline
# Time to physician assessment is drawn from a lognormal fitted to the observed
# AHS/Alberta.io hourly wait feed (one week, Nov 10-16 2026), see fit_lognormal_wait().
BASE_MISS_PROB = 0.13              # borrowed: Pedroso et al. 2026 (13% ED miss rate)
MISSED_RECOGNITION_DELAY_H = 12.0  # assumed (no source): a missed stroke is recognized
                                   # 12 h later; no Alberta data on this interval -> UNKNOWN

#================= CV arm =======================================
# Aldridge et al. 2022 (Face-FAST) and Cai et al. 2022 (DeepStroke)
TOOLS = {
    "FaceFAST":  dict(se=0.878, sp=0.993),
    "DeepStroke": dict(se=0.886, sp=0.838),
}
CV_TIME_TO_RECOGNITION_MIN = 10.0  # assumed: DeepStroke <=6 min capture + triage-desk margin

# economics
WTP_LEVELS = [25000, 50000, 100000]  # convention: no official Canadian threshold
PRICE_SCENARIOS = [5, 15, 30, 60]  # assumed: $ per patient screened (licence + integration)
PRICE_BASE = 15.0
CT_COST = 300.0                    # assumed: CT head cost per false-positive workup
CSHS_ACUTE = 11016.0               # observed: CIHI Cost of a Standard Hospital Stay, Alberta 2024-25 (script 02)

# scenarios
PREVALENCE_SCENARIOS = [0.05, 0.10, 0.20]  # assumed: stroke prevalence at the screening gate
PREVALENCE_BASE = 0.10
SEED = 20261119


def fit_lognormal_wait():
    """
    Fit a lognormal to the observed AHS/Alberta.io wait_minutes distribution
    (open emergency departments, wait > 0).
    Returns (mu, sigma, n): mean and SD of log-minutes, and snapshot count.
    """
    vals = []
    with open(AB_WAITTIME_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("type") != "Emergency" or row.get("is_open") != "true":
                continue
            w = row.get("wait_minutes", "").strip()
            if w:
                try:
                    v = int(w)
                    if v > 0:
                        vals.append(v)
                except ValueError:
                    pass
    logs = [math.log(v) for v in vals]
    mu = sum(logs) / len(logs)
    var = sum((x - mu) ** 2 for x in logs) / (len(logs) - 1)
    return mu, math.sqrt(var), len(vals)

MU, SIGMA, N_OBS = fit_lognormal_wait()


def baseline_recognition_min(rng, n):
    """Minutes to recognition for a self-presenting stroke under current care.
    mu/sigma are log-minutes from the fitted Alberta.io distribution."""
    t_assess = rng.lognormal(MU, SIGMA, n)
    missed = rng.random(n) < BASE_MISS_PROB
    return t_assess + missed * MISSED_RECOGNITION_DELAY_H * 60.0


def cv_recognition_min(rng, n, se):
    """Minutes to recognition with CV screening at triage.
    Detected: CV workflow time. Not detected: baseline path."""
    detected = rng.random(n) < se
    t_base = baseline_recognition_min(rng, n)
    return detected * CV_TIME_TO_RECOGNITION_MIN + (~detected) * t_base


def gate_table(p, se, sp, n=1000):
    """Closed-form screening-gate ledger per n screened."""
    strokes = n * p
    tp = strokes * se
    fn = strokes - tp
    fp = (n - strokes) * (1 - sp)
    tn = (n - strokes) - fp
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    # Strokes missed under CV screening. CV false negatives follow the
    # baseline clinician path (as in cv_recognition_min), so how many stay
    # missed depends on how CV misses overlap with clinician misses:
    #   independent  -> missed by both = fn x BASE_MISS_PROB  (best case)
    #   full overlap -> CV misses are a subset of clinician misses, so
    #                   missed = min(fn, baseline missed)       (worst case)
    missed_base = strokes * BASE_MISS_PROB
    missed_cv_indep = fn * BASE_MISS_PROB
    missed_cv_overlap = min(fn, missed_base)
    return dict(prevalence=p, se=se, sp=sp,
                strokes_present=strokes, true_pos=tp, false_neg=fn,
                false_pos=fp, true_neg=tn, ppv=ppv,
                extra_cts_per_1000=fp,
                missed_baseline=missed_base,
                missed_cv_full_overlap=missed_cv_overlap,
                missed_cv_independent=missed_cv_indep,
                recovered_min=missed_base - missed_cv_overlap,
                recovered_max=missed_base - missed_cv_indep)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # 1) per-1,000 gate ledger across prevalence x tool
    rows = []
    for tool, perf in TOOLS.items():
        for p in PREVALENCE_SCENARIOS:
            d = gate_table(p, perf["se"], perf["sp"])
            d["tool"] = tool
            rows.append(d)
    cols = ["tool", "prevalence", "se", "sp", "strokes_present", "true_pos",
            "false_neg", "false_pos", "true_neg", "ppv", "extra_cts_per_1000",
            "missed_baseline", "missed_cv_full_overlap", "missed_cv_independent",
            "recovered_min", "recovered_max"]
    with open(os.path.join(OUT, "SIM_01_output_per_1000.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(r[k], 4) if isinstance(r[k], float) else r[k])
                        for k in cols})

    # 2) door-to-recognition distributions (Monte Carlo, n=200,000)
    n = 200000
    dtr_rows = []
    base = baseline_recognition_min(rng, n)
    def qsum(name, arr, p_share):
        arr = sorted(arr)
        def q(x): return arr[int(x * len(arr))]
        return dict(arm=name, prevalence=p_share,
                    median_min=round(q(0.5), 1), p75_min=round(q(0.75), 1),
                    p90_min=round(q(0.90), 1),
                    share_over_4h=round(sum(1 for v in arr if v > 240) / len(arr), 4),
                    share_over_24h=round(sum(1 for v in arr if v > 1440) / len(arr), 4))
    dtr_rows.append(qsum("baseline", base, "all"))
    for tool, perf in TOOLS.items():
        cv = cv_recognition_min(rng, n, perf["se"])
        dtr_rows.append(qsum(tool + "_CV", cv, "all"))
    with open(os.path.join(OUT, "SIM_02_door_to_recognition.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dtr_rows[0].keys()))
        w.writeheader()
        w.writerows(dtr_rows)

if __name__ == "__main__":
    main()
