
strokes_per_year = round(4011 * 0.367) # 1,472 self-presenting strokes (CIHI 2026; CIHI 2016)
prevalence = 0.10   # stroke prevalence among screened patients (assumed)
price_per_screen = 15  # $ per patient screened (assumed)
ct_cost = 0.899 * 490 + 0.707 * (330 + 125)  # $762 per false positive (Yu et al., 2017; Mayfair Diagnostics, 2026)
uptake = [0.25, 0.75, 1.00] # years 1 to 3 (assumed)
wtp_levels = [20000, 50000, 100000]  # $ per QALY (Xie et al., 2016)

tools = {
    "Scenario A": 0.993,   # specificity (Aldridge et al., 2022)
    "Scenario B": 0.838,   # specificity (Cai et al., 2022)
}


screened = strokes_per_year / prevalence   # 14,720 patients screened per year

print("Table 06. Annual and three-year cost of screening")
print("Current care (reference): 0 false positives, $0")
for name, specificity in tools.items():
    false_pos = screened * (1 - prevalence) * (1 - specificity)
    cost_per_screen = price_per_screen + (1 - prevalence) * (1 - specificity) * ct_cost
    annual_cost = screened * cost_per_screen
    three_year = annual_cost * sum(uptake)
    print(f"{name}: {false_pos:,.0f} false-positive CTs, "
          f"${cost_per_screen:.2f} per patient screened, "
          f"${annual_cost:,.0f} per year, ${three_year:,.0f} over three years")

print("\nTable 07. Health gain required per stroke patient: QALYs (days)")
for name, specificity in tools.items():
    annual_cost = screened * (price_per_screen + (1 - prevalence) * (1 - specificity) * ct_cost)
    results = []
    for wtp in wtp_levels:
        qaly = annual_cost / strokes_per_year / wtp
        results.append(f"${wtp:,}: {qaly:.4f} ({qaly * 365:.1f} days)")
    print(f"{name}: " + " | ".join(results))