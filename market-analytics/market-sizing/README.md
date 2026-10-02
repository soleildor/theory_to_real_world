# Market Sizing

Turns marketplace sales rank into an annual market-size range, a growth history and a
positioning map.

| File | What it does |
|---|---|
| `bsr_market_size.py` | Calibrates units/day = A · BSR^b from your anchor points; estimates annual revenue per market (conservative / upper / central); concentration (top-1, top-10 share); review share vs revenue share; long-tail uplift |
| `collect_bsr_history.py` | Pulls up to 60 months of rank history (Keepa) or estimated units (Jungle Scout API) per ASIN; monthly revenue by brand and market; YoY and 6-month growth. Runs as a script or pasted into a Colab cell |
| `positioning_map.py` | One panel per market: unit-price index × functional depth, bubble area = revenue, colour = rising vs established |

## Quick start (synthetic data)

```bash
python bsr_market_size.py --products ../sample-data/products_sample.csv \
                          --anchors  ../sample-data/anchors_sample.csv \
                          --out ../sample-data/market_size_sample.xlsx
python positioning_map.py --products ../sample-data/market_size_sample.xlsx
```

The sample output (`../sample-data/positioning_map_sample.png`) is built from synthetic
brands and made-up anchors. It shows the format, not any real market.

## Anchors: the one input you must supply

`anchors.csv` has columns `bsr_category, bsr, units_per_day`. Good sources:

1. **"N+ bought in past month"** badges on products you already collected (badge lower
   bound ÷ 30), paired with each product's BSR — free and specific to your category.
2. Your own sales data for listings you operate.
3. Estimates exported from a tool you subscribe to.

Third-party BSR conversion tables are not included; check their terms before using one.

## Reading the output

- Report the **range** (conservative to upper). Most of the gap comes from the top few
  ranks, where extrapolation beyond the best-selling anchor is least reliable.
- `tail_uplift_to_1000` shows how much revenue an unsampled tail of up to 1,000 products
  would add if it followed the sample's rank-revenue curve. In concentrated categories it is
  a few percent, which is why the first few search pages are a reasonable proxy for the market.
- Rank is relative: if the whole category grows, a product's rank can stay flat while its
  sales rise. Rank history measures share shifts; pair it with category-level demand data
  for absolute growth.
