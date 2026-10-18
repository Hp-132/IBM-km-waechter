# analyze.py
# Summary: km_since_service and load_factor show the largest gaps between cars that broke down
# and those that did not. odometer_km and age_years show moderate gaps; avg_daily_km is the
# weakest separator. All conclusions are associative, not causal — the sample has only 26
# breakdowns out of 120 cars, so treat these numbers as indicators, not proof.
#
# Methodology: split the 120-car fleet into broke_down=1 (26 cars) and broke_down=0 (94 cars).
# For every numeric column compute mean and median for each group and the absolute gap.
# No machine learning.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

numeric_cols = [c for c in df.columns if c not in ("car_id", "broke_down")]

broke    = df[df["broke_down"] == 1]
not_broke = df[df["broke_down"] == 0]

print("=" * 70)
print(f"Breakdown-risk analysis   —   {len(df)} cars total, "
      f"{len(broke)} broke down, {len(not_broke)} did not")
print("=" * 70)

rows = []
for col in numeric_cols:
    b_mean   = broke[col].mean()
    b_median = broke[col].median()
    n_mean   = not_broke[col].mean()
    n_median = not_broke[col].median()
    gap_mean = abs(b_mean - n_mean)
    rows.append({
        "column":   col,
        "broke_mean":    b_mean,
        "broke_median":  b_median,
        "ok_mean":       n_mean,
        "ok_median":     n_median,
        "gap_mean":      gap_mean,
    })

# Print each column in detail
for r in rows:
    print(f"\n  {r['column']}")
    print(f"    broke down  : mean={r['broke_mean']:>8.2f}   median={r['broke_median']:>8.2f}")
    print(f"    no breakdown: mean={r['ok_mean']:>8.2f}   median={r['ok_median']:>8.2f}")
    print(f"    gap (mean)  : {r['gap_mean']:.2f}")

# Rank columns by gap descending
print()
print("=" * 70)
print("Columns ranked by mean gap (largest = best separator):")
print("=" * 70)
rows_sorted = sorted(rows, key=lambda x: x["gap_mean"], reverse=True)
for r in rows_sorted:
    direction = "HIGHER in broke-down" if rows[numeric_cols.index(r["column"])]["broke_mean"] > rows[numeric_cols.index(r["column"])]["ok_mean"] else "LOWER in broke-down"
    print(f"  {r['column']:<22}  gap={r['gap_mean']:>7.2f}   ({direction})")

print()
print("=" * 70)
print("Interpretation:")
print("=" * 70)

# Compute a simple 0-100 risk score for each car from the top separating columns.
# Score = normalised (0-1) position in each column's range, averaged, scaled to 100.
# Only columns whose mean gap exceeds the median gap across all columns are included.
threshold_gap = sorted([r["gap_mean"] for r in rows])[len(rows) // 2]
separating = [r["column"] for r in rows if r["gap_mean"] >= threshold_gap]

print(f"  Columns included in risk score (gap >= median gap {threshold_gap:.1f}): {separating}")
print()

df_score = df.copy()
score_parts = []
for col in separating:
    col_min = df_score[col].min()
    col_max = df_score[col].max()
    if col_max == col_min:
        normalised = pd.Series([0.5] * len(df_score))
    else:
        normalised = (df_score[col] - col_min) / (col_max - col_min)
    score_parts.append(normalised)

df_score["risk_score"] = sum(score_parts) / len(score_parts) * 100
df_score = df_score.sort_values("risk_score", ascending=False)

print("Top 10 highest-risk cars:")
print(df_score[["car_id", "risk_score", "broke_down"] + separating].head(10).to_string(index=False))
print()
print("LIMITS: Only 26 breakdowns. Association, not causation.")
