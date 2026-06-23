"""
baseline.py — the naive (seasonal) baseline forecast.

This is arguably the most important file in the project. Any "real" model
that can't clearly beat this isn't adding value — and reporting that
comparison honestly, even when it's unflattering, is what makes a forecasting
project credible rather than inflated.

The seasonal naive method: predict that demand at time T equals demand at
time T minus one week. This captures weekly seasonality (weekday vs weekend
patterns) for free, with zero modeling effort — which is exactly why it's
a meaningful bar to clear.
"""

import pandas as pd

STEPS_PER_WEEK = 96 * 7  # 15-min resolution: 96 steps/day * 7 days


def seasonal_naive_forecast(series: pd.Series, horizon_steps: int) -> pd.Series:
    """For each point being forecast, predict the value from exactly one
    week prior. `series` should be the full historical series; returns
    predictions aligned to the same index for the last `horizon_steps`."""
    shifted = series.shift(STEPS_PER_WEEK)
    return shifted.iloc[-horizon_steps:]


def naive_forecast_1step(series: pd.Series, horizon_steps: int) -> pd.Series:
    """Simpler baseline: predict the most recent observed value persists.
    Included alongside the seasonal naive for comparison — seasonal naive
    should win decisively given daily/weekly demand patterns; if it doesn't,
    that's a useful (and reportable) finding about the data itself."""
    shifted = series.shift(1)
    return shifted.iloc[-horizon_steps:]
