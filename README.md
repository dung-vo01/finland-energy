# Finland Energy Dashboard

A Power BI dashboard built on real, public electricity data from [Fingrid](https://data.fingrid.fi) — Finland's national grid operator. 

Imported data: electricity production and electricity consumption from August 10th, 2025 to August 10th, 2026


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

- Finland runs at roughly 94% self-sufficiency on average, but that drops to the range of 86 - 88% during the coldest winter months (Jan–Feb), and rises to above 100% in October (102.86%).
- One abnormal spike in March 2026 (98.28%) between two lowest points (Feb and Apr) needs further investigation since it occurs in the high-demand period.
- Weekday demand consistently runs a bit above weekend demand.
- On a daily basis, both consumption and productions move along each other: rise through the morning, a broad plateau, and a small evening bump before going down through midnight.

## Files

```
dashboards/
  finland-electricity.pbix    # the actual report, open in Power BI Desktop
  finland-electricity.pdf     # static export, viewable without Power BI
data/
  electricity-consumption-124_2025-08-10T0000_2026-08-10T2355.csv    # raw consumption data from Fingrid
  electricity-production-74_2025-08-10T0000_2026-08-10T2355.csv      # raw production data from Fingrid
```

## How to explore it

Either open `dashboards/finland-electricity.pdf` right here in GitHub for a quick look, or download `dashboards/finland-electricity.pbix` and open it in Power BI Desktop for the full interactive version.

## Data source

[Fingrid Open Data](https://data.fingrid.fi) — datasets 124 (consumption) and 74 (production), 15-minute resolution, Aug 2025–Aug 2026.

## Built with

Power BI Desktop · Fingrid Open Data API
