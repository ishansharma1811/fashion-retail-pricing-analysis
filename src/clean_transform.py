"""Clean raw transactions and engineer the features used by SQL / Power BI."""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "transactions_raw.csv"
OUT = ROOT / "data" / "processed" / "sales_clean.csv"

df = pd.read_csv(RAW)
log = {"raw_rows": len(df)}

# 1. Duplicates
df = df.drop_duplicates()
log["after_dedup"] = len(df)

# 2. Dates (two formats in the raw file)
d1 = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
d2 = pd.to_datetime(df["order_date"], format="%d/%m/%Y", errors="coerce")
df["order_date"] = d1.fillna(d2)
df = df.dropna(subset=["order_date"])

# 3. Text standardisation
df["category"] = df["category"].str.strip().str.title()
df["city"] = df["city"].fillna("Unknown")

# 4. Invalid quantities
df = df[df["quantity"] > 0]
log["after_invalid_qty"] = len(df)

# 5. Missing discount: recover from list vs. net price instead of dropping
implied = (1 - df["net_price"] / df["list_price"]) * 100
df["discount_pct"] = df["discount_pct"].fillna(implied.round(-1)).clip(0, 90)

# 6. Price outliers: flag per category using IQR, then drop the extreme ones
q1 = df.groupby("category")["list_price"].transform(lambda s: s.quantile(.25))
q3 = df.groupby("category")["list_price"].transform(lambda s: s.quantile(.75))
upper = q3 + 3 * (q3 - q1)
df = df[df["list_price"] <= upper]
log["after_outliers"] = len(df)

# 7. Recompute money columns consistently from clean inputs
df["net_price"] = (df["list_price"] * (1 - df["discount_pct"] / 100)).round(2)
df["revenue"] = (df["net_price"] * df["quantity"]).round(2)
df["cogs"] = (df["unit_cost"] * df["quantity"]).round(2)
df["gross_profit"] = (df["revenue"] - df["cogs"]).round(2)
df["margin_pct"] = np.where(df["revenue"] > 0, df["gross_profit"] / df["revenue"] * 100, np.nan).round(2)

# 8. Features
df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
df["month"] = df["order_date"].dt.month
df["quarter"] = "Q" + df["order_date"].dt.quarter.astype(str)
df["day_of_week"] = df["order_date"].dt.day_name()
df["discount_band"] = pd.cut(
    df["discount_pct"], bins=[-1, 0, 10, 20, 30, 40, 100],
    labels=["No discount", "1-10%", "11-20%", "21-30%", "31-40%", "41%+"]).astype(str)
df["is_discounted"] = (df["discount_pct"] > 0).astype(int)

df = df.sort_values("order_date").reset_index(drop=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
log["final_rows"] = len(df)
for k, v in log.items():
    print(f"{k:>18}: {v:,}")
print(f"Saved -> {OUT}")
