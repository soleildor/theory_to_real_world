"""
BSR / sales history collector -> monthly revenue and growth by brand and market
=============================================================================

Pulls up to 60 months of history per ASIN from Keepa (sales-rank history) or the
Jungle Scout API (daily estimated units), converts rank to revenue with the same curve as
`bsr_market_size.py`, and writes monthly revenue plus YoY / 6-month growth.

Requires your own Keepa or Jungle Scout API subscription. Keys are read from the CONFIG
block, Colab Secrets (KEEPA_KEY / JS_KEY / JS_KEY_NAME) or the command line.

Run (Colab cell or terminal):
  pip install pandas numpy openpyxl keepa junglescout-client
  python collect_bsr_history.py --source keepa --products final_products.xlsx --anchors anchors.csv --limit 5

Output workbook sheets:
  asin_monthly    ASIN x month: median BSR, estimated units (conservative/upper/mid), price, revenue
  brand_monthly   market x brand x month revenue
  market_monthly  market x month revenue
  growth          last-12-month revenue, YoY growth, last 6 vs prior 6 months
  log             per-ASIN collection status
"""
import argparse, sys, time, math
from datetime import date, timedelta
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Rank -> units curve: shared with bsr_market_size.py, calibrated from YOUR anchors file
from bsr_market_size import load_anchors, units_per_day

CURVES = {}   # filled in main() from --anchors


def bsr_to_daily(bsr, cat, mode="mid"):
    """mode: low (conservative) / high (upper) / mid (geometric mean)"""
    curve = CURVES.get(cat) or next(iter(CURVES.values()))
    return units_per_day(bsr, curve, {"low": "conservative", "high": "upper", "mid": "mid"}[mode])


