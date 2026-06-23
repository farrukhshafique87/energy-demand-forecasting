# Progress Log

## Week 1

**Goal:** Get data flowing (CSV path), build feature pipeline, get all three
models running end-to-end on a small slice to validate the pipeline works
before running on full data.

**Done:**
- ✅ ENTSO-E account registered, API access requested (in progress, async)
- ✅ CSV data exported from Transparency Platform UI for at least 3-6 months
- ✅ `data_loader.py` successfully combines and cleans CSV exports
- ✅ `features.py` builds the feature set without errors
- ✅ All three models (naive, SARIMA, XGBoost) run on a small slice
- ✅ `eval/run_comparison.py` produces a comparison table


## Week 2

**Goal:** Switch to live API once key arrives (if it has), run on full
history, sanity-check results, write up findings.

**Done:**
- [ ] API key received and `.env` configured
- [ ] Full historical data pulled (aim for 2+ years)
- [ ] Comparison re-run on full data
- [ ] Feature importance inspected
