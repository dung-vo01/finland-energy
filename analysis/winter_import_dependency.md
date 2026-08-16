# Winter Import Dependency: What It Costs

*A short case study built on the Finland Energy Dashboard's 2024–2026 self-sufficiency and price data.*

## The question

Finland covers roughly 94% of its own electricity demand domestically on average — but that number hides real seasonal swings. Does the shape of that swing repeat every year, and does it show up as a measurable cost when it happens?

## Method

- **Source data:** Fingrid open data (electricity production and consumption, 15-min resolution, 2024–2026 YTD) and Nord Pool day-ahead prices for Finland (via Sähkötin, hourly, same range).
- **Approach:** aggregate both series to monthly grain, compare the same calendar month across all 3 years to separate a recurring seasonal pattern from a one-off, then overlay average monthly price against self-sufficiency to check whether the two move together.
- **Full methodology and data quality notes:** see the project [README](../README.md).

## Finding 1: October is a real, recurring surplus

Comparing self-sufficiency by month across 2024, 2025, and 2026 (year split rather than a blended average) shows October consistently peaking — above 100% self-sufficiency in both complete years of data (2024 and 2025), meaning domestic production exceeded demand. This holds up as a genuine seasonal pattern, not a single-year fluke.

## Finding 2: March 2026 is a confirmed anomaly

A single year of data had flagged an unexplained bump in March 2026, sitting between two low points, that didn't fit the expected winter-to-spring shape. Extending to 3 years of data and computing a continuous month-over-month % change confirmed it wasn't just visual noise:

- **February 2026** had the lowest self-sufficiency of the year (86.3%)
- **March 2026** jumped to 98.28% — a +13.78% month-over-month change, the **largest single swing anywhere in the 3-year dataset**

This is a real, quantifiable event, not an artifact of chart smoothing.

## Finding 3: The March swing shows up directly in price

Nord Pool day-ahead prices for the same window:

- **February 2026:** 13.72 €/MWh — the highest monthly average in the entire 3-year dataset
- **March 2026:** 2.78 €/MWh — roughly an **80% drop**

The month with the tightest domestic supply relative to demand also had the highest price. The month self-sufficiency recovered sharply, price collapsed by a similar magnitude.

## The honest caveat

This inverse relationship is real and dramatic in early 2026, but it isn't a fixed rule. Checking the same relationship in 2024 and 2025 shows it holding in some periods (e.g. January 2024) and breaking in others — in August 2024 and April–June 2025, self-sufficiency and price moved in the *same* direction, not opposite.

That means self-sufficiency is **one contributing factor to price, not the sole driver.** Price in the Nordic market is also shaped by wind output, hydro reservoir levels, and supply conditions across Sweden, Norway, and the Baltics — none of which are captured in this dataset. The 2026 result is a strong, real example of the relationship, not proof that it holds every winter.

## What this means, practically

For a business exposed to Finnish spot pricing, the takeaway isn't "self-sufficiency predicts price" — it's narrower and more useful: **periods of unusually low domestic self-sufficiency are a meaningful early signal of price risk**, worth watching alongside the more established drivers (wind forecasts, temperature, hydro levels), rather than relying on it alone.

## Next steps, not yet done

- Pull Finland wind production data (available as a separate Fingrid dataset) to check whether the March 2026 recovery coincides with a wind capacity/output spike, which would explain the mechanism rather than just the correlation.
- Compute a demand-weighted average price instead of a simple monthly mean, to better reflect what a large consumer actually paid.
- Extend the price relationship check across a longer history once more full years of data are available, to see if 2026's pattern repeats or was unusual.

---
*Dashboard and full pipeline: see the [project README](../README.md).*