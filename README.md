# German Electricity Demand Forecasting

A time-series forecasting project predicting short-term electricity demand
(load) in Germany, using public ENTSO-E grid data. Built to demonstrate
rigorous forecasting methodology — not just "a model," but an honest,
baseline-compared evaluation of multiple approaches.

## Why this problem

Germany's ongoing energy transition (*Energiewende*) toward renewables makes
electricity demand forecasting an active, real-world problem: unlike solar
and wind generation, demand is the side of the grid-balancing equation that's
*more predictable* — driven by quantifiable factors (time of day, day of
week, season, temperature, holidays) — which makes it a genuinely tractable
forecasting problem, in contrast to something like stock price prediction
where the signal-to-noise ratio is far worse.

Grid operators (TSOs) and energy traders forecast demand daily as a core
operational function. This project is a small-scale, educational version of
that real task.

## Methodology — comparing approaches honestly

This project deliberately implements **three** forecasting approaches and
compares them on equal footing, rather than presenting a single model's
result in isolation:

1. **Naive baseline** — "tomorrow looks like the same time last week"
   (seasonal naive). This is the single most important model in the project:
   any "real" model that doesn't clearly beat this isn't adding value, and
   reporting this comparison honestly is what separates a rigorous forecasting
   project from an inflated one.
2. **Statistical time-series model** (SARIMA or Prophet) — captures trend and
   seasonality explicitly, interpretable, the industry-standard classical
   approach for this kind of data.
3. **Classical ML model** (XGBoost or Random Forest on engineered features) —
   captures non-linear interactions between calendar features, lagged demand,
   and (optionally) weather, generally the stronger performer when enough
   features are available.

All three are evaluated on the same held-out time period using the same
metrics. See [docs/evaluation.md](docs/evaluation.md) for the full
methodology and why naive train/test splitting is wrong for time-series data.

## Data source

[ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) — the
official, mandated EU electricity market data platform. Specifically: actual
total load (demand) for Germany, at 15-minute resolution.

Two ingestion paths are supported (see `src/data_loader.py`):
- **CSV export** (no API key needed) — manually exported from the platform UI,
  used to get started immediately
- **Live API** (via the `entsoe-py` library, requires a free API key — see
  [docs/data_access.md](docs/data_access.md) for registration steps) — used
  once the key is approved, for reproducible/automatable data refresh

## Project status

🚧 In progress — see [docs/progress-log.md](docs/progress-log.md)

## Disclaimer

This is an educational forecasting project. It is not used for, and is not
suitable for, real grid operations or trading decisions — actual TSO
forecasting systems incorporate far more data sources, redundancy, and
operational safeguards than a portfolio project reasonably can.
