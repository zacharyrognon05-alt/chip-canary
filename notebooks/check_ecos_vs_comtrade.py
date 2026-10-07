"""Cross-check: ECOS semiconductor export value index vs UN Comtrade Korean exports of HS 8542.

Also tests the currency basis of the ECOS index (not stated in the file): if it is in USD, its
year-on-year growth should track Comtrade in USD more closely than Comtrade converted to KRW.
KRW/USD monthly average from Yahoo Finance (KRW=X), downloaded at run time.

Usage:
    .venv/bin/python notebooks/check_ecos_vs_comtrade.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
OUT_FIG = ROOT / "outputs" / "check_ecos_vs_comtrade.html"

ecos = pd.read_csv(ROOT / "data/processed/ecos_semis_export_value_index.csv", index_col=0, parse_dates=True)
ct = pd.read_csv(ROOT / "data/processed/comtrade_kor_hs8542_exports.csv", index_col=0, parse_dates=True)
fx = yf.Ticker("KRW=X").history(start="2012-01-01", end="2026-01-01", auto_adjust=False)["Close"]
fx.index = fx.index.tz_localize(None)

df = pd.DataFrame({"ecos": ecos["value"], "ct_usd": ct["value_usd"] / 1e9})
df = df.join(fx.resample("MS").mean().rename("krwusd")).loc["2012-01":"2025-12"]
df["ct_krw"] = df["ct_usd"] * df["krwusd"]

# Year-on-year growth in %, on the common span (first Comtrade y/y: 2014-01)
yoy = (df[["ecos", "ct_usd", "ct_krw"]].pct_change(12, fill_method=None) * 100).loc["2014-01":]
gap = yoy["ecos"] - yoy["ct_usd"]

print(f"Common span (y/y): {yoy.index.min():%Y-%m} -> {yoy.index.max():%Y-%m}, {len(yoy)} months")
print(f"Corr. y/y ECOS vs Comtrade USD: {yoy['ecos'].corr(yoy['ct_usd']):.3f}")
print(f"Corr. y/y ECOS vs Comtrade KRW: {yoy['ecos'].corr(yoy['ct_krw']):.3f}")
for col in ["ct_usd", "ct_krw"]:
    g = (yoy["ecos"] - yoy[col]).abs()
    print(f"Mean |gap| ECOS - {col}: {g.mean():.1f} pp (median {g.median():.1f}, max {g.max():.1f})")
print(f"Mean signed gap ECOS - Comtrade USD: {gap.mean():+.1f} pp")
print("Mean signed gap by year:", gap.groupby(gap.index.year).mean().round(1).to_dict())

print("\nCross-correlation of y/y (k > 0: Comtrade shifted forward by k months):")
for k in range(-3, 4):
    print(f"  k={k:+d}: {yoy['ecos'].corr(yoy['ct_usd'].shift(k)):.3f}")

ratio = df["ct_usd"] / df["ecos"]
print("\nComtrade USD bn per ECOS index point, yearly mean (scope drift, HS breaks in 2017 and 2022):")
print(ratio.loc["2013":].groupby(ratio.loc["2013":].index.year).mean().round(4).to_dict())

flip = yoy[np.sign(yoy["ecos"]) != np.sign(yoy["ct_usd"])]
print(f"\nMonths where y/y signs differ: {len(flip)} of {len(yoy)}")
print(flip[["ecos", "ct_usd"]].round(1).to_string())

fig = go.Figure()
fig.add_scatter(x=yoy.index, y=yoy["ecos"], name="ECOS index, semiconductors (y/y %)")
fig.add_scatter(x=yoy.index, y=yoy["ct_usd"], name="UN Comtrade HS 8542, USD (y/y %)")
fig.update_layout(title="Korean chip exports: two sources, same cycle",
                  yaxis_title="Year-on-year growth (%)", template="plotly_white", hovermode="x unified")
OUT_FIG.parent.mkdir(exist_ok=True)
fig.write_html(OUT_FIG, include_plotlyjs="cdn")
print(f"\nFigure: {OUT_FIG.relative_to(ROOT)}")
