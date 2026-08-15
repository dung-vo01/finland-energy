# Quality check:
# - row count, null count, duplicate timestamps, dtypes, min/max/mean/std
# - gap checks in each file (missing intervals)
# - printed as a report

import pandas as pd
from pathlib import Path
import glob

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "consumption": {
        "pattern": RAW_DIR / "electricity-consumption-124_*.csv",
        "value_col": "Electricity consumption in Finland",
    },
    "production": {
        "pattern": RAW_DIR / "electricity-production-74_*.csv",
        "value_col": "Electricity production in Finland",
    },
}


def load_raw_multi(pattern: str, value_col: str) -> pd.DataFrame:
    paths = sorted(glob.glob(str(pattern)))
    if not paths:
        raise FileNotFoundError(f"No files matched: {pattern}")

    dfs = []
    for p in paths:
        df = pd.read_csv(p, sep=";")
        df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
        df = df.rename(columns={value_col: "value"})
        dfs.append(df[["startTime", "value"]])

    combined = pd.concat(dfs, ignore_index=True)
    return combined, paths


def check_gaps_per_file(paths: list[str], freq: str = "15min") -> dict:
    results = {}
    for p in paths:
        path = Path(p)
        df = pd.read_csv(path, sep=";")
        df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
        df = df.sort_values("startTime")

        expected = pd.date_range(
            df["startTime"].min(), df["startTime"].max(), freq=freq
        )
        missing = expected.difference(df["startTime"])

        results[path.name] = {
            "rows": len(df),
            "expected_rows": len(expected),
            "missing_intervals": len(missing),
        }
    
    return results


def quality_check(name: str, config: dict):
    print(f"\n=== File: {name.upper()} ===")

    df, paths = load_raw_multi(config["pattern"], config["value_col"])
    print(f"Loaded {len(df)} raw rows from {len(paths)} files.")

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

    print("\nPer-file gap check (within each file's own date range):")
    gap_stats = check_gaps_per_file(paths)
    for fname, g in gap_stats.items():
        print(f"    {fname}")
        print(
            f"      rows: {g['rows']}, expected: {g['expected_rows']}, missing intervals: {g['missing_intervals']}"
        )

    stats["gap_check"] = gap_stats

    return stats



if __name__ == "__main__":
    print("\n--- DATA QUALITY CHECK ---")

    for name, config in FILES.items():
        quality_check(name, config)