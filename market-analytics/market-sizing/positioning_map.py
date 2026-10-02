"""
Positioning map: price x functional depth
=========================================

One panel per market, one bubble per brand.

  x  unit-price index  = brand's revenue-weighted unit price / market median unit price (log)
  y  functional depth  = revenue-weighted score from ingredient / material keywords
                          0 plain patch, 1 one common active, 2 several or a premium active,
                          3 advanced tech (microneedle, PDRN ...)
  bubble area  = estimated annual revenue (rev_yr_mid from bsr_market_size.py)
  colour       = rising (revenue share > review share) vs established / declining

Keyword lists are examples for skin-care patches - edit them for your category.

Usage
-----
    python positioning_map.py --products market_size.xlsx --out positioning_map.png
"""
import argparse
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ADVANCED = r"microneedle|micro-needle|pdrn|salmon dna|exosome"
PREMIUM = r"niacinamide|peptide|retin|glutathione|bakuchiol|adenosine"
COMMON = (r"salicylic|\bbha\b|tea.?tree|hyaluron|caffeine|collagen|centella|cica|aloe|"
          r"vitamin c|zinc|benzoyl|green tea|cucumber|\bgold\b|citronella|calendula")

ACCENT, MUTED, INK, SUB, BG = "#c2572b", "#9aa7b4", "#1f2937", "#6b6259", "#faf6f1"


def function_score(text):
    t = str(text).lower()
    if re.search(ADVANCED, t):
        return 3
    premium = len(set(re.findall(PREMIUM, t)))
    common = len(set(re.findall(COMMON, t)))
    if premium >= 1 or common >= 3:
        return 2
    return 1 if common >= 1 else 0


def brand_table(p, top=18):
    p = p.copy()
    p["fs"] = p["text"].map(function_score)
    rows = []
    for market, g in p.groupby("market"):
        med = g.unit_price.median()
        rev_tot = g.rev_yr_mid.sum()
        rv_tot = g.reviews.sum() if "reviews" in g else np.nan
        for brand, b in g.groupby("brand"):
            w = b.rev_yr_mid.clip(lower=1e-9)
            rows.append(dict(market=market, brand=brand, rev=b.rev_yr_mid.sum(),
                             price_index=np.average(b.unit_price / med, weights=w),
                             depth=np.average(b.fs, weights=w),
                             rising=(b.rev_yr_mid.sum() / rev_tot) > (b.reviews.sum() / rv_tot)
                             if "reviews" in b else False))
    t = pd.DataFrame(rows)
    return t.sort_values("rev", ascending=False).groupby("market").head(top)


def plot(t, out, label_top=8):
    markets = list(t.groupby("market").rev.sum().sort_values(ascending=False).index)
    fig, axes = plt.subplots(1, len(markets), figsize=(8 * len(markets), 7.6), facecolor=BG, squeeze=False)
    rng = np.random.default_rng(3)
    for ax, m in zip(axes[0], markets):
        d = t[t.market == m].copy()
        d["y"] = d.depth + rng.uniform(-0.12, 0.12, len(d))          # small jitter so ties don't overlap
        size = d.rev / d.rev.max() * 3000 + 60                        # area proportional to revenue
        ax.set_facecolor(BG)
        ax.axvline(1, color="#cfc6ba", lw=1, zorder=0); ax.axhline(1.5, color="#cfc6ba", lw=1, zorder=0)
        ax.scatter(d.price_index, d.y, s=size, c=[ACCENT if r else MUTED for r in d.rising],
                   alpha=0.85, edgecolors=BG, linewidths=2, zorder=2)
        for _, r in d.head(label_top).iterrows():
            ax.annotate(r.brand, (r.price_index, r.y), xytext=(0, 14), textcoords="offset points",
                        ha="center", fontsize=10, color=INK)
        ax.set_xscale("log"); ax.set_xlim(0.1, 14); ax.set_ylim(-0.6, 3.6); ax.minorticks_off()
        ax.set_xticks([0.25, 0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0.25x", "0.5x", "1x median", "2x", "4x", "8x"], color=SUB)
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(["0 Plain", "1 One common active", "2 Multi / premium active", "3 Advanced tech"], color=SUB)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0)
        ax.set_xlabel("Unit-price index (vs market median, log)", color=SUB)
        ax.set_title(m, loc="left", fontsize=16, fontweight="bold", color=INK, pad=12)
    fig.suptitle("Positioning map: price x functional depth", x=0.05, ha="left",
                 fontsize=20, fontweight="bold", color=INK)
    fig.legend(handles=[Line2D([], [], marker="o", ls="", ms=11, mfc=ACCENT, mec=BG, label="Rising: revenue share > review share"),
                        Line2D([], [], marker="o", ls="", ms=11, mfc=MUTED, mec=BG, label="Established / declining")],
               loc="upper left", bbox_to_anchor=(0.045, 0.935), ncol=2, frameon=False, labelcolor=SUB)
    plt.subplots_adjust(left=0.11, right=0.98, top=0.80, bottom=0.1, wspace=0.42)
    plt.savefig(out, dpi=130, facecolor=BG)
    print("saved:", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", required=True, help="market_size.xlsx from bsr_market_size.py")
    ap.add_argument("--out", default="positioning_map.png")
    a = ap.parse_args()
    p = pd.read_excel(a.products, sheet_name="products")
    plot(brand_table(p), a.out)


if __name__ == "__main__":
    main()
