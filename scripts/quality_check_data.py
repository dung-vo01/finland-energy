# Quality check:
# - row count, null count, duplicate timestamps, dtypes, min/max/mean/std
# - printed as a report

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "consumption": {
        "path": RAW_DIR
        / "electricity-consumption-124_2025-08-10T0000_2026-08-10T2355.csv",
        "value_col": "Electricity consumption in Finland",
    },
    "production": {
        "path": RAW_DIR
        / "electricity-production-74_2025-08-10T0000_2026-08-10T2355.csv",
        "value_col": "Electricity production in Finland",
    },
}


def load_raw(path: str, value_col: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
    df = df.rename(columns={value_col: "value"})
    return df[["startTime", "value"]]


def quality_check(name: str, config: dict):
    print(f"\n=== File: {name.upper()} ===")

    df = load_raw(config["path"], config["value_col"])
    print(f"Loaded {len(df)} raw rows.")

    stats = {
        "row_count": len(df),
        "null_startTime": int(df["startTime"].isna().sum()),
        "null_value": int(df["value"].isna().sum()),
        "duplicate_startTime": int(df["startTime"].duplicated().sum()),
        "value_dtype": str(df["value"].dtype),
        "value_min": round(df["value"].min(), 2),
        "value_max": round(df["value"].max(), 2),
        "value_mean": round(df["value"].mean(), 2),
        "value_std": round(df["value"].std(), 2),
    }

    print(f"Rows: {stats['row_count']}")
    print(f"Null startTime: {stats['null_startTime']}")
    print(f"Null value: {stats['null_value']}")
    print(f"Duplicate startTime values: {stats['duplicate_startTime']}")
    print(f"Value dtype: {stats['value_dtype']}")
    print(f"Value range ([min, max]): [{stats['value_min']}, {stats['value_max']}]")
    print(f"Value mean: {stats['value_mean']}")
    print(f"Value std: {stats['value_std']}")

    return stats


if __name__ == "__main__":
    print("\n--- DATA QUALITY CHECK ---")
    for name, config in FILES.items():
        quality_check(name, config)
