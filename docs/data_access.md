# Data Access

## Option 1: CSV export (no API key — use this to start immediately)

1. Go to the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
2. Navigate to: **Load → Total Load - Day Ahead / Actual**
3. Select:
   - Country: **Germany (DE) — or a specific German bidding zone (DE-LU)**
   - Date range: as much history as available (aim for at least 2 full years
     to capture yearly seasonality; the platform typically allows export in
     monthly chunks, so this may take several exports)
4. Export as CSV, save into `data/raw/` in this repo
   (e.g. `data/raw/load_DE_2023.csv`, `data/raw/load_DE_2024.csv`, ...)
5. Run `python src/data_loader.py --source csv` to combine and clean

## Option 2: Live API (requires free key — set up in parallel, switch over later)

1. Register an account at https://transparency.entsoe.eu/
2. Once registered and logged in, send an email to **transparency@entsoe.eu**
   with subject line **"Restful API access"**, stating your registered email
   address in the body
3. Wait for approval (timeline varies — register early, don't block on this)
4. Once approved, find your API key under your account's
   **"Web API Security Token"**
5. Copy `.env.example` to `.env` and add your key:
   ```
   ENTSOE_API_KEY=your-key-here
   ```
6. Run `python src/data_loader.py --source api --start 2023-01-01 --end 2024-12-31`

