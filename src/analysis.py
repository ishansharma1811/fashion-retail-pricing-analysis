"""EDA + pricing insights. Produces charts in reports/charts and prints key findings."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "reports" / "charts"
CH.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(ROOT / "data" / "processed" / "sales_clean.csv", parse_dates=["order_date"])
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})
BANDS = ["No discount", "1-10%", "11-20%", "21-30%", "31-40%", "41%+"]

# 1. Revenue vs profit by category
cat = df.groupby("category").agg(revenue=("revenue", "sum"), profit=("gross_profit", "sum")).sort_values("revenue")
ax = (cat / 1000).plot.barh(figsize=(8, 4.5), color=["#4C78A8", "#54A24B"])
ax.set(title="Revenue and gross profit by category", xlabel="Thousands")
plt.tight_layout(); plt.savefig(CH / "01_category_revenue_profit.png"); plt.close()

# 2. Units lift vs profit per transaction, by discount band
b = df.groupby("discount_band").agg(units=("quantity", "mean"), profit=("gross_profit", "mean")).reindex(BANDS)
fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.bar(b.index, b.profit, color="#54A24B"); ax1.set_ylabel("Avg profit per transaction")
ax2 = ax1.twinx(); ax2.plot(b.index, b.units, color="#E45756", marker="o"); ax2.set_ylabel("Avg units per transaction")
ax1.set_title("Deeper discounts lift units but erode profit"); plt.tight_layout()
plt.savefig(CH / "02_discount_units_vs_profit.png"); plt.close()

# 3. Heatmap: profit lift vs no-discount baseline, category x band
base = df[df.discount_pct == 0].groupby("category")["gross_profit"].mean()
m = df[df.discount_pct > 0].groupby(["category", "discount_band"])["gross_profit"].mean().unstack()[BANDS[1:]]
lift = m.sub(base, axis=0).div(base, axis=0) * 100
fig, ax = plt.subplots(figsize=(8, 4.5))
im = ax.imshow(lift, cmap="RdYlGn", vmin=-80, vmax=80)
ax.set_xticks(range(lift.shape[1]), lift.columns); ax.set_yticks(range(lift.shape[0]), lift.index)
for i in range(lift.shape[0]):
    for j in range(lift.shape[1]):
        ax.text(j, i, f"{lift.iat[i, j]:.0f}%", ha="center", va="center", fontsize=8)
ax.set_title("Profit-per-transaction change vs. no discount"); fig.colorbar(im, label="% change")
plt.tight_layout(); plt.savefig(CH / "03_profit_lift_heatmap.png"); plt.close()

# 4. Monthly revenue + discount penetration
mo = df.groupby("year_month").agg(rev=("revenue", "sum"), pen=("is_discounted", "mean"))
fig, ax1 = plt.subplots(figsize=(9, 4.5))
ax1.bar(mo.index, mo.rev / 1000, color="#4C78A8"); ax1.set_ylabel("Revenue (thousands)")
ax2 = ax1.twinx(); ax2.plot(mo.index, mo.pen * 100, color="#F58518", marker="o"); ax2.set_ylabel("% transactions discounted")
plt.setp(ax1.get_xticklabels(), rotation=45); ax1.set_title("Monthly revenue vs. discount penetration")
plt.tight_layout(); plt.savefig(CH / "04_monthly_trend.png"); plt.close()

# 5. Discount elasticity per category (log-log slope of units on (1 - discount))
rows = []
for c, g in df.groupby("category"):
    x = np.log(1 - g.discount_pct / 100); y = np.log(g.quantity)
    rows.append((c, np.polyfit(x, y, 1)[0] * -1))
el = pd.DataFrame(rows, columns=["category", "elasticity"]).sort_values("elasticity")
ax = el.plot.barh(x="category", y="elasticity", legend=False, figsize=(7, 4), color="#B279A2")
ax.axvline(0.5, ls="--", c="grey"); ax.set(title="Estimated discount sensitivity of units (log-log slope)", xlabel="Elasticity")
plt.tight_layout(); plt.savefig(CH / "05_category_elasticity.png"); plt.close()

# ---------- Findings ----------
tot_rev, tot_gp = df.revenue.sum(), df.gross_profit.sum()
print(f"Total revenue {tot_rev:,.0f} | gross profit {tot_gp:,.0f} | margin {tot_gp / tot_rev:.1%}")
d = df[df.is_discounted == 1]
print(f"Discounted txns: {len(d) / len(df):.1%} of orders, {d.revenue.sum() / tot_rev:.1%} of revenue, {d.gross_profit.sum() / tot_gp:.1%} of profit")
print("\nProfit lift vs no-discount baseline (%):"); print(lift.round(0).to_string())
print("\nElasticity:"); print(el.round(2).to_string(index=False))
deep = df[df.discount_pct >= 40]
print(f"\n40%+ discounts: {len(deep) / len(df):.1%} of orders, margin {deep.gross_profit.sum() / deep.revenue.sum():.1%}")
lift.round(1).to_csv(ROOT / "data" / "processed" / "profit_lift_matrix.csv")
