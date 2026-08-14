# Clean raw data

# Clean-up criteria:

# Row-level (dropped entire row):
# - startTime that can not be parsed as a timestamp. However, in real-life scenario,
# the row should be flagged instead of removing completely since the energy value can be valid.
# - Missing energy value: this is safe to remove the entire completely

# Value-level:
# - Value <= 0: use linear interpolation to patch
# - Value outside [Q1 - 3*IQR, Q3 + 3*IQR] (extreme statistical outlier):
# flag only, so the user can make further investigation.


# Timestamp gaps:
# - Any gap > 15 minutes between consecutive rows will get the missing
# 15-min slot(s) inserted and the value linearly interpolated


import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "consumption": {
        "path": RAW_DIR
        / "electricity-consumption-124_2025-08-10T0000_2026-08-10T2355.csv",
        "value_col": "Electricity consumption in Finland",
        "out_col": "consumption_mwh_h",
        "out_path": CLEAN_DIR
        / "electricity-consumption-124_2025-08-10T0000_2026-08-10T2355-clean.csv",
    },
    "production": {
        "path": RAW_DIR
        / "electricity-production-74_2025-08-10T0000_2026-08-10T2355.csv",
        "value_col": "Electricity production in Finland",
        "out_col": "production_mwh_h",
        "out_path": CLEAN_DIR
        / "electricity-production-74_2025-08-10T0000_2026-08-10T2355-clean.csv",
    },
}


def load_raw(path: str, value_col: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
    df = df.rename(columns={value_col: "value"})
    return df[["startTime", "value"]]


def drop_bad_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    n_start = len(df)

    bad_timestamp = df["startTime"].isna()
    bad_value = df["value"].isna()

    stats = {
        "dropped_bad_timestamp": int(bad_timestamp.sum()),
        "dropped_missing_value": int((bad_value & ~bad_timestamp).sum()),
    }

    df = df[~bad_timestamp & ~bad_value].copy()
    stats["rows_dropped_total"] = n_start - len(df)
    return df, stats


def handle_bad_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.sort_values("startTime").reset_index(drop=True)

    q1, q3 = df["value"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr

    is_non_positive = df["value"] <= 0
    is_extreme = (df["value"] < lower_bound) | (df["value"] > upper_bound)
    is_outlier = is_extreme & ~is_non_positive

    stats = {
        "iqr_lower_bound": round(lower_bound, 2),
        "iqr_upper_bound": round(upper_bound, 2),
        "values_non_positive": int(is_non_positive.sum()),
        "values_flagged_outlier": int(is_outlier.sum()),
    }

    df.loc[is_non_positive, "value"] = np.nan
    df["value"] = df["value"].interpolate(method="linear", limit_direction="both")

    df["is_outlier"] = is_outlier

    return df, stats


def fill_timestamp_gaps(
    df: pd.DataFrame, freq: str = "15min"
) -> tuple[pd.DataFrame, dict]:
    df = df.sort_values("startTime").set_index("startTime")

    full_index = pd.date_range(df.index.min(), df.index.max(), freq=freq)
    n_missing = len(full_index) - len(df)

    df = df.reindex(full_index)
    df["value"] = df["value"].interpolate(method="linear", limit_direction="both")
    df["is_outlier"] = df["is_outlier"].fillna(False)

    df = df.reset_index().rename(columns={"index": "startTime"})
    stats = {"missing_intervals_filled": int(n_missing)}
    return df, stats


def clean_file(name: str, config: dict) -> None:
    print(f"\n=== File: {name.upper()} ===")

    df = load_raw(config["path"], config["value_col"])
    print(f"Loaded {len(df)} raw rows.")

    df, drop_stats = drop_bad_rows(df)
    print(
        f"Dropped {drop_stats['rows_dropped_total']} rows "
        f"(bad timestamp: {drop_stats['dropped_bad_timestamp']}, "
        f"missing value: {drop_stats['dropped_missing_value']})."
    )

    df, value_stats = handle_bad_values(df)
    print(
        f"IQR bounds: [{value_stats['iqr_lower_bound']}, {value_stats['iqr_upper_bound']}]"
    )
    print(
        f"Fixed {value_stats['values_non_positive']} non-positive values via interpolation."
    )
    print(
        f"Flagged {value_stats['values_flagged_outlier']} extreme outliers "
        f"(kept as-is, marked in `is_outlier` column for review)."
    )

    df, gap_stats = fill_timestamp_gaps(df)
    print(
        f"Filled {gap_stats['missing_intervals_filled']} missing 15-min intervals via interpolation."
    )

    df = df.rename(columns={"value": config["out_col"]})
    df = df[["startTime", config["out_col"], "is_outlier"]]
    df.to_csv(config["out_path"], index=False)
    print(f"Wrote {len(df)} clean rows to {config['out_path']}")


if __name__ == "__main__":
    print("\n--- CLEANING DATA ---")
    for name, config in FILES.items():
        clean_file(name, config)
