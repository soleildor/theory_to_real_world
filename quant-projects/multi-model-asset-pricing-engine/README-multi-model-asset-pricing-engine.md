# Multi-Model Asset Pricing Engine

## Overview

Rather than relying on a single asset pricing model, this pipeline applies
**nine distinct theoretical frameworks in parallel to the same ticker
universe** to compare expected returns and target prices. Agreement or
disagreement across models is interpreted as a measure of signal
robustness.

## Models Implemented

| # | Model | Frequency |
|---|---|---|
| 1 | CAPM | Daily + Monthly |
| 2 | Fama-French 5-Factor (FF5) | Daily + Monthly |
| 3 | Arbitrage Pricing Theory (APT) | Daily + Monthly |
| 4 | Dividend Discount Model (Gordon Growth) | Monthly |
| 5 | Ornstein-Uhlenbeck Mean Reversion | Daily + Monthly |
| 6 | Kalman Filter CAPM (time-varying beta) | Daily + Monthly |
| 7 | GARCH(1,1) | Daily + Monthly |
| 8 | Consumption CAPM (CCAPM) | Monthly |
| 9 | EV/EBITDA + P/E fundamental valuation | — |

Also included: **Bayesian shrinkage (James-Stein betas)**, **NBER-window
comparisons**, and **regime-separated estimation** options, culminating in a
**conviction score and budget-constrained portfolio optimizer (Kelly
sizing)**.

## Sample Outputs

`sample-outputs/AAPL/` contains an example ticker-level output (the full CSV
set is generated locally on each run; only one representative ticker is
included here to keep the repo lightweight):

- Per-model expected return / target price files (`pricing_capmxdaily.csv`,
  `pricing_ff5xdaily.csv`, etc.)
- `pricing_all_models.csv` — a consolidated summary across all models

Regime-segmented variants (`_current_regi`, `_nber_clean`, `_nber_current`,
`_nber_full`) are omitted for brevity — reproducible by running Cells 05b /
06b.

**Outputs derived from WRDS (`ev_ebitda`, `pe`) are excluded** due to
data-license restrictions. If you have WRDS access, run Cell 14 directly to
reproduce them.

## Prerequisites

| Credential | Notes |
|---|---|
| FRED API Key | Free at https://fred.stlouisfed.org/docs/api/api_key.html; set as `FRED_API_KEY` env variable |
| WRDS Access | Institutional subscription required (used only in Cell 14, EV/EBITDA & P/E valuation). Credentials are entered via `getpass` at runtime |

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook us_multi_model_asset_pricing_engine.ipynb
```

Google Drive mounting is only attempted in a Colab environment; running
locally automatically falls back to a `./investment_us_output` folder.

## ⚠️ Disclaimer

This project is provided for academic and portfolio purposes only and does
not constitute investment advice. The holdings used in `MY_PORTFOLIO` are
illustrative dummy values (AAPL, MSFT), not real positions. Target prices
and conviction scores produced by the models should not be used for actual
investment decisions.

---
*© 2026 Suna Kim. Shared publicly to demonstrate applied finance/coding skills
as part of a professional portfolio.*
