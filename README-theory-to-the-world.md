# theory_to_real_world

A collection of applied finance projects built while studying for a PhD
program and CFA/investment-management coursework, translating theoretical
models into code run on real market data. This repository serves as a
career portfolio targeting research analyst and quantitative analysis roles.

## Repository Structure

| Folder | Contents |
|---|---|
| [`research/`](research/) | Sell-side-style equity research reports (investment thesis, valuation, risk factors) |
| [`quant-projects/`](quant-projects/) | Quantitative analysis, simulation, and factor-modeling code projects (Python/Jupyter) |
| `shared/` | Utilities shared across projects (currently empty) |

## Quant Projects Index

| Project | Topic | Key Method |
|---|---|---|
| [Historical Scenario Simulation](quant-projects/us-historical-scenario-simulation/) | Historical-analogue scenario simulation for price projection | Monte Carlo, Historical Backcast, Ridge Factor Regression |
| [Multi-Model Asset Pricing Engine](quant-projects/multi-model-asset-pricing-engine/) | Unified pipeline running 9 asset pricing models | CAPM, FF5, APT, DDM, Kalman Filter, GARCH, CCAPM |
| [KR-US ADR Arbitrage Opportunity](quant-projects/kr-us-adr-arbitrage-opp/) | Cross-listed arbitrage analysis between Korean ADRs and KRX | Ornstein-Uhlenbeck Mean Reversion, Kelly Sizing |

Each project folder contains its own README with theoretical background,
methodology, instructions to run, and sample output.

## ⚠️ General Disclaimer

All code and outputs in this repository (target prices, buy/sell signals,
conviction scores, etc.) are provided **for academic and educational
purposes and as a career-portfolio demonstration only**. Nothing here
constitutes investment advice or a recommendation to buy or sell any
security. Outputs reflect a snapshot of a specific point in time and data
and may not have been updated since.

## Stack

Python · pandas · numpy · scikit-learn · statsmodels · yfinance · FRED API ·
matplotlib · Jupyter

---
*© 2026 Suna Kim. Shared publicly to demonstrate applied finance/coding
skills as part of a professional portfolio.*