# ---------------------------------------------------------------------------
def collect_keepa(asins, key, months, log):
    import keepa
    api = keepa.Keepa(key)
    rows = []
    days = int(months * 30.5)
    for i in range(0, len(asins), 20):            # 20개씩 요청, 토큰 부족 시 라이브러리가 자동 대기
        batch = asins[i:i + 20]
        try:
            prods = api.query(batch, domain="US", history=True, days=days, wait=True)
        except Exception as e:
            for a in batch: log.append((a, "keepa", f"error: {e}"))
            continue
        for p in prods:
            a = p.get("asin"); d = p.get("data") or {}
            if "SALES" not in d or len(d["SALES"]) == 0:
                log.append((a, "keepa", "no sales-rank history")); continue
            s = pd.Series(d["SALES"], index=pd.to_datetime(d["SALES_time"]), dtype=float)
            s = s[s > 0]
            price = None
            for k in ("NEW", "AMAZON", "BUY_BOX_SHIPPING"):
                if k in d and len(d[k]):
                    price = pd.Series(d[k], index=pd.to_datetime(d[k + "_time"]), dtype=float)
                    price = price[price > 0]
                    if len(price): break
            # 월별: BSR은 일 단위로 채운 뒤 월 중앙값 (Keepa 이력은 변동 시점만 기록)
            daily = s.resample("D").last().ffill()
            m = daily.resample("MS").median().rename("bsr")
            df = m.to_frame()
            if price is not None and len(price):
                df["price"] = price.resample("D").last().ffill().resample("MS").median()
            df["asin"] = a
            rows.append(df.reset_index().rename(columns={"index": "month"}))
            log.append((a, "keepa", f"ok {len(m)} months"))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _walk(o, out):
    """Jungle Scout 응답 안에서 date + estimated_units_sold 를 가진 레코드를 찾아 모음"""
    if isinstance(o, dict):
        if "date" in o and "estimated_units_sold" in o:
            out.append(o)
        for v in o.values(): _walk(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o: _walk(v, out)


def collect_junglescout(asins, key_name, key, months, log):
    from junglescout import ClientSync
    from junglescout.models.parameters import Marketplace
    client = ClientSync(api_key_name=key_name, api_key=key, marketplace=Marketplace.US)
    end = date.today() - timedelta(days=1)
    start_all = end - timedelta(days=int(months * 30.5))
    rows = []
    for a in asins:
        recs = []
        s = start_all
        while s < end:                              # 1년 단위로 나눠 요청
            e = min(s + timedelta(days=364), end)
            try:
                r = client.sales_estimates(asin=a, start_date=s.isoformat(), end_date=e.isoformat())
                raw = r.model_dump() if hasattr(r, "model_dump") else (r.dict() if hasattr(r, "dict") else r)
                _walk(raw, recs)
            except Exception as ex:
                log.append((a, "junglescout", f"{s}~{e} error: {ex}"))
            s = e + timedelta(days=1)
            time.sleep(0.3)
        if not recs:
            log.append((a, "junglescout", "no data")); continue
        df = pd.DataFrame(recs)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        m = pd.DataFrame({
            "units_js": df["estimated_units_sold"].astype(float).resample("MS").sum(),
            "price": pd.to_numeric(df.get("last_known_price"), errors="coerce").resample("MS").median()
            if "last_known_price" in df else np.nan,
        })
        m["asin"] = a
        rows.append(m.reset_index().rename(columns={"date": "month"}))
        log.append((a, "junglescout", f"ok {len(m)} months"))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# ---------------------------------------------------------------------------
def build(hist, meta, source):
    h = hist.merge(meta, left_on="asin", right_on="ASIN", how="left")
    h["price"] = h["price"].fillna(h["current_price"])
    days = h["month"].dt.days_in_month
    if source == "keepa":
        for mode in ("low", "high", "mid"):
            h[f"units_{mode}"] = [bsr_to_daily(b, c, mode) for b, c in zip(h.bsr, h.bsr_category)] * days
        h["revenue"] = h["units_mid"] * h["price"]
        h["revenue_low"] = h["units_low"] * h["price"]; h["revenue_high"] = h["units_high"] * h["price"]
    else:
        h["revenue"] = h["units_js"] * h["price"]
    # 진행 중인 이번 달은 제외 (월 일부만 있음)
    h = h[h["month"] < pd.Timestamp(date.today().replace(day=1))]

    # 같은 브랜드·같은 BSR을 공유하는 변형(같은 리스팅)은 한 번만 계산
    if source == "keepa":
        h = h.sort_values("revenue", ascending=False).drop_duplicates(["brand", "month", "bsr"])

    brand = h.groupby(["market", "brand", "month"], as_index=False)["revenue"].sum()
    market = h.groupby(["market", "month"], as_index=False)["revenue"].sum()

    def growth(df, keys):
        out = []
        last = df["month"].max()
        for k, g in df.groupby(keys):
            g = g.set_index("month")["revenue"]
            r12 = g[g.index > last - pd.DateOffset(months=12)].sum()
            p12 = g[(g.index <= last - pd.DateOffset(months=12)) & (g.index > last - pd.DateOffset(months=24))].sum()
            r6 = g[g.index > last - pd.DateOffset(months=6)].sum()
            p6 = g[(g.index <= last - pd.DateOffset(months=6)) & (g.index > last - pd.DateOffset(months=12))].sum()
            row = dict(zip(keys if isinstance(keys, list) else [keys], k if isinstance(k, tuple) else (k,)))
            row.update(최근12개월매출=r12, 직전12개월매출=p12,
                       전년대비성장률=(r12 / p12 - 1) if p12 > 0 else np.nan,
                       최근6개월_vs_직전6개월=(r6 / p6 - 1) if p6 > 0 else np.nan,
                       데이터시작월=g.index.min().strftime("%Y-%m"))
            out.append(row)
        return pd.DataFrame(out)

    g = pd.concat([growth(market, ["market"]).assign(level="market"),
                   growth(brand, ["market", "brand"]).assign(level="brand")], ignore_index=True)
    g = g.sort_values(["level", "market", "최근12개월매출"], ascending=[False, True, False])
    return h, brand, market, g


import re


def _num(s):
    m = re.search(r"[\d,]*\.?\d+", str(s).replace(",", ""))
    return float(m.group()) if m else np.nan


def load_products(path):
    """최종 제품 데이터 파일 → 수집용 메타 (ASIN, market, brand, bsr_category, current_price ...)"""
    if path.lower().endswith((".xlsx", ".xls")):
        d = pd.read_excel(path)
    else:
        sep = "\t" if path.lower().endswith((".tsv", ".txt")) else None
        d = pd.read_csv(path, sep=sep, engine="python", encoding="utf-8-sig")
    d = d.drop_duplicates("ASIN")
    bsr_txt = d["베스트셀러순위"].fillna("").astype(str)
    main = bsr_txt.str.extract(r"#([\d,]+) in ([A-Za-z &',-]+?)\s*\(")
    sub = bsr_txt.str.extract(r"\)\s*#([\d,]+) in ([A-Za-z &',-]+?)(?:\s*#|$)")
    meta = pd.DataFrame({
        "ASIN": d["ASIN"].values,
        "market": d["시장 카테고리_대분류"].values,
        "brand": d["브랜드"].fillna("").astype(str).str.strip().values,
        "bsr_category": main[1].fillna("Beauty & Personal Care").str.strip().values,
        "current_bsr": main[0].str.replace(",", "").astype(float).values,
        "sub_category": sub[1].str.strip().values,
        "sub_rank": sub[0].str.replace(",", "").astype(float).values,
        "current_price": d["가격($)"].map(_num).values if "가격($)" in d else np.nan,
        "count": d["매수(장/쌍)"].map(_num).values if "매수(장/쌍)" in d else np.nan,
        "unit": d["계산단위"].values if "계산단위" in d else None,
        "title": d["상품명"].values if "상품명" in d else "",
    })
    # 브랜드 표기 통일 (abib / Abib 같은 대소문자 차이)
    canon = meta.groupby(meta.brand.str.lower())["brand"].agg(lambda s: s.value_counts().index[0])
    meta["brand"] = meta.brand.str.lower().map(canon)
    return meta


def check_products(meta):
    """상품명에 적힌 수량(42ct, 60 Pack, 32 Count...)과 매수 열이 다른 상품을 표시"""
    pat = r"(\d{1,4})\s*(?:-\s*)?(?:ct\b|count|pack\b|pcs|pieces|patches|stickers|pairs|sheets)"
    title_n = meta["title"].astype(str).str.lower().str.extract(pat)[0].astype(float)
    chk = meta[["ASIN", "market", "brand", "title", "unit", "count", "current_price"]].copy()
    chk["title_count"] = title_n
    chk["flag"] = np.where(title_n.notna() & chk["count"].notna() & (title_n != chk["count"]),
                           "상품명 수량과 매수 불일치", "")
    chk.loc[(chk.market == "벌레 관련 패치") & chk["unit"].astype(str).str.contains("쌍"), "flag"] += " / 벌레 패치인데 단위가 쌍"
    chk.loc[chk.current_price.isna(), "flag"] += " / 가격 없음"
    chk["flag"] = chk["flag"].str.strip(" /")
    return chk


# ===========================================================================
# ▼▼ Colab 셀에 통째로 붙여넣어 실행할 때는 여기만 고치세요 ▼▼
# ===========================================================================
CONFIG = dict(
    SOURCE="keepa",          # "keepa" 또는 "junglescout"
    KEY="",                  # 비워두면 Colab 보안 비밀(🔑)의 KEEPA_KEY / JS_KEY 를 사용
    KEY_NAME="",             # Jungle Scout만: API key name (비우면 보안 비밀 JS_KEY_NAME)
    MONTHS=60,
    DIR="/content/drive/MyDrive/YOUR_PROJECT_FOLDER",   # where inputs live and outputs go
    PRODUCTS="",             # 최종 제품 데이터 파일명 (예: "final_products.xlsx"). 비우면 asins.csv 사용
    ASINS="asins.csv",
    OUT="bsr_history.xlsx",
    ANCHORS="anchors.csv",   # bsr_category,bsr,units_per_day - see bsr_market_size.py
    LIMIT=5,                 # 시험용: 처음 5개만. 전체 수집은 None
)
# ===========================================================================
DATA_DIR = CONFIG["DIR"]


def _colab_secret(name):
    try:
        from google.colab import userdata
        return userdata.get(name)
    except Exception:
        return None


def main():
    import os
    C = CONFIG
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["keepa", "junglescout"], default=C["SOURCE"])
    ap.add_argument("--key", default=C["KEY"])
    ap.add_argument("--key-name", default=C["KEY_NAME"])
    ap.add_argument("--months", type=int, default=C["MONTHS"])
    ap.add_argument("--dir", default=C["DIR"], help="asins.csv를 읽고 결과를 저장할 폴더")
    ap.add_argument("--asins", default=C["ASINS"])
    ap.add_argument("--products", default=C["PRODUCTS"] or None, help="최종 제품 데이터 파일 (있으면 asins.csv 대신 사용)")
    ap.add_argument("--out", default=C["OUT"])
    ap.add_argument("--anchors", default=C["ANCHORS"])
    ap.add_argument("--limit", type=int, default=C["LIMIT"])
    a, _ = ap.parse_known_args()                     # Colab이 붙이는 -f 인자는 무시

    if not a.key:
        a.key = _colab_secret("KEEPA_KEY" if a.source == "keepa" else "JS_KEY")
    if a.source == "junglescout" and not a.key_name:
        a.key_name = _colab_secret("JS_KEY_NAME")
    if not a.key:
        print("API 키가 없어요. CONFIG의 KEY에 넣거나, Colab 왼쪽 🔑(보안 비밀)에 "
              + ("KEEPA_KEY" if a.source == "keepa" else "JS_KEY") + " 를 추가하세요.")
        return

    os.makedirs(a.dir, exist_ok=True)
    P = lambda f: f if os.path.isabs(f) else os.path.join(a.dir, f)
    a.asins, a.out = P(a.asins), P(a.out)
    print(f"폴더: {a.dir}")
    CURVES.update(load_anchors(P(a.anchors)))

    if a.products:
        meta = load_products(P(a.products))
        chk = check_products(meta)
        bad = chk[chk.flag != ""]
        chk.to_csv(P("product_check.csv"), index=False, encoding="utf-8-sig")
        print(f"제품 데이터 {len(meta)}개 로드. 가격·매수 확인 필요 {len(bad)}개 → product_check.csv")
    else:
        meta = pd.read_csv(P(a.asins))
    asins = meta["ASIN"].dropna().unique().tolist()[: a.limit]
    log = []
    print(f"{len(asins)}개 ASIN, {a.months}개월, source={a.source}")
    if a.source == "keepa":
        hist = collect_keepa(asins, a.key, a.months, log)
    else:
        if not a.key_name:
            print("Jungle Scout key name이 없어요 (CONFIG KEY_NAME 또는 보안 비밀 JS_KEY_NAME)"); return
        hist = collect_junglescout(asins, a.key_name, a.key, a.months, log)
    if hist.empty:
        pd.DataFrame(log, columns=["asin", "source", "status"]).to_csv(P("collect_log.csv"), index=False)
        print("수집된 데이터 없음 - collect_log.csv 확인"); return
    hist.to_csv(P("raw_history.csv"), index=False)       # 원본 백업 (다시 집계할 때 재수집 불필요)
    h, brand, market, g = build(hist, meta, a.source)
    with pd.ExcelWriter(a.out) as w:
        h.to_excel(w, sheet_name="asin_monthly", index=False)
        brand.to_excel(w, sheet_name="brand_monthly", index=False)
        market.to_excel(w, sheet_name="market_monthly", index=False)
        g.to_excel(w, sheet_name="growth", index=False)
        pd.DataFrame(log, columns=["asin", "source", "status"]).to_excel(w, sheet_name="log", index=False)
    print(f"완료 → {a.out}  (성공 {sum('ok' in s for _,_,s in log)} / 기록 {len(log)})")


if __name__ == "__main__":
    main()
