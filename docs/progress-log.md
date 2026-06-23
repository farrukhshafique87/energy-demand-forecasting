# Progress Log

## Week 1 — [DATE]

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

**Decisions:**
- (fill in: how much history did you get, any column-name surprises in the
  CSV export, any model fitting issues)

**Blockers / open questions:**
- (fill in)

---

## Week 2 — [DATE]

**Goal:** Switch to live API once key arrives (if it has), run on full
history, sanity-check results, write up findings.

**Done:**
- [ ] API key received and `.env` configured
- [ ] Full historical data pulled (aim for 2+ years)
- [ ] Comparison re-run on full data
- [ ] Feature importance inspected — does it make intuitive sense?
- [ ] Results written up in plain language (for CV/interview talking points)

---

## Template for future weeks

```
## Week N — [DATE]

**Goal:**

**Done:**
- [ ]

**Decisions:**

**Blockers / open questions:**
```
