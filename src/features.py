"""
features.py — feature engineering for the ML model (XGBoost/Random Forest).

Note: the statistical model (SARIMA/Prophet) doesn't need these — it works
directly on the raw time series. These features are specifically for the
ML approach, which needs the time-series problem reframed as a supervised
regression problem (tabular X -> y).

Feature groups:
- Calendar features: hour, day-of-week, month, is_weekend, is_holiday
  (demand has strong, well-known patterns tied to all of these)
- Lag features: load N steps ago (captures short-term autocorrelation)
- Rolling statistics: rolling mean/std over recent windows (captures
  recent trend level, smooths noise)

IMPORTANT (the part most tutorials get wrong): lag and rolling features must
only use information that would have been available at prediction time. We
compute them with proper shifting to avoid leakage — using "future" data to
predict the past is the single most common bug in time-series ML projects,
and it inflates apparent accuracy invisibly. Worth stating explicitly in any
interview discussion of this project.
"""

import pandas as pd
import numpy as np

# German public holidays (fixed-date ones; for a real production system you'd
# use a library like `holidays`, included here as an optional enhancement)
LAG_STEPS = [1, 4, 96, 96 * 7]  # 15-min steps: 15min, 1hr, 1 day, 1 week ago
ROLLING_WINDOWS = [4, 96]        # 1hr, 1 day rolling windows


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek  # 0 = Monday
    df["month"] = df.index.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # cyclical encoding for hour and day_of_week — avoids the model thinking
    # hour 23 and hour 0 are "far apart" the way raw integers would suggest
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    return df


def add_holiday_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Optional: requires `pip install holidays`. Marks German public holidays,
    which typically show demand patterns similar to weekends."""
    df = df.copy()
    try:
        import holidays as holidays_lib
        de_holidays = holidays_lib.Germany(years=range(df.index.year.min(), df.index.year.max() + 1))
        df["is_holiday"] = df.index.normalize().isin(de_holidays).astype(int)
    except ImportError:
        print("`holidays` package not installed — skipping is_holiday feature. "
              "Run: pip install holidays")
        df["is_holiday"] = 0
    return df


def add_lag_features(df: pd.DataFrame, target_col: str = "load_mw") -> pd.DataFrame:
    df = df.copy()
    for lag in LAG_STEPS:
        df[f"lag_{lag}"] = df[target_col].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, target_col: str = "load_mw") -> pd.DataFrame:
    df = df.copy()
    for window in ROLLING_WINDOWS:
        # shift(1) before rolling ensures we never include the current,
        # to-be-predicted value in its own rolling window — this is the
        # leakage trap mentioned in the module docstring
        shifted = df[target_col].shift(1)
        df[f"rolling_mean_{window}"] = shifted.rolling(window).mean()
        df[f"rolling_std_{window}"] = shifted.rolling(window).std()
    return df


def build_feature_set(df: pd.DataFrame, target_col: str = "load_mw") -> pd.DataFrame:
    """Full feature pipeline. Returns a DataFrame ready for supervised ML,
    with rows containing NaN (from lag/rolling warm-up) dropped."""
    df = add_calendar_features(df)
    df = add_holiday_feature(df)
    df = add_lag_features(df, target_col)
    df = add_rolling_features(df, target_col)
    df = df.dropna()
    return df


if __name__ == "__main__":
    from pathlib import Path
    processed_path = Path(__file__).parent.parent / "data" / "processed" / "load_germany.parquet"
    df = pd.read_parquet(processed_path)
    featured = build_feature_set(df)
    print(f"Built feature set: {featured.shape[0]} rows, {featured.shape[1]} columns")
    print(f"Columns: {list(featured.columns)}")
    out_path = processed_path.parent / "features.parquet"
    featured.to_parquet(out_path)
    print(f"Saved to {out_path}")
