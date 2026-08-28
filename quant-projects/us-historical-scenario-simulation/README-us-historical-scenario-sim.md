# US Historical Scenario Simulation

## Overview

This model treats past market shocks (oil shocks, the dot-com bust, the
Global Financial Crisis, COVID, etc.) as "historical analogues," reconstructs
the current macro regime as a weighted blend of these episodes, and uses
Monte Carlo simulation to project a distribution of future prices.

## Methodology

1. **Scenario library** — 10 historical regimes (1973 Oil Shock, 1990 Gulf
   War, 2000 Dot-Com Bust, 2008 GFC, 2020 COVID Crash, 2022 Rate Shock, 2025
   Tariff/Trade War, a Soft Landing base case, etc.), each defined by
   phase-specific drift/volatility parameters
2. **Macro weighting** — measures the distance between the current state of
   18 macro proxies (oil, VIX, rates, etc.) and each historical analogue to
   derive blend weights
3. **Blended fan charts** — simulates Monte Carlo paths across the weighted
   blend of scenarios, producing 50/70/90% confidence-interval fan charts
4. **Factor-regression projection** (Cell 09) — uses each ticker's actual
   factor sensitivities (via Ridge regression on the 18 proxies) so that the
   same scenario produces different projections for different tickers
5. **Backcast** (Cell 08B) — rolls the model backward to ask what target
   price it would have implied at a past date (note: this is a backcast, not
   an out-of-sample forecast)

## Sample Outputs

Files in `sample-outputs/`:

- **`explore_NVDA_all_scenarios.png`** — a grid of all 10 scenarios applied
  to NVDA, showing median outcomes ranging from -37% (Nixon/Watergate Bear)
  to +77% (COVID-Crash analogue)
- **`factor_TSM_projection.png`** — factor-regression-based projection for
  TSM (Taiwan Semiconductor)
- **`sim_all_nations_master.csv`** — scenario-blend statistics
  (p5/p25/median/p75/p95, beta, etc.) across the full US/Korea/Japan/China/
  global ticker universe

## ⚠️ Model Limitation

In `factor_TSM_projection.png`, the blended projection comes out to
**+1524.8%** relative to the current price. This is not a bug — it
illustrates a structural limitation of **linear factor-regression
projection**. For a stock like TSM with heavy tech-factor loading, applying
a historical proxy move over a multi-year horizon can compound to
unrealistic levels. This is a limitation specific to Cell 09's
factor-regression approach, in contrast to the bounded historical-analogue
approach used in Cell 07.

## Prerequisites

| Credential | Notes |
|---|---|
| FRED API Key | Free at https://fred.stlouisfed.org/docs/api/api_key.html; set as `FRED_API_KEY` env variable |
| WRDS Access | Optional (used for fundamental context; the simulation itself runs without it) |

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook us_historical_scenario_simulation.ipynb
```

## ⚠️ Disclaimer

This project is provided for academic and portfolio purposes only and does
not constitute investment advice. Simulated target prices and scenarios are
based on data and assumptions specific to a point in time and should not be
used for actual investment decisions.

---
*© 2026 Suna Kim. Shared publicly to demonstrate applied finance/coding skills
as part of a professional portfolio.*
