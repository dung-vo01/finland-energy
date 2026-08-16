# Finland Energy Dashboard

A dashboard built on real, public data covering Finland's electricity production and consumption from [Fingrid](https://data.fingrid.fi) (Finland's national grid operator) and electricity hourly price from [Nord Pool day-ahead prices](https://sahkotin.fi) via the Sähkötin API.

Data covers **January 2024 through July 2026**.

**How this project evolved:** First built in Power BI on a single year of data. Rebuilt in AWS QuickSight with a Python pipeline (`scripts/`) that quality-checks and cleans the raw data before it ever reaches a BI tool. Later expanded to 3 years of history, then extended with Nord Pool price data to connect self-sufficiency patterns to their actual cost impact.

## What's in the dashboard

**Overview**
- KPIs: average consumption, average production, production surplus/deficit, self-sufficiency (%)
- Weekday vs weekend average consumption and production
- Consumption vs production across the full 3-year range, 7-day rolling average
- Year and month-year filters

**Patterns**
- Average consumption and production by hour of day
- Self-sufficiency (%) by month, averaged across all 3 years
- Production surplus/deficit over time, 7-day rolling average

**Trends**
- Self-sufficiency by month, split by year (2024/2025/2026) — tests whether seasonal patterns actually repeat year to year
- Continuous month-over-month % change in self-sufficiency across the full 3-year timeline
- Finding: October is a consistent seasonal peak in both complete years of data (2024 and 2025). March 2026 stands out as an outlier: its Feb - Mar swing (+13.78%) is the largest month-over-month change in the dataset, well above the typical seasonal transition seen in 2024/2025.

**Price**
- Self-sufficiency vs. Nord Pool day-ahead price, dual-axis, filterable by year
- Finding: February 2026 combined the lowest self-sufficiency of the year (86.3%) with the highest price (13.72 €/MWh). March 2026 saw self-sufficiency jump to 98.28% while price fell to 2.78 €/MWh, roughly an 80% drop. The same inverse pattern appears in parts of 2024 and 2025 but isn't consistent year-round, suggesting self-sufficiency is one contributing factor to price rather than the sole driver.

**Forecast**
- 14-day forecast of the consumption/production 7-day rolling average, built on the full historical series.

## Key insights

- **Finland averages 94% self-sufficiency, but winter is where it actually matters.** Jan-Feb consistently sits lowest, exactly when demand is highest, which is the window where import dependency is real.
- **October is a genuine, recurring seasonal surplus**, confirmed by comparing the same month across both complete years (2024 and 2025).
- **March 2026 is a confirmed anomaly.** Its month-over-month self-sufficiency swing (+13.78%) is the largest in the 3-year dataset, and it coincides with an almost 80% price drop in the same window.
- **Self-sufficiency and price move inversely at times, but not reliably year-round.** The relationship is clearest in early 2026; it breaks down in parts of 2024 and 2025 (e.g. Aug 2024, Apr–Jun 2025), meaning price is driven by more than domestic supply alone, for example, plausible other factors include wind output and cross-Nordic supply conditions, not investigated here (see Limitations).
- **Weekday demand is consistently higher than weekend**, and **daily production tracks demand closely** rather than running independently which is consistent with a grid balancing supply in near real-time.

This is domestic production only, with no import/export data — "self-sufficiency" means how much of Finland's own demand was covered domestically, not literal energy independence. A shortfall means imports made up the difference, not an outage.

## Case study
 
[**Winter Import Dependency: What It Costs**](analysis/winter_import_dependency.md) — pulls together the Trends and Price page findings into a short write-up: the recurring October surplus, the confirmed March 2026 anomaly, and its ~80% price swing, with an honest look at where the self-sufficiency/price relationship does and doesn't hold across all 3 years.

## Data quality notes

A few things worth knowing about the underlying data, found while building the pipeline:

- **The 2024 file has a notably higher rate of missing 15-min intervals than 2025 or 2026** (356 for consumption, 354 for production — vs. 34/0 in 2025 and 0/1 in 2026). Missing data are interpolated via the standard gap-filling step.
- **The 2025 file's row count runs 1 higher than the naive expected-interval calculation** — traced to the October 2025 DST transition adding a genuine extra UTC interval, not a data error.
- Calendar fields (`year`, `month`, etc.) are derived from **Finland local time** (`Europe/Helsinki`), not UTC, to avoid a few boundary hours mislabeling as the wrong year/month.

## Files

```
analysis/
  winter-import-dependency.md                 # case study write-up
dashboards/
  finland-electricity.pbix                    # original Power BI report, open in Power BI Desktop
  finland-electricity-dashboard.pdf           # static export of QuickSight dashboard
  Finland-electricity-dashboard-demo.gif      # demo of the QuickSight dashboard
data/
  raw/                                        # original CSVs — see "Data setup" below
    electricity-consumption-124_*.csv         # Fingrid, one file per calendar year
    electricity-production-74_*.csv           # Fingrid, one file per calendar year
    electricity-prices-hourly-*.csv           # Nord Pool day-ahead price, one file per calendar year
  clean/                                      # output of scripts/clean_data.py
    electricity-consumption-3y-clean.csv
    electricity-production-3y-clean.csv
    electricity-price-monthly-3y-clean.csv
scripts/
  quality_check_data.py                       # profiles raw electricity + price CSVs: row counts, nulls, duplicates, gap checks
  clean_data.py                               # dedupes, drops bad rows, interpolates, flags outliers, fills gaps, aggregates price to monthly
requirements.txt
```

## Data pipeline

```
raw CSVs (Fingrid + Sähkötin)
   ->  scripts/quality_check_data.py   — profile the raw data, no changes made
   ->  scripts/clean_data.py           — clean electricity data, aggregate price to monthly, write to data/clean/
   ->  QuickSight                       — connect to the clean CSVs, build visuals
```

**1. Quality check (`scripts/quality_check_data.py`)**
Read-only report on the raw CSVs: row count, null counts, duplicate timestamps, dtype, min/max/mean/std, and a per-file gap check (missing intervals within each file's own date range). Run this first.

**2. Cleaning — electricity (consumption/production)**
- Merges multiple yearly files per dataset, removing duplicate timestamps (keeps the most recently-pulled value if duplicates disagree).
- Drops rows with an unparseable timestamp or missing value.
- Values `<= 0` are fixed via linear interpolation (physically implausible for grid data).
- Extreme outliers (outside `Q1 - 3*IQR` to `Q3 + 3*IQR`) are **flagged, not altered** — kept as-is with an `is_outlier` column, since these may be real demand/production events worth investigating rather than sensor errors.
- Gaps greater than 15 minutes get the missing interval(s) inserted and linearly interpolated.
- Calendar fields (`year`, `month`, `month_name`, `month_year`, `month_year_sort`, `date`, `day`, `hour`) are derived from Finland local time.

**3. Cleaning — price**
- Merges yearly price files, deduplicates.
- **No interpolation, no outlier flagging, no gap-filling.** Negative and zero prices are real Nord Pool market signal (oversupply), not errors. A missing price hour reflects something real about that hour rather than a value to estimate.
- Aggregated directly to a monthly average (`year`, `month`, `avg_price_eur_mwh`).

## Data setup

Raw CSVs are not committed to this repo (kept out to control repo size). To reproduce:

**Electricity (consumption/production):** [Fingrid Open Data](https://data.fingrid.fi) — dataset 124 (consumption) and dataset 74 (production), 15-minute resolution. Pull one calendar-year file per year (Jan 1 00:00 to Dec 31 23:55, local time) and save to `data/raw/` following the existing naming convention.

**Price:** [Sähkötin](https://sahkotin.fi/api) provides free Nord Pool day-ahead prices for Finland (FI bidding zone), sourced via the Porssisahko.net API. Example query for one calendar year:
```
https://sahkotin.fi/prices.csv?fix&start=YYYY-12-31T22:00:00.000Z&end=YYYY-12-31T21:59:59.000Z
```
(Start/end are offset to `22:00 UTC` the prior day, since Finland is UTC+2/+3 — this aligns the pull to local-time year boundaries.) Save as `electricity-prices-hourly-YYYY.csv` in `data/raw/`.

## Running locally

Requires Python 3.10+.

```bash
# from the repo root
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# 1. profile the raw data
python3 scripts/quality_check_data.py

# 2. clean it — writes to data/clean/
python3 scripts/clean_data.py
```

## QuickSight dashboard

Built in AWS QuickSight across 5 pages: Overview, Patterns, Trends, Price, and Forecast. Since QuickSight dashboards are gated behind AWS/Cognito login and can't be shared publicly, see `dashboards/` for static exported dashboard (finland-electricity-dashboard.pdf). Below is a short demo of the dashboard on AWS QuickSight.

![QuickSight dashboard demo](dashboards/finland-electricity-dashboard-demo.gif)

## Limitations

- Production figures are domestic only — no cross-border import/export data, so "self-sufficiency" reflects domestic coverage of demand, not literal energy independence.
- 2026 data is partial (through July) — any comparison involving 2026 totals or full-year averages should be read as year-to-date, not a complete year.
- The self-sufficiency/price relationship is directional, not causal — price is influenced by factors beyond domestic self-sufficiency (e.g. wind output, cross-Nordic supply) that weren't independently tested here.
- Price averages are simple (unweighted) monthly means, not demand-weighted — a demand-weighted average would better reflect what a large consumer actually paid on average.

## Data sources

- [Fingrid Open Data](https://data.fingrid.fi) — datasets 124 (consumption) and 74 (production), 15-minute resolution.
- [Sähkötin](https://sahkotin.fi/api) — Nord Pool day-ahead prices for Finland, sourced via Porssisahko.net.

## Built with

Power BI Desktop · AWS QuickSight · Python (pandas) · Fingrid Open Data API · Sähkötin API