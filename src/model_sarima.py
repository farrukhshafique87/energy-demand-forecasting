"""
model_sarima.py — statistical time-series model (SARIMA) for demand forecasting.

SARIMA = Seasonal AutoRegressive Integrated Moving Average. Chosen over plain
ARIMA because electricity demand has strong, explicit daily and weekly
seasonality that SARIMA's seasonal terms are specifically designed to capture.

Note on compute cost: SARIMA on 15-minute-resolution data with a weekly
seasonal period (672 steps) is extremely expensive to fit. This module:
1. Resamples to hourly resolution (96 → 24 steps/day)
2. Uses only the most recent 90 days of training data — a deliberate and
   defensible choice: SARIMA is a short-term forecaster that captures local
   structure, not long-term trends. More data doesn't always help SARIMA;
   it mainly increases fitting cost and risks convergence failure.
   This is documented as an explicit design decision, not a limitation.
"""

import warnings
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

SEASONAL_PERIOD = 24       # hourly resolution, daily seasonality
TRAIN_WINDOW_DAYS = 90     # use only the most recent N days for fitting


def resample_hourly(series: pd.Series) -> pd.Series:
    return series.resample("h").mean()


def fit_sarima(train_series: pd.Series):
    """Fit SARIMA on hourly data. Convergence warnings are shown (not
    suppressed) — if you see them, it usually means the training window
    is still too large or the order parameters need tuning."""
    model = SARIMAX(
        train_series,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, SEASONAL_PERIOD),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fitted = model.fit(disp=False, maxiter=200)
        convergence_warnings = [w for w in caught if "convergence" in str(w.message).lower()]
        if convergence_warnings:
            print(
                f"  SARIMA convergence warning: model may not have converged fully. "
                f"Forecasts may be unreliable — consider reducing TRAIN_WINDOW_DAYS "
                f"or adjusting order parameters."
            )
        else:
            print(f"  SARIMA converged OK (AIC={fitted.aic:.1f})")
    return fitted


def forecast_sarima(train_series: pd.Series, horizon_steps: int) -> pd.Series:
    """Fit on the most recent TRAIN_WINDOW_DAYS of train_series (hourly),
    forecast horizon_steps ahead."""
    hourly = resample_hourly(train_series)

    # cap to most recent window — see module docstring for why
    window_hours = TRAIN_WINDOW_DAYS * 24
    if len(hourly) > window_hours:
        print(f"  Using most recent {TRAIN_WINDOW_DAYS} days ({window_hours} hourly "
              f"points) of {len(hourly)} available for SARIMA fitting.")
        hourly = hourly.iloc[-window_hours:]

    fitted = fit_sarima(hourly)
    forecast = fitted.forecast(steps=horizon_steps)
    return forecast


if __name__ == "__main__":
    from pathlib import Path
    processed_path = Path(__file__).parent.parent / "data" / "processed" / "load_germany.parquet"
    df = pd.read_parquet(processed_path)
    series = df["load_mw"]
    train = series.iloc[:int(len(series) * 0.8)]
    forecast = forecast_sarima(train, horizon_steps=24)
    print(forecast)
