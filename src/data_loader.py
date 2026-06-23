"""
data_loader.py — loads German electricity load data from either:
  (a) manually-exported CSV files from the ENTSO-E Transparency Platform UI, or
  (b) the live ENTSO-E API via the entsoe-py client (requires an API key)

Both paths normalize to the same schema: a DataFrame with columns
['timestamp', 'load_mw'], indexed by timestamp, at 15-minute resolution.
This lets every downstream script (features, models, eval) stay source-agnostic.

Usage:
    python data_loader.py --source csv
    python data_loader.py --source api --start 2023-01-01 --end 2024-12-31
"""

import argparse
import glob
import os
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_PATH = DATA_DIR / "processed" / "load_germany.parquet"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip BOM characters, leading/trailing whitespace, and normalize case
    for matching purposes. Windows-exported CSVs (e.g. from Chrome) often
    include a UTF-8 BOM (\\ufeff) prepended to the first column name, which
    silently breaks exact-string column matching after concat — this is the
    most common cause of 'columns not found' errors when individual files
    loaded fine on their own."""
    df = df.copy()
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df


def load_from_csv() -> pd.DataFrame:
    """Load and combine all CSV exports from data/raw/.

    NOTE: ENTSO-E's CSV export column names have varied across platform
    versions. This function tries common variants; if your export uses
    different column names, check the first few rows it prints and adjust
    the COLUMN_MAP below.
    """
    csv_files = sorted(glob.glob(str(RAW_DIR / "*.csv")))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DIR}. "
            "See docs/data_access.md for export instructions."
        )

    frames = []
    all_columns_seen = set()
    for f in csv_files:
        df = pd.read_csv(f, encoding="utf-8-sig")  # utf-8-sig strips BOM automatically
        df = _normalize_columns(df)
        frames.append(df)
        all_columns_seen.add(tuple(df.columns))
        print(f"Loaded {f}: {len(df)} rows, columns: {list(df.columns)}")

    if len(all_columns_seen) > 1:
        print(
            f"\nWarning: not all files have identical columns after normalization. "
            f"Distinct column sets found: {all_columns_seen}\n"
            f"This usually means one export used a different platform version or "
            f"language setting. Inspect the file(s) with mismatched columns directly.\n"
        )

    combined = pd.concat(frames, ignore_index=True)
    print(f"\nCombined columns after concat: {list(combined.columns)}\n")

    # Common ENTSO-E export column names — adjust if your export differs.
    # Confirmed format as of June 2026 GUI export:
    # "MTU (CET/CEST)","Area","Actual Total Load (MW)","Day-ahead Total Load Forecast (MW)"
    timestamp_col_candidates = ["MTU (CET/CEST)", "Time (CET/CEST)", "MTU", "timestamp", "DateTime"]
    load_col_candidates = [
        "Actual Total Load (MW)",
        "Actual Total Load [MW] - BZN|DE-LU",
        "Actual Total Load [MW]",
        "load_mw",
        "Actual Total Load",
    ]

    ts_col = next((c for c in timestamp_col_candidates if c in combined.columns), None)
    load_col = next((c for c in load_col_candidates if c in combined.columns), None)

    if ts_col is None or load_col is None:
        raise ValueError(
            f"Could not identify timestamp/load columns automatically.\n"
            f"Available columns: {list(combined.columns)}\n"
            f"Edit data_loader.py's column candidates to match your export."
        )

    combined = combined.rename(columns={ts_col: "timestamp", load_col: "load_mw"})
    combined = combined[["timestamp", "load_mw"]]

    # ENTSO-E timestamps are often a range like "01.01.2023 00:00 - 00:15";
    # take the start of the interval
    combined["timestamp"] = combined["timestamp"].astype(str).str.split(" - ").str[0]
    combined["timestamp"] = pd.to_datetime(combined["timestamp"], dayfirst=True, errors="coerce")

    # ENTSO-E uses "-" (or sometimes "n/e") as a placeholder for not-yet-published
    # actuals — typically the most recent several hours of "today", since actual
    # load is published with a delay. These are NOT random/erroneous gaps, so
    # report them explicitly rather than silently dropping via dropna(), which
    # would hide a real and predictable data characteristic.
    pre_numeric_missing = combined["load_mw"].isin(["-", "n/e", "N/A", ""]).sum()
    combined["load_mw"] = pd.to_numeric(combined["load_mw"], errors="coerce")

    n_total = len(combined)
    n_missing = combined["load_mw"].isna().sum()
    if n_missing > 0:
        pct = n_missing / n_total * 100
        print(
            f"Note: {n_missing}/{n_total} rows ({pct:.1f}%) have missing 'load_mw' "
            f"values (ENTSO-E uses '-' for not-yet-published actuals, typically the "
            f"most recent hours of data). These rows are dropped here — if you're "
            f"exporting 'today' repeatedly, prefer exporting full past days only, "
            f"since today's last several hours will always be incomplete."
        )

    combined = combined.dropna(subset=["timestamp", "load_mw"])
    combined = combined.sort_values("timestamp").drop_duplicates(subset=["timestamp"])
    combined = combined.set_index("timestamp")

    return combined


def load_from_api(start: str, end: str) -> pd.DataFrame:
    """Load data from the live ENTSO-E API. Requires ENTSOE_API_KEY in .env."""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ENTSOE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ENTSOE_API_KEY not found. Copy .env.example to .env and add your key. "
            "See docs/data_access.md for how to get one."
        )

    from entsoe import EntsoePandasClient

    client = EntsoePandasClient(api_key=api_key)
    start_ts = pd.Timestamp(start, tz="Europe/Berlin")
    end_ts = pd.Timestamp(end, tz="Europe/Berlin")

    print(f"Fetching DE load data from {start} to {end}...")
    series = client.query_load(country_code="DE_LU", start=start_ts, end=end_ts)

    df = series.to_frame(name="load_mw")
    df.index.name = "timestamp"
    print(df)
    return df


def save_processed(df: pd.DataFrame):
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH)
    print(f"Saved {len(df)} rows to {PROCESSED_PATH}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["csv", "api"], required=True)
    parser.add_argument("--start", default="2023-01-01", help="API only: start date")
    parser.add_argument("--end", default="2024-12-31", help="API only: end date")
    args = parser.parse_args()

    if args.source == "csv":
        df = load_from_csv()
    else:
        df = load_from_api(args.start, args.end)

    save_processed(df)


if __name__ == "__main__":
    main()
