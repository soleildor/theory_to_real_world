# KR-US ADR Arbitrage Opportunity

## Overview

This project analyzes the price gap between KRX-listed (Korea Exchange)
stocks and their US-listed ADRs (American Depositary Receipts). KRX is
treated as the price-discovery market, with the ADR modeled as converging to
the KRX price with a lag.

Two investor perspectives are modeled separately:
- **KRX fundamental investor** (KRW terms)
- **USD investor** (KRX price + FX + arbitrage spread)

## Methodology

1. **Automatic ADR discovery** — given any KRX ticker, automatically detects
   whether it has a US listing and infers the ADR ratio via price inference
   (no hardcoding required)
2. **Korean fundamental model** — KR-CAPM (KOSPI benchmark, BOK risk-free
   rate), Korean FF5, Korean APT
3. **Premium/discount analysis** — fits an Ornstein-Uhlenbeck AR(1)
   mean-reversion model to estimate the ADR premium's equilibrium level and
   half-life. Korean market shock windows (2020 COVID, 2022 Legoland, 2024
   martial law) are masked as contamination periods
4. **USD investor model** —
   `E[r_total] = E[r_KRX_KRW] + FX_carry + arb_convergence + div_yield − ADR_fee`
5. **Conviction score + Kelly allocation** — position sizing based on signal
   strength (quarter-Kelly, capped at 30%)

## Sample Output

Files in `sample-output/`:

**Key outputs**
- `ke_adr_conviction.csv` — final buy/sell/hold signals per ticker with
  Kelly-sized conviction scores
- `ke_fanchart_SKM.png` — example fan chart: SK Telecom (SKM) historical ADR
  price + forward target-price projection
- `ke_compare_KB.png` — 4-panel comparison of KB Financial's ADR vs. KRX
  (normalized price, premium, rolling correlation, rolling volatility ratio)

**Supporting diagnostics**
- `ke_adr_discovery_results.csv` — auto-discovered KRX↔US listing pairs
- `ke_adr_ratio_audit.csv` — ADR ratio inference QA
- `ke_krx_fundamental_results.csv`, `ke_krx_full_summary.csv` — detailed
  Korean-side fundamental model output
- `ke_adr_premium_stats.csv`, `ke_adr_usd_valuation.csv` — intermediate
  premium/valuation calculations

## Prerequisites & Dependencies

This notebook is designed to build on outputs from
[`multi-model-asset-pricing-engine`](../multi-model-asset-pricing-engine/)
(Cells 00–03: risk-free rate, analysis window, FRED client, etc.). It can
also run standalone (reasonable fallback defaults are applied
automatically without errors), but running the main engine first is
recommended for full accuracy.

| Credential | Notes |
|---|---|
| FRED API Key | Free at https://fred.stlouisfed.org/docs/api/api_key.html; set as `FRED_API_KEY` env variable |
| Google Drive | Used only in Colab; running locally automatically falls back to a local folder |

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook kr-us-adr-arbitrage-opportunity.ipynb
```

## ⚠️ Disclaimer

The outputs in this folder (buy/sell signals, target prices, conviction
scores) are the result of a model demo/backtest run on historical data as of
the stated `run_date`. They are **not current investment advice or trading
recommendations.** Signals have not been updated since that snapshot and
should not be used for actual investment decisions. This project is provided
for academic and portfolio purposes only.

---
*© 2026 Suna Kim. Shared publicly to demonstrate applied finance/coding skills
as part of a professional portfolio.*
