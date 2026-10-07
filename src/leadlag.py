"""Part 1: information timing. Specifications pre-registered in QUESTION.md (section 4).

Implemented so far:
  V1-1  Lead time in days, per firm (descriptive, no test).
        Main definition: from the first-20-days release of the quarter's last month to the firm's
        first earnings release. Compared with the thresholds of QUESTION.md on the median
        (< 7 days: wrong; 7-14: intermediate; >= 15: right); mean and shares per band reported.
        Comparison combinations (reported only): monthly release of the last month as starting
        point; Samsung's detailed end-of-month results as end point.
  V1-2  Correlation of y/y growth: exports known at t (exports_known_first20) vs the quarter's
        earnings as first released after t, for SK Hynix and Samsung, revenue and operating profit
        (operating profit as (OP_t - OP_t-4) / Revenue_t-4). Pearson r, Fisher-z 95% CI (main),
        moving-block bootstrap 95% CI (blocks of 4 quarters, check for autocorrelation), raw
        p-value (Holm correction once V1-3 is computed). Verdict against the expected categories
        of QUESTION.md (precision of 2026-10-07).
  V1-3  Comparisons of correlations, paired moving-block bootstrap (same quarters for both series):
        SK Hynix vs Samsung (revenue, OP) and revenue vs OP (SK Hynix, Samsung). Two-sided bootstrap
        p-value. Verdict: right if the 95% CI of the difference is above zero, wrong if the point
        estimate is <= 0, not conclusive otherwise (no equality margin is defined for part 1).
  Holm  Correction over the part 1 family: 4 tests of V1-2 + 4 of V1-3.
  E-3   Descriptive: the V1-2 correlations before 2023 (quarters up to 2022Q4) next to the full sample.
  Robustness (QUESTION.md 4.4, those that apply to part 1): V1-2 and V1-3 redone with
        (r1) UN Comtrade HS 8542 instead of ECOS for months T1 and T2 (2015-2025);
        (r2) earnings converted to USD with the quarterly mean KRW/USD rate.

Usage:
    .venv/bin/python src/leadlag.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"

FIRMS = {"skhynix": "SK Hynix", "samsung": "Samsung Electronics"}
# Reference categorical palette, slots 1-2 in fixed order (dataviz skill, references/palette.md)
COLORS = {"skhynix": "#2a78d6", "samsung": "#eb6834"}
WRONG_BELOW, RIGHT_FROM = 7, 15  # thresholds in days, QUESTION.md section 2

# V1-2: correlation categories (lower bound included) and expected categories (QUESTION.md, 2026-10-07)
CATEGORIES = [("weak", -1.0, 0.3), ("medium", 0.3, 0.6), ("strong", 0.6, 0.8), ("very strong", 0.8, 1.0001)]
EXPECTED = {
    ("skhynix", "revenue"): {"very strong"},
    ("skhynix", "op"): {"medium", "strong"},
    ("samsung", "revenue"): {"medium", "strong"},
    ("samsung", "op"): {"weak", "medium"},
}
MEASURES = {"revenue": "revenue_yoy_first", "op": "op_change_scaled_first"}
BOOT_REPS, BLOCK, SEED = 10_000, 4, 20261007


def band(days: float) -> str:
    if days < WRONG_BELOW:
        return "wrong (< 7 days)"
    if days < RIGHT_FROM:
        return "intermediate (7-14 days)"
    return "right (>= 15 days)"


def lead_times() -> pd.DataFrame:
    q = pd.read_csv(PROC / "quarterly.csv", parse_dates=["date_first20_T3", "date_monthly_T3", "date_first_earnings"])
    e = pd.read_csv(PROC / "earnings.csv")[["firm", "quarter", "last_prelim_date"]]
    q = q.merge(e, on=["firm", "quarter"], how="left")
    # Samsung's detailed results (last preliminary filing of the quarter); SK Hynix files once
    q["date_full_results"] = pd.to_datetime(q["last_prelim_date"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
    q["lead_first20_to_full"] = (q["date_full_results"] - q["date_first20_T3"]).dt.days
    q["lead_monthly_to_full"] = (q["date_full_results"] - q["date_monthly_T3"]).dt.days
    return q


def summarize(q: pd.DataFrame) -> pd.DataFrame:
    defs = {
        "lead_days_main": "MAIN: first-20-days (T3) -> first earnings release",
        "lead_days_from_monthly": "monthly release (T3) -> first earnings release",
        "lead_first20_to_full": "first-20-days (T3) -> full results",
        "lead_monthly_to_full": "monthly release (T3) -> full results",
    }
    rows = []
    for firm in FIRMS:
        d = q[q["firm"] == firm]
        for col, label in defs.items():
            x = d[col].dropna()
            if x.empty:
                continue
            rows.append({
                "firm": FIRMS[firm], "definition": label, "n_quarters": len(x),
                "first_quarter": d.loc[x.index, "quarter"].min(), "last_quarter": d.loc[x.index, "quarter"].max(),
                "median_days": x.median(), "mean_days": round(x.mean(), 1), "min_days": x.min(), "max_days": x.max(),
                "share_under_7": round((x < WRONG_BELOW).mean(), 2),
                "share_7_to_14": round(((x >= WRONG_BELOW) & (x < RIGHT_FROM)).mean(), 2),
                "share_15_plus": round((x >= RIGHT_FROM).mean(), 2),
                "band_of_median": band(x.median()),
                "band_of_mean": band(x.mean()),
            })
    return pd.DataFrame(rows)


def figure(q: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    y_top = 50  # above the longest lead (SK Hynix, 44 days), leaves room for the zone label
    # Threshold zones: wrong (< 7 days, darker), intermediate (7-14, lighter), right (no fill)
    fig.add_hrect(y0=0, y1=WRONG_BELOW, fillcolor="#e9e7e1", line_width=0, layer="below")
    fig.add_hrect(y0=WRONG_BELOW, y1=RIGHT_FROM, fillcolor="#f4f3ef", line_width=0, layer="below")
    for y in (WRONG_BELOW, RIGHT_FROM):
        fig.add_hline(y=y, line_width=1, line_dash="dot", line_color="#52514e")
    # Zone labels on the left, where no curve passes (Samsung never falls below 14 days)
    for y, text in [(WRONG_BELOW / 2, "Expectation wrong (< 7 days)"),
                    ((WRONG_BELOW + RIGHT_FROM) / 2 - 1, "Intermediate (7-14 days)"),
                    (y_top - 2, "Expectation right (>= 15 days)")]:
        fig.add_annotation(x=0, xref="paper", xanchor="left", y=y, text=text, showarrow=False,
                           xshift=4, font=dict(size=11, color="#52514e"))
    for firm, name in FIRMS.items():
        d = q[(q["firm"] == firm) & q["lead_days_main"].notna()]
        fig.add_scatter(
            x=d["quarter"], y=d["lead_days_main"], mode="lines+markers", name=name,
            line=dict(color=COLORS[firm], width=2), marker=dict(size=8, color=COLORS[firm],
                                                               line=dict(width=2, color="#fcfcfb")),
            customdata=d[["date_first20_T3", "date_first_earnings"]].apply(lambda c: c.dt.strftime("%Y-%m-%d")).values,
            hovertemplate=(f"<b>{name}</b> %{{x}}<br>Lead: %{{y}} days<br>"
                           "First-20-days release: %{customdata[0]}<br>First earnings release: %{customdata[1]}"
                           "<extra></extra>"),
        )
        last = d.iloc[-1]
        # Samsung's last point sits near the 15-day line: lift its label above the line
        fig.add_annotation(x=last["quarter"], y=last["lead_days_main"], text=name, showarrow=False,
                           xanchor="left", xshift=8, yshift=12 if firm == "samsung" else 0,
                           font=dict(size=12, color="#0b0b0b"))
    fig.update_layout(
        title=dict(text="Lead time: from the first-20-days export figure to the first earnings release",
                   font=dict(size=16)),
        xaxis=dict(title="Quarter", showgrid=False, tickmode="array",
                   tickvals=sorted(q.loc[q["quarter"].str.endswith("Q1") & q["lead_days_main"].notna(), "quarter"].unique()),
                   ticktext=[v[:4] for v in sorted(q.loc[q["quarter"].str.endswith("Q1") & q["lead_days_main"].notna(), "quarter"].unique())]),
        yaxis=dict(title="Calendar days", range=[0, y_top], gridcolor="#e9e8e4", zeroline=False),
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font=dict(color="#0b0b0b"),
        legend=dict(orientation="h", y=1.08, x=0), hovermode="closest", margin=dict(r=140),
    )
    return fig


def category(r: float) -> str:
    return next(name for name, lo, hi in CATEGORIES if lo <= r < hi)


def categories_spanned(lo: float, hi: float) -> list[str]:
    return [name for name, a, b in CATEGORIES if a < hi and lo < b]


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def block_bootstrap_ci(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    """Moving-block bootstrap: resample blocks of consecutive quarters to keep autocorrelation."""
    n = len(x)
    starts = np.arange(n - BLOCK + 1)
    n_blocks = int(np.ceil(n / BLOCK))
    rs = np.empty(BOOT_REPS)
    for b in range(BOOT_REPS):
        idx = np.concatenate([np.arange(s0, s0 + BLOCK) for s0 in rng.choice(starts, n_blocks)])[:n]
        rs[b] = np.corrcoef(x[idx], y[idx])[0, 1]
    return float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def verdict(r: float, lo: float, hi: float, expected: set[str]) -> str:
    point = "right" if category(r) in expected else "wrong"
    spanned = set(categories_spanned(lo, hi))
    if spanned <= expected:
        return f"{point}, conclusive"
    if not (spanned & expected):
        return f"{point}, conclusive"
    return f"not conclusive (point estimate: {point})"


def correlations(q: pd.DataFrame, last_quarter: str | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    if last_quarter:
        q = q[q["quarter"] <= last_quarter]
    for (firm, measure), expected in EXPECTED.items():
        d = q[q["firm"] == firm].sort_values("quarter").dropna(subset=["exports_known_first20", MEASURES[measure]])
        x, y = d["exports_known_first20"].to_numpy(), d[MEASURES[measure]].to_numpy()
        r, p = stats.pearsonr(x, y)
        lo, hi = fisher_ci(r, len(x))
        blo, bhi = block_bootstrap_ci(x, y, rng)
        rows.append({
            "firm": FIRMS[firm], "measure": "revenue y/y" if measure == "revenue" else "OP change / revenue(t-4)",
            "n": len(x), "first_quarter": d["quarter"].min(), "last_quarter": d["quarter"].max(),
            "r": round(r, 3), "fisher_lo": round(lo, 3), "fisher_hi": round(hi, 3),
            "boot_lo": round(blo, 3), "boot_hi": round(bhi, 3), "p_raw": p,
            "category": category(r), "expected": " or ".join(sorted(expected, key=[c[0] for c in CATEGORIES].index)),
            "fisher_ci_spans": " to ".join(dict.fromkeys(categories_spanned(lo, hi))),
            "boot_ci_spans": " to ".join(dict.fromkeys(categories_spanned(blo, bhi))),
            "verdict_fisher": verdict(r, lo, hi, expected),
            "verdict_boot": verdict(r, blo, bhi, expected),
        })
    return pd.DataFrame(rows)


def paired_panel(q: pd.DataFrame) -> pd.DataFrame:
    """One row per quarter with exports and the four earnings measures (quarters complete for all)."""
    wide = q.pivot(index="quarter", columns="firm", values=list(MEASURES.values()))
    wide.columns = [f"{firm}_{col}" for col, firm in wide.columns]
    x = q.drop_duplicates("quarter").set_index("quarter")["exports_known_first20"]
    return wide.join(x).dropna().sort_index()


COMPARISONS = [
    ("SK Hynix > Samsung, revenue", ("skhynix", "revenue"), ("samsung", "revenue")),
    ("SK Hynix > Samsung, OP", ("skhynix", "op"), ("samsung", "op")),
    ("revenue > OP, SK Hynix", ("skhynix", "revenue"), ("skhynix", "op")),
    ("revenue > OP, Samsung", ("samsung", "revenue"), ("samsung", "op")),
]


def compare_correlations(q: pd.DataFrame) -> pd.DataFrame:
    panel = paired_panel(q)
    n = len(panel)
    x = panel["exports_known_first20"].to_numpy()
    col = lambda key: panel[f"{key[0]}_{MEASURES[key[1]]}"].to_numpy()
    rng = np.random.default_rng(SEED + 1)
    starts, n_blocks = np.arange(n - BLOCK + 1), int(np.ceil(n / BLOCK))
    boot_idx = [np.concatenate([np.arange(s0, s0 + BLOCK) for s0 in rng.choice(starts, n_blocks)])[:n]
                for _ in range(BOOT_REPS)]
    rows = []
    for label, a, b in COMPARISONS:
        ya, yb = col(a), col(b)
        diff = np.corrcoef(x, ya)[0, 1] - np.corrcoef(x, yb)[0, 1]
        d = np.array([np.corrcoef(x[i], ya[i])[0, 1] - np.corrcoef(x[i], yb[i])[0, 1] for i in boot_idx])
        lo, hi = np.nanpercentile(d, [2.5, 97.5])
        # Two-sided bootstrap p-value for H0: no difference
        share_below = (np.sum(d <= 0) + 1) / (BOOT_REPS + 1)
        share_above = (np.sum(d >= 0) + 1) / (BOOT_REPS + 1)
        p = min(1.0, 2 * min(share_below, share_above))
        verdict_ = "right" if lo > 0 else ("wrong" if diff <= 0 else "not conclusive")
        rows.append({"comparison": label, "n": n, "difference": round(diff, 3),
                     "boot_lo": round(lo, 3), "boot_hi": round(hi, 3), "p_raw": p, "verdict": verdict_})
    return pd.DataFrame(rows)


def variant_comtrade(q: pd.DataFrame) -> pd.DataFrame:
    """exports_known_first20 rebuilt with Comtrade (USD) for T1 and T2, KCS first-20-days for T3."""
    ct = pd.read_csv(PROC / "comtrade_kor_hs8542_exports.csv", index_col=0, parse_dates=True)["value_usd"]
    ct.index = ct.index.to_period("M")
    ct_yoy = ct / ct.shift(12) - 1
    f20 = pd.read_csv(PROC / "kcs_first20_semis.csv").set_index("ref_month")["chip_export_yoy_pct"] / 100
    f20.index = pd.PeriodIndex(f20.index, freq="M")
    out = q.copy()
    values = []
    for quarter in out["quarter"]:
        t1 = pd.Period(quarter, freq="Q").asfreq("M", "start")
        months = [t1, t1 + 1, t1 + 2]
        w = [ct.get(m - 12, np.nan) for m in months]
        g = [ct_yoy.get(months[0], np.nan), ct_yoy.get(months[1], np.nan), f20.get(months[2], np.nan)]
        ok = not any(pd.isna(v) for v in w + g)
        values.append(sum(wi * (1 + gi) for wi, gi in zip(w, g)) / sum(w) - 1 if ok else np.nan)
    out["exports_known_first20"] = values
    return out


def variant_usd(q: pd.DataFrame) -> pd.DataFrame:
    """Earnings measures recomputed in USD (quarterly mean KRW per USD, this quarter and a year earlier)."""
    e = pd.read_csv(PROC / "earnings.csv")[["firm", "quarter", "revenue_prelim", "revenue_prelim_ly",
                                            "op_prelim", "op_prelim_ly"]]
    out = q.merge(e, on=["firm", "quarter"], how="left")
    fx_t = out["krwusd_q"]
    fx_ly = fx_t / (1 + out["krwusd_yoy"])
    out["revenue_yoy_first"] = (out["revenue_prelim"] / fx_t) / (out["revenue_prelim_ly"] / fx_ly) - 1
    out["op_change_scaled_first"] = (out["op_prelim"] / fx_t - out["op_prelim_ly"] / fx_ly) / (out["revenue_prelim_ly"] / fx_ly)
    return out


def figure_v1_2(q: pd.DataFrame, corr: pd.DataFrame) -> go.Figure:
    """2x2 small multiples: exports known at t vs earnings, one panel per firm and measure.
    Marker shape encodes the period (circle before 2023, diamond from 2023), colour the firm."""
    panels = [("skhynix", "revenue"), ("skhynix", "op"), ("samsung", "revenue"), ("samsung", "op")]
    ylab = {"revenue": "Revenue, y/y (%)", "op": "OP change / revenue a year earlier (%)"}
    titles = [f"{FIRMS[f]}: {'revenue' if m == 'revenue' else 'operating profit'}" for f, m in panels]
    fig = make_subplots(rows=2, cols=2, subplot_titles=titles, horizontal_spacing=0.1, vertical_spacing=0.16)
    for k, (firm, measure) in enumerate(panels):
        row, col = k // 2 + 1, k % 2 + 1
        d = q[q["firm"] == firm].dropna(subset=["exports_known_first20", MEASURES[measure]])
        for period, symbol, mask in [("before 2023", "circle", d["quarter"] < "2023Q1"),
                                     ("2023 onwards", "diamond", d["quarter"] >= "2023Q1")]:
            dd = d[mask]
            fig.add_scatter(
                x=dd["exports_known_first20"] * 100, y=dd[MEASURES[measure]] * 100, mode="markers",
                name=period, legendgroup=period, showlegend=False,
                marker=dict(symbol=symbol, size=9, color=COLORS[firm], line=dict(width=2, color="#fcfcfb")),
                customdata=dd["quarter"], row=row, col=col,
                hovertemplate="%{customdata}<br>Exports known at t: %{x:.1f}%<br>Earnings: %{y:.1f}%<extra></extra>")
        c = corr[(corr["firm"] == FIRMS[firm]) & (corr["measure"].str.startswith("revenue") == (measure == "revenue"))].iloc[0]
        fig.add_annotation(text=f"r = {c['r']:.2f} [{c['fisher_lo']:.2f}, {c['fisher_hi']:.2f}], n = {c['n']}",
                           xref=f"x{k + 1 if k else ''} domain", yref=f"y{k + 1 if k else ''} domain",
                           x=0.02, y=0.98, xanchor="left", yanchor="top", showarrow=False,
                           font=dict(size=11, color="#52514e"))
        fig.update_xaxes(title_text="Exports known at t, y/y (%)" if row == 2 else None, row=row, col=col,
                         showgrid=False, zeroline=True, zerolinecolor="#d6d5d0")
        fig.update_yaxes(title_text=ylab[measure], row=row, col=col, gridcolor="#e9e8e4",
                         zeroline=True, zerolinecolor="#d6d5d0")
    # Legend for marker shape only, in neutral ink (colour identifies the firm, named in each panel)
    for period, symbol in [("before 2023", "circle"), ("2023 onwards", "diamond")]:
        fig.add_scatter(x=[None], y=[None], mode="markers", name=period, legendgroup=period,
                        marker=dict(symbol=symbol, size=9, color="#52514e"), row=1, col=1)
    fig.update_layout(
        title=dict(text="Chip exports known at t vs earnings first released 2-5 weeks later (2016Q3-2026Q2)",
                   font=dict(size=16)),
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font=dict(color="#0b0b0b"),
        legend=dict(orientation="h", y=1.1, x=0, title_text="Period (marker shape): "),
        height=760, margin=dict(t=120))
    return fig


def holm(pvalues: pd.Series) -> pd.Series:
    order = pvalues.sort_values().index
    m, running, adj = len(pvalues), 0.0, {}
    for k, idx in enumerate(order):
        running = max(running, min(1.0, (m - k) * pvalues[idx]))
        adj[idx] = running
    return pd.Series(adj)[pvalues.index]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    q = lead_times()
    summary = summarize(q)
    summary.to_csv(OUT / "v1_1_lead_time_summary.csv", index=False)
    q[["firm", "quarter", "date_first20_T3", "date_monthly_T3", "date_first_earnings", "date_full_results",
       "lead_days_main", "lead_days_from_monthly", "lead_first20_to_full", "lead_monthly_to_full"]].to_csv(
        OUT / "v1_1_lead_time_by_quarter.csv", index=False)
    figure(q).write_html(OUT / "v1_1_lead_time.html", include_plotlyjs="cdn")

    pd.set_option("display.width", 200)
    print(summary.drop(columns=["band_of_mean"]).to_string(index=False))
    split = summary[summary["band_of_median"] != summary["band_of_mean"]]
    print("\nMedian and mean in different bands:", "none" if split.empty else split[["firm", "definition"]].values.tolist())
    print(f"\nSaved: outputs/v1_1_lead_time_summary.csv, v1_1_lead_time_by_quarter.csv, v1_1_lead_time.html")

    corr = correlations(q)
    corr.to_csv(OUT / "v1_2_correlations.csv", index=False)
    print("\n=== V1-2")
    print(corr.drop(columns=["first_quarter", "last_quarter"]).to_string(index=False))
    figure_v1_2(q, corr).write_html(OUT / "v1_2_correlations.html", include_plotlyjs="cdn")
    print("\nSaved: outputs/v1_2_correlations.csv, v1_2_correlations.html")

    comp = compare_correlations(q)
    family = pd.concat([
        pd.DataFrame({"test": "V1-2 " + corr["firm"] + ", " + corr["measure"], "p_raw": corr["p_raw"]}),
        pd.DataFrame({"test": "V1-3 " + comp["comparison"], "p_raw": comp["p_raw"]}),
    ], ignore_index=True)
    family["p_holm"] = holm(family["p_raw"])
    family["significant_5pct_holm"] = family["p_holm"] < 0.05
    comp = comp.merge(family.assign(comparison=family["test"].str[5:])[["comparison", "p_holm"]], on="comparison")
    comp.to_csv(OUT / "v1_3_comparisons.csv", index=False)
    family.to_csv(OUT / "v1_holm_family.csv", index=False)
    print("\n=== V1-3"); print(comp.to_string(index=False))
    print("\n=== Holm, part 1 family (8 tests)"); print(family.to_string(index=False))

    pre = correlations(q, last_quarter="2022Q4")
    side = corr[["firm", "measure", "n", "r", "fisher_lo", "fisher_hi", "boot_lo", "boot_hi", "category"]].merge(
        pre[["firm", "measure", "n", "r", "fisher_lo", "fisher_hi", "boot_lo", "boot_hi", "category", "expected"]],
        on=["firm", "measure"], suffixes=("_full", "_pre2023"))
    side.to_csv(OUT / "e3_pre2023_vs_full.csv", index=False)
    print("\n=== E-3 (descriptive): before 2023 vs full sample"); print(side.to_string(index=False))
    print("\nSaved: outputs/v1_3_comparisons.csv, v1_holm_family.csv, e3_pre2023_vs_full.csv")

    rob = []
    for name, variant in [("main", q), ("r1 Comtrade for T1-T2", variant_comtrade(q)), ("r2 earnings in USD", variant_usd(q))]:
        c, k = correlations(variant), compare_correlations(variant)
        for r in c.itertuples():
            rob.append({"variant": name, "spec": f"V1-2 {r.firm}, {r.measure}", "n": r.n, "estimate": r.r,
                        "ci_fisher": f"{r.fisher_lo:.3f} to {r.fisher_hi:.3f}", "category": r.category,
                        "verdict": r.verdict_fisher})
        for r in k.itertuples():
            rob.append({"variant": name, "spec": f"V1-3 {r.comparison}", "n": r.n, "estimate": r.difference,
                        "ci_fisher": f"boot {r.boot_lo:.3f} to {r.boot_hi:.3f}", "category": "", "verdict": r.verdict})
    rob = pd.DataFrame(rob)
    rob.to_csv(OUT / "v1_robustness.csv", index=False)
    main_v = rob[rob["variant"] == "main"].set_index("spec")
    print("\n=== Robustness (part 1)")
    for name, g in rob[rob["variant"] != "main"].groupby("variant"):
        changed = [sp for sp, row in g.set_index("spec").iterrows()
                   if (row["verdict"], row["category"]) != (main_v.loc[sp, "verdict"], main_v.loc[sp, "category"])]
        print(f"{name}: n = {g['n'].min()}-{g['n'].max()}; specs whose category or verdict changes: {changed or 'none'}")
    print("Saved: outputs/v1_robustness.csv")


if __name__ == "__main__":
    main()
