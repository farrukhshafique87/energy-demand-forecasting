# Evaluation Methodology

## Why naive train/test splitting (e.g. random k-fold) is wrong here

Standard k-fold cross-validation randomly shuffles data into folds. For
time-series data, this leaks future information into the training set (the
model can "see" patterns from timestamps after the ones it's being tested
on), which inflates apparent performance in a way that won't hold up on
genuinely new, future data. This is one of the most common mistakes in
time-series ML projects, and is worth being able to explain clearly: the
correct approach is a **chronological split** — train on the past, test on a
later, held-out period the model never saw, with no shuffling.

This project uses a single chronological 80/20 split (train on the earlier
80% of the timeline, test on the most recent 20%). A more rigorous
production setup would use **rolling-origin / walk-forward validation**
(multiple chronological splits, sliding forward through time) — noted here
as a deliberate scope decision for a portfolio project, not an oversight.

## Metrics used

- **MAE (Mean Absolute Error)** — average absolute error in MW. Easy to
  interpret directly ("the model is off by X MW on average").
- **RMSE (Root Mean Squared Error)** — penalizes large errors more than MAE;
  useful because large demand-forecast errors are operationally more costly
  than small ones (grid balancing risk).
- **MAPE (Mean Absolute Percentage Error)** — error as a percentage, useful
  for comparing across different demand levels (e.g. weekday vs weekend).
- **Skill score vs. naive baseline** — `1 - (model_MAE / naive_MAE)`. This is
  the metric that actually matters: a skill score of 0 means the model adds
  no value over the naive seasonal baseline; negative means it's worse.
  Reporting this number honestly, even if it's unflattering for one of the
  models, is the entire point of including a baseline at all.

## What "good" looks like here

For German electricity demand, the seasonal naive baseline is already a
strong predictor (demand patterns repeat weekly with high consistency). A
realistic, honest outcome is that the ML/statistical models beat the naive
baseline by a modest margin (e.g. 10-30% improvement), not by some
dramatically larger number — and if a result looks too good, the right
instinct is to check for a leakage bug (see features.py's lag/rolling
shifting logic) before believing it.
