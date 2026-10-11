# Power BI Dashboard Build Guide

Power BI Desktop files (.pbix) can't be generated outside Power BI, so this guide gets you
to the finished dashboard in ~45 minutes using the data this project produces.

## 1. Load data
Home → Get Data → Text/CSV → `data/processed/sales_clean.csv` → **Transform Data**:
- Set types: `order_date` = Date, money columns = Fixed decimal, `discount_pct`/`margin_pct` = Decimal.
- Rename table to `Sales`.
- Optional: also load `sql_category_performance.csv` and `profit_lift_matrix.csv` for reference visuals.

## 2. Date table (Modeling → New table)
```DAX
DimDate =
ADDCOLUMNS(
    CALENDAR(DATE(2025,1,1), DATE(2025,12,31)),
    "Year", YEAR([Date]),
    "MonthNo", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "Quarter", "Q" & QUARTER([Date])
)
```
Relate `DimDate[Date]` → `Sales[order_date]` (one-to-many). Sort `Month` by `MonthNo`.

## 3. Measures
```DAX
Revenue            = SUM(Sales[revenue])
Gross Profit       = SUM(Sales[gross_profit])
Units Sold         = SUM(Sales[quantity])
Margin %           = DIVIDE([Gross Profit], [Revenue])
Orders             = DISTINCTCOUNT(Sales[transaction_id])
Avg Discount %     = AVERAGE(Sales[discount_pct]) / 100
Discounted Orders %= DIVIDE(CALCULATE([Orders], Sales[is_discounted] = 1), [Orders])
Profit per Order   = DIVIDE([Gross Profit], [Orders])
Units per Order    = DIVIDE([Units Sold], [Orders])

Baseline Profit per Order =
CALCULATE([Profit per Order], Sales[discount_pct] = 0)

Profit Lift vs Baseline % =
DIVIDE([Profit per Order] - [Baseline Profit per Order], [Baseline Profit per Order])

Revenue MoM % =
VAR prev = CALCULATE([Revenue], DATEADD(DimDate[Date], -1, MONTH))
RETURN DIVIDE([Revenue] - prev, prev)

Deep Discount Margin % =
CALCULATE([Margin %], Sales[discount_pct] >= 40)
```

## 4. Report pages

**Page 1 – Executive Overview**
- KPI cards: Revenue, Gross Profit, Margin %, Orders, Discounted Orders %
- Line + clustered column: Revenue (columns) and Discounted Orders % (line) by `Month`
- Donut: Revenue by `channel`
- Slicers: Quarter, City, Channel, Customer Segment

**Page 2 – Category Performance**
- Clustered bar: Revenue and Gross Profit by `category`
- Table: category, Revenue, Margin %, Avg Discount %, Units per Order (conditional formatting on Margin %)
- Scatter: X = Avg Discount %, Y = Margin %, size = Revenue, details = category

**Page 3 – Discount Impact**
- Column + line: `discount_band` (sorted No discount → 41%+): Profit per Order (columns), Units per Order (line)
- Matrix: rows = category, columns = discount_band, values = Profit Lift vs Baseline %
  → Format → Cell elements → Background colour: diverging red/white/green, centre at 0
- Card: Deep Discount Margin %

**Page 4 – Recommendations** (text boxes)
Paste the recommendations from `reports/findings.md`.

## 5. Polish
Consistent palette (one colour for revenue, one for profit), turn on tooltips, add a Reset-filters
bookmark button, and set the theme under View → Themes. Export a PDF or publish to Power BI Service
and add a screenshot to the repo's README.
