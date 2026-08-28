# Quant Projects

A collection of quantitative analysis, simulation, and factor-modeling
projects. Each folder is a self-contained Jupyter notebook with its own
README and sample output (`sample-output(s)/`).

| Project | Topic | Key Method |
|---|---|---|
| [`us-historical-scenario-simulation/`](us-historical-scenario-simulation/) | Historical-analogue scenario simulation for price projection | Monte Carlo, Historical Backcast, Ridge Factor Regression |
| [`multi-model-asset-pricing-engine/`](multi-model-asset-pricing-engine/) | Unified pipeline running 9 asset pricing models + portfolio optimization | CAPM, FF5, APT, DDM, Kalman Filter, GARCH, CCAPM |
| [`kr-us-adr-arbitrage-opp/`](kr-us-adr-arbitrage-opp/) | Cross-listed arbitrage analysis between Korean ADRs and KRX | Ornstein-Uhlenbeck Mean Reversion, Kelly Sizing |

## Note on execution order

`kr-us-adr-arbitrage-opp/` is designed to build on outputs from
`multi-model-asset-pricing-engine/` (Cells 00–03: risk-free rate, analysis
window, etc.). It can also run standalone (reasonable fallback defaults are
applied automatically), but running the main engine first is recommended
for full accuracy.

## Common Prerequisites

| Credential | Notes |
|---|---|
| FRED API Key | Free at https://fred.stlouisfed.org/docs/api/api_key.html |
| WRDS Access | Required for some optional sections; core functionality works without it |

See each project's `requirements.txt` for dependencies.

## ⚠️ Disclaimer

All outputs in this folder are provided for academic and portfolio purposes
only and do not constitute investment advice. See the
[top-level README](../README.md) for details.
