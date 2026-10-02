# Market Analytics

Applied e-commerce market-intelligence tooling: data-collection pipelines for Amazon US
and Coupang, a news-based launch monitor, and a quantitative market-sizing toolkit that
turns marketplace sales rank into revenue estimates, growth rates and positioning maps.

The quant projects in this repository apply asset-pricing theory to financial markets.
This folder applies the same habits to consumer-product markets: model the unobservable
(sales) from an observable proxy (rank), report ranges instead of point estimates, and
test the sample's coverage before trusting the total.

> © 2026 Suna Kim. All Rights Reserved.
> Shared for portfolio and demonstration purposes only. No permission is granted to use,
> copy, modify, or distribute this code without explicit written consent from the author.

## Contents

| Folder | What it does | Key techniques |
|---|---|---|
| [`amazon-pipeline/`](amazon-pipeline/) | Search crawl → keyword merge → product-page collection → detail parsing → BSR sales estimate → merge by ASIN | Playwright collection with block detection, HTML parsing, ASIN-level de-duplication |
| [`coupang-pipeline/`](coupang-pipeline/) | Search-page extraction → keyword append → product-detail OCR + LLM attribute extraction → price-history filter | Page-source parsing, OCR, Gemini API structured extraction |
| [`news-monitoring/`](news-monitoring/) | New-product launch news → de-duplicated issues → brand / category / USP trend charts | TF-IDF cosine similarity, fuzzy matching, issue clustering |
| [`market-sizing/`](market-sizing/) | BSR → units → revenue market size; 60-month history and YoY growth; price × function positioning map | Power-law calibration, scenario ranges, rank-size tail extrapolation |
| [`sample-data/`](sample-data/) | Small **synthetic** files so every script and the rewritten notebooks run end-to-end | — |

## Pipeline at a glance

```
Amazon US                                   Coupang
01 search results ─┐                        01 search-page products ─┐
02 merge keywords ─┤                        02 keyword append ───────┤
03 product pages ──┤                        03 detail OCR + LLM ─────┤
04 parse details ──┤                        04 price-history filter ─┘
05 BSR → sales ────┤
06 merge by ASIN ──┴──► market-sizing/  ──► market size range · growth · positioning map
```

## Method notes (market sizing)

- **Rank → sales.** Units/day = A · BSR^b, calibrated per category from anchor points you
  supply (e.g. Amazon's "N+ bought in past month" badges paired with each product's BSR).
  Two scenarios: an upper least-squares fit and a conservative fit that flattens the slope
  above the best-selling anchor, where extrapolation error is largest.
- **Coverage.** Sales are highly concentrated, so the first few search pages capture most
  revenue. `tail_uplift` fits the sample's rank-revenue curve and reports how much an
  unsampled tail would add (typically a few percent for concentrated categories).
- **Review share ≠ revenue share.** Cumulative reviews reward older listings; rank-based
  revenue reflects current sales. Comparing the two flags rising versus declining brands.

## Disclaimer

This code is shared to show **methods**: how the pipelines are structured, how pages are
parsed, and how sales rank is turned into market-size estimates. It is not a ready-to-run
scraping tool.

- **Portfolio and educational use only.** It is not a commercial product and gives no
  business, financial or legal advice. See the copyright notice above for reuse terms.
- **Notebooks that contact live websites.** The notebooks below send automated requests
  to sites that are not affiliated with this repository. Each has a ⚠️ warning cell at the top.

  | Notebook | Contacts |
  |---|---|
  | `amazon-pipeline/01` | aiprice.com (price history) |
  | `amazon-pipeline/03` | amazon.com product pages (Playwright) |
  | `amazon-pipeline/05` | LumaiScope public BSR-estimate API |
  | `coupang-pipeline/01` | aiprice.com (price history) |
  | `coupang-pipeline/03` | Coupang product-detail images |

  These sites' terms of service may prohibit or limit automated access. **Do not run these
  notebooks against a live site without that site's permission.** If you do run any of them,
  you are responsible for complying with the site's terms, robots rules, rate limits and
  applicable law. Keep request rates low and do not redistribute what you collect.
- **No data, keys or third-party tables included.** No collected data, API keys or
  calibration tables from paid tools are in this repository. `sample-data/` is synthetic,
  so every downstream step can be followed without contacting any site.
- **No affiliation.** Amazon, Coupang, aiprice, LumaiScope, Keepa, Jungle Scout and Helium 10
  are named only to describe what the code does. This project is not affiliated with or
  endorsed by any of them, and all trademarks belong to their owners.
- **Estimates, not facts.** Rank-based sales estimates carry wide error, especially at the top
  ranks. Treat every number as a range and check it against a direct sales signal.
- **No warranty.** The code is provided "as is". Sites change their pages often, so the
  collectors may stop working at any time.

## Stack

Python · pandas · numpy · matplotlib · seaborn · scikit-learn · rapidfuzz · BeautifulSoup ·
Playwright · requests · Keepa / Jungle Scout APIs (optional) · Gemini API (optional) · Google Colab
