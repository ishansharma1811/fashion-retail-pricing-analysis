-- Fashion Retail Pricing & Discount Analysis  |  SQLite / ANSI-friendly
-- Table: sales (loaded from data/processed/sales_clean.csv)

-- name: category_performance
SELECT category,
       COUNT(*)                                        AS transactions,
       SUM(quantity)                                   AS units,
       ROUND(SUM(revenue), 0)                          AS revenue,
       ROUND(SUM(gross_profit), 0)                     AS gross_profit,
       ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1) AS margin_pct,
       ROUND(AVG(discount_pct), 1)                     AS avg_discount_pct,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM sales), 1) AS revenue_share_pct
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- name: discount_band_performance
SELECT discount_band,
       COUNT(*)                                        AS transactions,
       ROUND(AVG(quantity), 2)                         AS avg_units_per_txn,
       ROUND(AVG(revenue), 2)                          AS avg_revenue_per_txn,
       ROUND(AVG(gross_profit), 2)                     AS avg_profit_per_txn,
       ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1) AS margin_pct
FROM sales
GROUP BY discount_band
ORDER BY MIN(discount_pct);

-- name: category_discount_matrix
SELECT category, discount_band,
       ROUND(AVG(quantity), 2)      AS avg_units_per_txn,
       ROUND(AVG(gross_profit), 2)  AS avg_profit_per_txn,
       COUNT(*)                     AS transactions
FROM sales
GROUP BY category, discount_band
ORDER BY category, MIN(discount_pct);

-- name: monthly_trend
SELECT year_month,
       ROUND(SUM(revenue), 0)       AS revenue,
       ROUND(SUM(gross_profit), 0)  AS gross_profit,
       ROUND(100.0 * SUM(CASE WHEN is_discounted = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_txns_discounted,
       ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1) AS margin_pct
FROM sales
GROUP BY year_month
ORDER BY year_month;

-- name: month_over_month_growth   (window function)
WITH m AS (
  SELECT year_month, SUM(revenue) AS revenue FROM sales GROUP BY year_month
)
SELECT year_month,
       ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
             / LAG(revenue) OVER (ORDER BY year_month), 1) AS mom_growth_pct
FROM m;

-- name: category_rank_by_profit_per_month   (window function)
SELECT year_month, category, ROUND(SUM(gross_profit), 0) AS gross_profit,
       RANK() OVER (PARTITION BY year_month ORDER BY SUM(gross_profit) DESC) AS profit_rank
FROM sales
GROUP BY year_month, category;

-- name: channel_segment_view
SELECT channel, customer_segment,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(AVG(discount_pct), 1) AS avg_discount_pct,
       ROUND(100.0 * SUM(gross_profit) / SUM(revenue), 1) AS margin_pct
FROM sales
GROUP BY channel, customer_segment
ORDER BY revenue DESC;

-- name: discount_that_destroys_profit   (deep discounts where profit/txn < no-discount baseline)
WITH base AS (
  SELECT category, AVG(gross_profit) AS base_profit
  FROM sales WHERE discount_pct = 0 GROUP BY category
)
SELECT s.category, s.discount_band,
       ROUND(AVG(s.gross_profit), 2) AS avg_profit_per_txn,
       ROUND(b.base_profit, 2)       AS baseline_profit_per_txn,
       ROUND(100.0 * (AVG(s.gross_profit) - b.base_profit) / b.base_profit, 1) AS profit_lift_pct
FROM sales s JOIN base b USING (category)
WHERE s.discount_pct > 0
GROUP BY s.category, s.discount_band
ORDER BY s.category, MIN(s.discount_pct);
