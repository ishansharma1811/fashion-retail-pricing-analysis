# Key Findings & Recommendations

Dataset: 29,921 clean transactions, Jan–Dec 2025, 7 categories, 6 cities, 2 channels.
Total revenue 3.74M, gross profit 1.59M, blended margin 42.5%.

## What the data shows
1. **Discounts grow units but shrink profit.** Moving from no discount to 31–40% off raises units per order from 2.2 to 3.1 (+43%), yet profit per order falls from 63.8 to 17.8 (-72%).
2. **43% of orders are discounted but they earn only 32% of profit** (42% of revenue).
3. **41%+ discounts are break-even at best.** Margin on these orders is about 1%; Footwear, Outerwear and Activewear lose money at that depth.
4. **Footwear and Outerwear are the least discount-sensitive** (elasticity 0.45 and 0.57) and have the thinnest margins (34% and 37%), so discounts there give away margin for little extra volume. Footwear is the #1 revenue category.
5. **Accessories and Dresses respond most to discounts** (elasticity about 0.9) and carry high margins (54% and 47%), making them the best candidates for promotions.
6. **Promo months drag margin.** January and July (end-of-season) run ~75% discounted orders with margins about 37% vs about 45% in regular months. Revenue in those months is not meaningfully higher.

## Recommendations
- **Cap discounts at 20% for Footwear and Outerwear.** Even 11-20% already cuts profit per order by 33-41% there.
- **Never run 40%+ sitewide.** Reserve it for clearance of aged stock, as an explicit loss-leader decision.
- **Concentrate promotions on Accessories, Dresses and Tops,** where volume lift partly offsets margin loss.
- **Use bundles and thresholds instead of blanket cuts** (for example, accessory add-on at 15% off with any outerwear or footwear purchase).
- **Shorten end-of-season sales** (Jan/Jul) and test a smaller promo footprint, since revenue barely moves while margin drops about 8 points.
- **Measure promotions on profit per order, not revenue or units.** Track `Profit Lift vs Baseline %` on the dashboard.

## Caveats
Data is synthetic, generated with built-in elasticity and cost assumptions. The method (cleaning,
SQL, baselining, Power BI model) transfers to real data, but conclusions should be re-validated on it.
Discount depth is not randomised, so elasticity here is observational, not causal.
