# Fashion Retail Pricing & Discount Analysis
**SQL · Python · Pandas · Power BI**

End-to-end analysis of how discount depth affects units, revenue and profit across fashion
product categories, ending in an interactive Power BI dashboard and pricing recommendations.

## Highlights
- Cleaned ~30K messy transactions with Pandas (duplicates, mixed date formats, inconsistent category text, missing discounts, outliers, invalid quantities).
- Wrote 8 SQL queries (aggregations, CTEs, window functions: `LAG`, `RANK`) to compare categories, discount bands, channels and months.
- Quantified discount sensitivity and profit lift vs a no-discount baseline per category.
- Power BI dashboard (4 pages) with DAX measures for margin, profit lift and MoM growth.
- Headline result: deeper discounts raise units per order but cut profit per order; 41%+ discounts yield ~1% margin.

## Project structure
```
src/generate_data.py     Simulate raw transactions (with injected data-quality issues)
src/clean_transform.py   Cleaning + feature engineering -> data/processed/sales_clean.csv
src/run_sql.py           Loads SQLite, runs sql/queries.sql, exports sql_*.csv
src/analysis.py          EDA, charts, key findings
sql/queries.sql          Named SQL queries
powerbi/POWERBI_GUIDE.md Data model, DAX measures, page-by-page dashboard build
reports/findings.md      Insights and recommendations
reports/charts/          Generated charts
```

## Run it
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/clean_transform.py
python src/run_sql.py
python src/analysis.py
```
Then follow `powerbi/POWERBI_GUIDE.md` to build the dashboard from `data/processed/sales_clean.csv`.

## Using real data instead
Replace `data/raw/transactions_raw.csv` with a real export (e.g. a Kaggle fashion retail dataset)
and map its columns to: `transaction_id, order_date, category, list_price, discount_pct, quantity, unit_cost`.
Adjust `clean_transform.py` accordingly; everything downstream is unchanged.

## Cleaning log (this run)
30,450 raw rows → 30,000 after dedup → 29,975 after invalid quantities → 29,921 after outlier removal.
