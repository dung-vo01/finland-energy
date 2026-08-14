# Finland Energy Dashboard

A dashboard built on real, public electricity data from [Fingrid](https://data.fingrid.fi) — Finland's national grid operator.

Imported data: electricity production and electricity consumption from August 10th, 2025 to August 10th, 2026

**How this project evolved:** First built in Power BI. Then rebuilt in AWS QuickSight - that version started out just uploading the raw Fingrid CSVs straight to QuickSight. The current, latest version adds a Python pipeline (`scripts/`) which quality checks and cleans the raw data first before uploading the cleaned-up files to QuickSight.

## What's in the dashboard

**Overview**
- KPIs: average consumption, average production, production surplus/deficit, self-sufficiency (%)
- Weekday vs weekend average consumption and production
- Consumption vs production across the full year using 7-day rolling average

**Patterns**
- Average consumption and production in a day (hourly interval)
- Self-sufficiency (%) by month, to see whether Finland covered its own demand or leaned on imports
- Production surplus/deficit over time using a 7-day rolling average

A few things to notice:
- All values are in MWh/h, except for self sufficiency in %
- Electricity production here is domestic only, not net of imports/exports. When surplus/deficit goes negative, that means domestic production fell short of demand (consumption). So, it doesn't consider cross-border trades (import) at all, which requires separate datasets that I didn't pull in (TODO).

## Insights from data

- Finland runs at roughly 94% self-sufficiency on average, but that drops to the range of 86 - 88% during the coldest winter months (Jan–Feb), and rises to above 100% in October (102.82%).
- One abnormal spike in March 2026 (98.26%) between two lowest points (Feb and Apr) needs further investigation since it occurs in the high-demand period.
- Weekday demand consistently runs a bit above weekend demand.
- On a daily basis, both consumption and productions move along each other: rise through the morning, a broad plateau, and a small evening bump before going down through midnight.

(All the above numbers were based on the latest version in AWS QuickSight)

## Files

```
dashboards/
  finland-electricity.pbix             # the actual report, open in Power BI Desktop
  finland-electricity.pdf              # static export, viewable without Power BI
  Finland-electricity-QuickSight.gif   # demo of the same dashboard rebuilt in AWS QuickSight
data/
  raw/                                 # original CSVs from Fingrid
    electricity-consumption-124_2025-08-10T0000_2026-08-10T2355.csv
    electricity-production-74_2025-08-10T0000_2026-08-10T2355.csv
  clean/                               # output of scripts/clean_data.py, used as the SQL load source
    electricity-consumption-clean.csv
    electricity-production-clean.csv
scripts/
  quality_check_data.py    # profiles the raw CSVs (row count, nulls, duplicates, dtypes, min/max/mean/std)
  clean_data.py             # drops unusable rows, fixes non-positive values, flags outliers, fills timestamp gaps
requirements.txt
```

## How to explore it

Either open `dashboards/finland-electricity.pdf` right here in GitHub for a quick look, or download `dashboards/finland-electricity.pbix` and open it in Power BI Desktop for the full interactive version.

## QuickSight version

I rebuilt the same dashboard in Amazon QuickSight to get hands-on with AWS's BI stack: same data, same insights, different tool. The numbers can be slightly different, given they have different ways to calculate the 7-day rolling average.

Since QuickSight dashboards are gated behind AWS/Cognito login and can't be shared publicly, this GIF is the easiest way to see it in action.

![QuickSight dashboard demo](dashboards/Finland-electricity-QuickSight.gif)

## Data pipeline: quality check & clean

Rather than pulling the raw CSVs straight into a BI tool, I built a small Python pipeline to validate and clean the data first:

```
raw CSVs (Fingrid)
   ->  scripts/quality_check_data.py   — profile the raw data, no changes made
   ->  scripts/clean_data.py           — clean it, write to data/clean/
   ->  QuickSight / Power BI            — connect to the clean CSVs, build visuals
```

**1. Quality check (`scripts/quality_check_data.py`)**
Read-only report on the raw CSVs before anything is touched: row count, null counts, duplicate timestamps, column dtype, and min/max/mean/std for the value column. Run this first to see what you're working with.

**2. Cleaning (`scripts/clean_data.py`)**
- Drops rows where the timestamp can't be parsed, or the value is missing.
- Values `<= 0` are fixed via linear interpolation (physically implausible for grid consumption/production, unambiguous fix).
- Extreme outliers (outside `Q1 - 3*IQR` to `Q3 + 3*IQR`) are **flagged, not altered** — the original value is kept, and an `is_outlier` column marks it, since these could be real events (e.g. a demand spike) worth investigating rather than sensor errors.
- Any gap greater than 15 minutes between consecutive readings gets the missing interval(s) inserted, with the value linearly interpolated.
- Writes clean output to `data/clean/`.

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

The clean CSVs in `data/clean/` are what gets connected to QuickSight or Power BI

## Data source

[Fingrid Open Data](https://data.fingrid.fi) — datasets 124 (consumption) and 74 (production), 15-minute resolution, Aug 2025–Aug 2026.

## Built with

Power BI Desktop · Amazon QuickSight · Python (pandas) · Fingrid Open Data API