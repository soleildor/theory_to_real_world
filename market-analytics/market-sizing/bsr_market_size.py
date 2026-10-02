"""
BSR-based market sizing
=======================

Turns a product list with Amazon Best Sellers Rank (BSR) and price into an estimated
annual market size, reported as a range rather than a single number.

Method
------
1. Calibrate a power law  units/day = A * BSR^b  per category from anchor points
   (BSR, units/day). Anchors are supplied by you - see `ANCHORS` below.
2. Two scenarios:
     upper        - least-squares fit through all anchors
     conservative - above the best-selling anchor, extrapolate with the flatter slope of
                    the first two anchors (top-rank extrapolation is where error is
                    largest); below it, same as upper
   The central estimate is the geometric mean of the two.
3. Revenue = units/day * 30 * price, summed per market, * 12.
4. Variants that share one listing (same brand + same BSR) are counted once.
5. Optional long-tail check: fit the rank-revenue curve of the sample and extrapolate
   to N products to see how much the unsampled tail would add.

Where anchors come from
-----------------------
Do not copy a third-party BSR table into this file. Good sources of anchors:
  * Amazon's "N+ bought in past month" badge on products you have already collected
    (monthly units lower bound -> divide by 30), paired with each product's BSR
  * your own sales data for listings you operate
  * estimates exported from a tool you subscribe to (Keepa, Helium 10, Jungle Scout)
At least two anchors per category; three or more spread across ranks is better.

Usage
-----
    python bsr_market_size.py --products ../sample-data/products_sample.csv \
                              --anchors  ../sample-data/anchors_sample.csv
"""
import argparse
import math

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Curve
# ---------------------------------------------------------------------------
def fit_curve(anchors):
    """anchors: list of (bsr, units_per_day), sorted or not. Returns curve params."""
    pts = sorted(anchors)
    if len(pts) < 2:
        raise ValueError("need at least two anchors per category")
    x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts])
    slope, icpt = np.polyfit(x, y, 1)
    top = (y[1] - y[0]) / (x[1] - x[0])
    return dict(a=icpt, b=slope, top=top, x0=x[0], y0=y[0])


def units_per_day(bsr, curve, scenario="mid"):
    if bsr is None or not np.isfinite(bsr) or bsr <= 0:
        return np.nan
    lx = math.log(bsr)
    upper = math.exp(curve["a"] + curve["b"] * lx)
    cons = math.exp(curve["y0"] + curve["top"] * (lx - curve["x0"])) if lx < curve["x0"] else upper
    return {"upper": upper, "conservative": cons, "mid": math.sqrt(upper * cons)}[scenario]


def load_anchors(path):
    a = pd.read_csv(path)        # columns: bsr_category, bsr, units_per_day
    return {cat: fit_curve(list(zip(g.bsr, g.units_per_day))) for cat, g in a.groupby("bsr_category")}


# ---------------------------------------------------------------------------
# Market size
# ---------------------------------------------------------------------------
def estimate(products, curves):
    """products: columns market, brand, bsr, bsr_category, price (+ optional reviews)."""
    p = products.dropna(subset=["bsr", "price"]).copy()
    p = p[p.bsr_category.isin(curves)]
    p = p.sort_values("bsr").drop_duplicates(["brand", "bsr"])          # shared listings once
    for s in ("conservative", "upper", "mid"):
        p[f"units_mo_{s}"] = [units_per_day(b, curves[c], s) * 30 for b, c in zip(p.bsr, p.bsr_category)]
        p[f"rev_yr_{s}"] = p[f"units_mo_{s}"] * p.price * 12
    return p


def market_table(p):
    t = p.groupby("market").agg(products=("bsr", "size"),
                                rev_conservative=("rev_yr_conservative", "sum"),
                                rev_upper=("rev_yr_upper", "sum"),
                                rev_mid=("rev_yr_mid", "sum"))
    t["revenue_share_mid"] = t.rev_mid / t.rev_mid.sum()
    if "reviews" in p:
        r = p.groupby("market").reviews.sum()
        t["review_share"] = r / r.sum()
    top = p.sort_values("rev_yr_mid", ascending=False).groupby("market")
    t["top1_share"] = top.rev_yr_mid.apply(lambda s: s.iloc[0] / s.sum())
    t["top10_share"] = top.rev_yr_mid.apply(lambda s: s.head(10).sum() / s.sum())
    return t.sort_values("rev_mid", ascending=False)


def tail_uplift(p, n_total=1000):
    """Extra revenue (%) if each market had n_total products following the sample's rank curve."""
    out = {}
    for m, g in p.groupby("market"):
        rev = g.rev_yr_mid.sort_values(ascending=False).values
        n = len(rev)
        if n < 5:
            out[m] = np.nan; continue
        r = np.arange(1, n + 1); keep = r >= 3                          # skip the top-2 outliers
        s, i = np.polyfit(np.log(r[keep]), np.log(rev[keep]), 1)
        out[m] = (np.exp(i) * np.arange(n + 1, n_total + 1) ** s).sum() / rev.sum()
    return pd.Series(out, name=f"tail_uplift_to_{n_total}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--out", default="market_size.xlsx")
    a = ap.parse_args()

    curves = load_anchors(a.anchors)
    for c, f in curves.items():
        print(f"{c}: units/day = {math.exp(f['a']):,.0f} * BSR^{f['b']:.3f}  (top slope {f['top']:.3f})")
    p = estimate(pd.read_csv(a.products), curves)
    t = market_table(p).join(tail_uplift(p))
    fmt = t.copy()
    for c in ("rev_conservative", "rev_upper", "rev_mid"):
        fmt[c] = (fmt[c] / 1e6).map("${:,.1f}M".format)
    for c in [c for c in fmt if "share" in c or "uplift" in c]:
        fmt[c] = fmt[c].map("{:.0%}".format)
    print(fmt.to_string())
    with pd.ExcelWriter(a.out) as w:
        t.to_excel(w, sheet_name="market")
        p.to_excel(w, sheet_name="products", index=False)
    print("saved:", a.out)


if __name__ == "__main__":
    main()
