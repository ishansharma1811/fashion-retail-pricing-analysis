"""Generate a realistic, deliberately messy fashion-retail transaction dataset.

Why synthetic? Real retail data is proprietary. This script simulates one year of
transactions with built-in category margins, discount elasticity and seasonality,
plus typical data-quality problems (duplicates, mixed casing, missing values,
bad dates) so the cleaning step in clean_transform.py has real work to do.
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N = 30_000
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "transactions_raw.csv"

# category: (avg list price, cost ratio, discount elasticity, share of demand)
CATS = {
    "Tops":        (35,  0.45, 1.6, 0.22),
    "Bottoms":     (55,  0.48, 1.3, 0.16),
    "Dresses":     (70,  0.46, 1.8, 0.14),
    "Outerwear":   (120, 0.55, 1.1, 0.09),
    "Footwear":    (90,  0.58, 0.9, 0.13),
    "Activewear":  (48,  0.50, 1.4, 0.12),
    "Accessories": (25,  0.40, 2.0, 0.14),
}
CHANNELS = ["Online", "In-store"]
SEGMENTS = ["New", "Returning", "Loyalty"]
CITIES = ["Jaipur", "Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad"]

names = list(CATS)
shares = np.array([CATS[c][3] for c in names])
cat = RNG.choice(names, size=N, p=shares / shares.sum())

dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(RNG.integers(0, 365, N), unit="D")

def promo_prob(d):
    m, day = d.month, d.day
    if m in (1, 7):                    # end-of-season sales
        return 0.75
    if m == 11 and day >= 20:          # Black Friday window
        return 0.85
    if m in (10, 12):                  # festive
        return 0.55
    return 0.30

p = np.array([promo_prob(d) for d in dates])
is_promo = RNG.random(N) < p
disc_levels = np.array([0.10, 0.20, 0.30, 0.40, 0.50])
disc_probs = np.array([0.25, 0.30, 0.25, 0.14, 0.06])
discount = np.where(is_promo, RNG.choice(disc_levels, N, p=disc_probs), 0.0)

list_price = np.array([CATS[c][0] for c in cat]) * RNG.lognormal(0, 0.18, N)
cost_ratio = np.array([CATS[c][1] for c in cat])
elast = np.array([CATS[c][2] for c in cat])

# Units per transaction rise with discount depth (category-specific elasticity)
lam = 1.2 * (1 + elast * discount * 1.4)
qty = RNG.poisson(lam) + 1

df = pd.DataFrame({
    "transaction_id": [f"T{100000 + i}" for i in range(N)],
    "order_date": dates,
    "city": RNG.choice(CITIES, N, p=[.12, .22, .22, .18, .13, .13]),
    "channel": RNG.choice(CHANNELS, N, p=[.45, .55]),
    "customer_segment": RNG.choice(SEGMENTS, N, p=[.30, .45, .25]),
    "category": cat,
    "list_price": list_price.round(2),
    "discount_pct": (discount * 100).round(0),
    "quantity": qty,
    "unit_cost": (list_price * cost_ratio).round(2),
})
df["net_price"] = (df.list_price * (1 - df.discount_pct / 100)).round(2)

# ---------- inject real-world mess ----------
n = len(df)
df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
idx = RNG.choice(n, int(n * 0.03), replace=False)          # mixed date formats
df.loc[idx, "order_date"] = pd.to_datetime(df.loc[idx, "order_date"]).dt.strftime("%d/%m/%Y")
idx = RNG.choice(n, int(n * 0.05), replace=False)          # messy category text
df.loc[idx, "category"] = df.loc[idx, "category"].apply(
    lambda s: RNG.choice([s.upper(), s.lower(), " " + s + " "]))
df.loc[RNG.choice(n, int(n * 0.02), replace=False), "discount_pct"] = np.nan   # missing discount
df.loc[RNG.choice(n, int(n * 0.01), replace=False), "city"] = np.nan
df.loc[RNG.choice(n, 40, replace=False), "list_price"] *= 25                    # price outliers
df.loc[RNG.choice(n, 25, replace=False), "quantity"] = -1                       # bad quantities
df = pd.concat([df, df.sample(int(n * 0.015), random_state=1)], ignore_index=True)  # duplicates
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Wrote {len(df):,} raw rows -> {OUT}")
