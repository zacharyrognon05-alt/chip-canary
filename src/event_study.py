"""Part 2: market reaction to export releases and earnings. Pre-registered in QUESTION.md (section 4).

Specifications: V2-1 to V2-5, Holm correction over the 22 tests, robustness of section 4.4.

For each event and stock (SK Hynix, Samsung, KOSPI):
  - estimation window: the 250 KRX trading days before the event window, minus event days (the
    windows of all three event types);
  - abnormal return = return - normal return (main: constant mean over the estimation window;
    robustness: market model on the SOX of the previous US session);
  - reaction = |CAR| over the event window (main [-1, +1]); normal day = mean |CAR| over all windows
    of the same length in the estimation window made only of non-event days; ratio = reaction /
    normal day (1 = a normal day).
Events whose window overlaps the window of an event of another type are excluded (main).

Tests: V2-1 permutation against placebo windows; V2-2, V2-3 permutation of group labels; V2-4
sign-flip permutation on paired events; V2-5 OLS slope, permutation of the predicted parts.
95% CIs by bootstrap. Two-sided p-values. Verdicts follow QUESTION.md (rule 7).

Usage:
    .venv/bin/python src/event_study.py
"""

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
MARKETS = ROOT / "data" / "raw" / "markets"
OUT = ROOT / "outputs"

STOCKS = {"skhynix": "SK Hynix", "samsung": "Samsung", "kospi": "KOSPI"}
EST_DAYS, MIN_EST_DAYS, MIN_WINDOWS = 250, 100, 30
REPS, SEED = 5_000, 20261007
GAP = 0.5           # meaningful gap, in normal days (QUESTION.md)
BURN_IN = 8         # V2-5: quarters before the first prediction (QUESTION.md, point 4)
UNVERIFIED = ("first20", "2016-09")
MIN_N = 10          # below this many events or quarters, a test is reported as not computable


@dataclass(frozen=True)
class Variant:
    name: str = "main"
    window: tuple = (-1, 1)
    model: str = "mean"            # "mean" or "sox"
    drop_extreme: bool = False     # drop events whose window contains 2026-07-31
    drop_unverified: bool = False  # drop the first20 event of 2016-09
    keep_overlaps: bool = False
    v25_measure: str = "op_change_scaled_first"
    v25_exports: str = "ecos"      # "ecos", "comtrade"
    v25_usd: bool = False


VARIANTS = [
    Variant(),
    Variant("window [0,+3]", window=(0, 3)),
    Variant("market model, SOX", model="sox"),
    Variant("without 2026-07-31", drop_extreme=True),
    Variant("without unverified 2016-09", drop_unverified=True),
    Variant("overlaps included", keep_overlaps=True),
    Variant("V2-5 on revenue", v25_measure="revenue_yoy_first"),
    Variant("V2-5 exports from Comtrade", v25_exports="comtrade"),
    Variant("V2-5 earnings in USD", v25_usd=True),
]


# ---------------------------------------------------------------- data

def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    ret = pd.read_csv(PROC / "daily_returns.csv", index_col="date", parse_dates=True)
    # SOX return of the last US session before each KRX day (US closes before Korea opens)
    sox = pd.read_csv(MARKETS / "sox.csv", index_col="date", parse_dates=True)["Adj Close"]
    sox = sox[sox.index < pd.Timestamp.today().normalize()]  # drop an incomplete current session
    sox_ret = sox.pct_change().rename("sox").reset_index()
    aligned = pd.merge_asof(pd.DataFrame({"date": ret.index}), sox_ret, on="date",
                            allow_exact_matches=False, direction="backward")
    ret["ret_sox_prev"] = aligned["sox"].to_numpy()
    ev = pd.read_csv(PROC / "events.csv", parse_dates=["event_day", "release_date"])
    ev = ev.dropna(subset=["event_day"]).reset_index(drop=True)
    ev["k"] = ev["event_day"].map(pd.Series(np.arange(len(ret)), index=ret.index))
    ev["group"] = np.where(ev["event_type"] == "earnings",
                           "earnings_" + ev["issuer"].str.split().str[0].str.lower(), ev["event_type"])
    return ret, ev


def window_positions(k: int, w: tuple) -> np.ndarray:
    return np.arange(k + w[0], k + w[1] + 1)


def event_mask(ev: pd.DataFrame, n: int, w: tuple) -> np.ndarray:
    mask = np.zeros(n, dtype=bool)
    for k in ev["k"]:
        pos = window_positions(k, w)
        mask[pos[(pos >= 0) & (pos < n)]] = True
    return mask


def overlaps(ev: pd.DataFrame, w: tuple) -> pd.Series:
    win = {t: set(np.concatenate([window_positions(k, w) for k in g["k"]])) for t, g in ev.groupby("event_type")}
    return ev.apply(lambda r: any(set(window_positions(r.k, w)) & s for t, s in win.items() if t != r.event_type), axis=1)


# ---------------------------------------------------------------- reactions per event

def reactions(ret: pd.DataFrame, ev: pd.DataFrame, v: Variant) -> tuple[pd.DataFrame, dict]:
    w, L = v.window, v.window[1] - v.window[0] + 1
    mask = event_mask(ev, len(ret), w)
    x = ret["ret_sox_prev"].to_numpy()
    rows, placebo = [], {}
    for stock in STOCKS:
        r = ret[f"ret_{stock}"].to_numpy()
        ok = ~np.isnan(r) & ~mask & (~np.isnan(x) if v.model == "sox" else True)
        for e in ev.itertuples():
            pos = window_positions(e.k, w)
            lo, hi = pos[0] - EST_DAYS, pos[0]
            if lo < 0 or pos[-1] >= len(r) or np.isnan(r[pos]).any():
                continue
            est = np.arange(lo, hi)
            est_ok = est[ok[est]]
            if len(est_ok) < MIN_EST_DAYS:
                continue
            if v.model == "sox":
                if np.isnan(x[pos]).any():
                    continue
                b, a = np.polyfit(x[est_ok], r[est_ok], 1)
                ar = lambda idx: r[idx] - (a + b * x[idx])
            else:
                mu = r[est_ok].mean()
                ar = lambda idx: r[idx] - mu
            starts = est[: len(est) - L + 1]
            good = np.all([ok[starts + j] for j in range(L)], axis=0)
            starts = starts[good]
            if len(starts) < MIN_WINDOWS:
                continue
            normals = np.abs(sum(ar(starts + j) for j in range(L)))
            normal = normals.mean()
            car = ar(pos).sum()
            rows.append({"stock": stock, "event_id": e.Index, "group": e.group, "event_type": e.event_type,
                         "ref_month": e.ref_month, "release_date": e.release_date, "event_day": e.event_day,
                         "main_sample": e.main_sample, "rule_based_date": e.rule_based_date,
                         "car": car, "normal_day": normal, "ratio": abs(car) / normal,
                         "has_extreme_day": bool(ret["extreme_day"].iloc[pos].any())})
            placebo[(stock, e.Index)] = normals / normal
    return pd.DataFrame(rows), placebo


# ---------------------------------------------------------------- statistics

def two_sided(null: np.ndarray, observed: float, center: float) -> float:
    return (np.sum(np.abs(null - center) >= abs(observed - center)) + 1) / (len(null) + 1)


def level_test(d: pd.DataFrame, placebo: dict, rng) -> dict:
    pools = [placebo[(s, i)] for s, i in zip(d["stock"], d["event_id"])]
    null = np.column_stack([p[rng.integers(0, len(p), REPS)] for p in pools]).mean(axis=1)
    vals = d["ratio"].to_numpy()
    lo, hi = np.percentile(rng.choice(vals, (REPS, len(vals))).mean(axis=1), [2.5, 97.5])
    return {"n": len(vals), "estimate": vals.mean(), "ci_lo": lo, "ci_hi": hi,
            "p_raw": two_sided(null, vals.mean(), null.mean())}


def gap_test(xv: np.ndarray, yv: np.ndarray, rng) -> dict:
    obs = xv.mean() - yv.mean()
    pooled = np.concatenate([xv, yv])
    null = np.array([(lambda p: p[:len(xv)].mean() - p[len(xv):].mean())(rng.permutation(pooled)) for _ in range(REPS)])
    boot = rng.choice(xv, (REPS, len(xv))).mean(axis=1) - rng.choice(yv, (REPS, len(yv))).mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"n": f"{len(xv)} vs {len(yv)}", "estimate": obs, "ci_lo": lo, "ci_hi": hi,
            "p_raw": two_sided(null, obs, 0.0), "mean_x": xv.mean(), "mean_y": yv.mean()}


def paired_test(diff: np.ndarray, rng) -> dict:
    null = (rng.choice([-1, 1], (REPS, len(diff))) * diff).mean(axis=1)
    lo, hi = np.percentile(rng.choice(diff, (REPS, len(diff))).mean(axis=1), [2.5, 97.5])
    return {"n": len(diff), "estimate": diff.mean(), "ci_lo": lo, "ci_hi": hi, "p_raw": two_sided(null, diff.mean(), 0.0)}


def level_class(r: float) -> str:
    return "almost no reaction (<= 1)" if r <= 1 else ("much stronger (>= 2)" if r >= 2 else "between 1 and 2")


def verdict_earnings(r, lo, hi) -> str:
    point = "wrong" if r >= 2 else "right"
    return f"{point}, conclusive" if (lo >= 2 or hi < 2) else f"not conclusive (point estimate: {point})"


def verdict_gap(gap, lo, hi) -> str:
    return "right" if (gap >= GAP and lo > 0) else ("wrong" if hi < GAP else "not conclusive")


def holm(p: pd.Series) -> pd.Series:
    order, m, run, adj = p.sort_values().index, len(p), 0.0, {}
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i]))
        adj[i] = run
    return pd.Series(adj)[p.index]


# ---------------------------------------------------------------- V2-5

def comtrade_exports(q: pd.DataFrame) -> pd.Series:
    ct = pd.read_csv(PROC / "comtrade_kor_hs8542_exports.csv", index_col=0, parse_dates=True)["value_usd"]
    ct.index = ct.index.to_period("M")
    f20 = pd.read_csv(PROC / "kcs_first20_semis.csv").set_index("ref_month")["chip_export_yoy_pct"] / 100
    f20.index = pd.PeriodIndex(f20.index, freq="M")
    out = []
    for quarter in q["quarter"]:
        m = pd.Period(quarter, freq="Q").asfreq("M", "start")
        months = [m, m + 1, m + 2]
        w = [ct.get(x - 12, np.nan) for x in months]
        g = [ct.get(months[0], np.nan) / w[0] - 1, ct.get(months[1], np.nan) / w[1] - 1, f20.get(months[2], np.nan)]
        out.append(np.nan if any(pd.isna(z) for z in w + g) else sum(a * (1 + b) for a, b in zip(w, g)) / sum(w) - 1)
    return pd.Series(out, index=q.index)


def usd_measure(q: pd.DataFrame, measure: str) -> pd.Series:
    e = pd.read_csv(PROC / "earnings.csv")[["firm", "quarter", "revenue_prelim", "revenue_prelim_ly", "op_prelim", "op_prelim_ly"]]
    m = q[["firm", "quarter", "krwusd_q", "krwusd_yoy"]].merge(e, on=["firm", "quarter"], how="left")
    fx_t, fx_ly = m["krwusd_q"], m["krwusd_q"] / (1 + m["krwusd_yoy"])
    if measure == "revenue_yoy_first":
        return pd.Series(((m["revenue_prelim"] / fx_t) / (m["revenue_prelim_ly"] / fx_ly) - 1).to_numpy(), index=q.index)
    return pd.Series(((m["op_prelim"] / fx_t - m["op_prelim_ly"] / fx_ly) / (m["revenue_prelim_ly"] / fx_ly)).to_numpy(), index=q.index)


def predicted_parts(v: Variant) -> pd.DataFrame:
    """Expanding-window prediction of earnings from exports known at t, no look-ahead."""
    q = pd.read_csv(PROC / "quarterly.csv", parse_dates=["date_first20_T3", "date_first_earnings"])
    x = comtrade_exports(q) if v.v25_exports == "comtrade" else q["exports_known_first20"]
    y = usd_measure(q, v.v25_measure) if v.v25_usd else q[v.v25_measure]
    q = q.assign(x=x, y=y)
    rows = []
    for firm, d in q.groupby("firm"):
        d = d.dropna(subset=["x", "y", "date_first20_T3"]).sort_values("quarter")
        for r in d.itertuples():
            train = d[d["date_first_earnings"] < r.date_first20_T3]  # earnings already released at t
            if len(train) < BURN_IN:
                continue
            b, a = np.polyfit(train["x"], train["y"], 1)
            rows.append({"firm": firm, "quarter": r.quarter, "date_first_earnings": r.date_first_earnings,
                         "n_train": len(train), "predicted": a + b * r.x})
    return pd.DataFrame(rows)


def v25(rx: pd.DataFrame, v: Variant, rng) -> list[dict]:
    pred = predicted_parts(v)
    out = []
    for firm, group, stock in [("skhynix", "earnings_sk", "skhynix"), ("samsung", "earnings_samsung", "samsung")]:
        e = rx[(rx["group"] == group) & (rx["stock"] == stock) & rx["main_sample"]]
        d = pred[pred["firm"] == firm].merge(e, left_on="date_first_earnings", right_on="release_date")
        xv, yv = d["predicted"].to_numpy(), (d["car"] / d["normal_day"]).to_numpy()
        if len(xv) < MIN_N:
            out.append({"spec": f"V2-5 priced-in test, {STOCKS[stock]}", "n": len(xv), "estimate": np.nan,
                        "ci_lo": np.nan, "ci_hi": np.nan, "p_raw": np.nan, "verdict": f"not computable (n < {MIN_N})"})
            continue
        slope = np.polyfit(xv, yv, 1)[0]
        null = np.array([np.polyfit(rng.permutation(xv), yv, 1)[0] for _ in range(REPS)])
        boot = []
        for _ in range(REPS):
            idx = rng.integers(0, len(xv), len(xv))
            if np.ptp(xv[idx]) > 0:
                boot.append(np.polyfit(xv[idx], yv[idx], 1)[0])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        sd = xv.std(ddof=1)
        verdict = ("consistent with priced in, not a proof" if lo <= 0 <= hi
                   else ("wrong (positive: reaction to the predictable part)" if lo > 0 else "wrong (negative slope)"))
        out.append({"spec": f"V2-5 priced-in test, {STOCKS[stock]}", "n": len(xv), "estimate": slope,
                    "ci_lo": lo, "ci_hi": hi, "p_raw": two_sided(null, slope, 0.0), "verdict": verdict,
                    "effect_per_sd": slope * sd, "max_effect_per_sd": max(abs(lo), abs(hi)) * sd,
                    "first_quarter": d["quarter"].min(), "last_quarter": d["quarter"].max()})
    return out


# ---------------------------------------------------------------- one full run

def run(ret: pd.DataFrame, ev: pd.DataFrame, v: Variant) -> tuple[pd.DataFrame, pd.DataFrame]:
    ev = ev.copy()
    ev["overlap"] = overlaps(ev, v.window)
    rx, placebo = reactions(ret, ev, v)
    rx = rx.merge(ev[["overlap"]], left_on="event_id", right_index=True)
    use = rx if v.keep_overlaps else rx[~rx["overlap"]]
    if v.drop_extreme:
        use = use[~use["has_extreme_day"]]
    if v.drop_unverified:
        use = use[~((use["event_type"] == UNVERIFIED[0]) & (use["ref_month"] == UNVERIFIED[1]))]
    rng = np.random.default_rng(SEED)
    res = []
    small = lambda spec, n: {"spec": spec, "n": n, "estimate": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                             "p_raw": np.nan, "verdict": f"not computable (n < {MIN_N})"}

    def sel(group, stock, main=True):
        d = use[(use["group"] == group) & (use["stock"] == stock)]
        return d[d["main_sample"]] if main else d

    cells = [(g, s) for g in ("first20", "monthly") for s in STOCKS] + [
        ("earnings_samsung", "samsung"), ("earnings_samsung", "kospi"), ("earnings_sk", "skhynix"), ("earnings_sk", "kospi")]
    for g, s in cells:
        if len(sel(g, s)) < MIN_N:
            res.append(small(f"V2-1 {g}, {STOCKS[s]}", len(sel(g, s))))
            continue
        t = level_test(sel(g, s), placebo, rng)
        t.update(spec=f"V2-1 {g}, {STOCKS[s]}", level=level_class(t["estimate"]),
                 verdict=verdict_earnings(t["estimate"], t["ci_lo"], t["ci_hi"]) if g.startswith("earnings")
                 else "descriptive")
        res.append(t)
    for s in STOCKS:
        t = gap_test(sel("first20", s)["ratio"].to_numpy(), sel("monthly", s)["ratio"].to_numpy(), rng)
        t.update(spec=f"V2-2 first20 > monthly, {STOCKS[s]}", verdict=verdict_gap(t["estimate"], t["ci_lo"], t["ci_hi"]))
        res.append(t)
    for s in STOCKS:
        m = use[(use["group"] == "monthly") & (use["stock"] == s)]
        t = gap_test(m[m["rule_based_date"]]["ratio"].to_numpy(), m[m["main_sample"]]["ratio"].to_numpy(), rng)
        t.update(spec=f"V2-3 monthly before 2016 > after, {STOCKS[s]}",
                 verdict=verdict_gap(t["estimate"], t["ci_lo"], t["ci_hi"]) + " (not interpretable: rule-based dates)")
        res.append(t)
    for g in ("monthly", "first20"):
        wide = use[(use["group"] == g) & use["main_sample"]].pivot(index="event_id", columns="stock", values="ratio")
        for a, b in [("skhynix", "samsung"), ("samsung", "kospi")]:
            dd = wide[[a, b]].dropna()
            t = paired_test((dd[a] - dd[b]).to_numpy(), rng)
            t.update(spec=f"V2-4 {g}, {STOCKS[a]} > {STOCKS[b]}", verdict=verdict_gap(t["estimate"], t["ci_lo"], t["ci_hi"]))
            res.append(t)
    res += v25(use, v, rng)
    out = pd.DataFrame(res)
    ok = out["p_raw"].notna()
    out.loc[ok, "p_holm"] = holm(out.loc[ok, "p_raw"])  # family of 22 tests (fewer if some not computable)
    out.insert(0, "variant", v.name)
    return out, use


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ret, ev = load()
    allres = []
    for v in VARIANTS:
        out, use = run(ret, ev, v)
        allres.append(out)
        if v.name == "main":
            use.to_csv(OUT / "v2_reactions_by_event.csv", index=False)
            out.to_csv(OUT / "v2_main.csv", index=False)
    allres = pd.concat(allres, ignore_index=True)
    allres.to_csv(OUT / "v2_robustness.csv", index=False)

    pd.set_option("display.width", 230)
    main_r = allres[allres["variant"] == "main"]
    cols = ["spec", "n", "estimate", "ci_lo", "ci_hi", "p_raw", "p_holm", "verdict"]
    print("=== Main (22 tests, Holm within the family)")
    print(main_r[cols].round(4).to_string(index=False))
    v25r = main_r[main_r["spec"].str.startswith("V2-5")]
    print("\nV2-5 details:"); print(v25r[["spec", "n", "first_quarter", "last_quarter", "effect_per_sd", "max_effect_per_sd"]].round(3).to_string(index=False))

    print("\n=== Robustness: verdict or Holm significance changes vs main")
    base = main_r.set_index("spec")
    for name, g in allres[allres["variant"] != "main"].groupby("variant", sort=False):
        g = g.set_index("spec")
        relevant = g.index if name.startswith("V2-5") is False else [s for s in g.index if s.startswith("V2-5")]
        changed = [f"{s}: {base.loc[s, 'verdict']} -> {g.loc[s, 'verdict']}"
                   + (f" (Holm sig {base.loc[s, 'p_holm'] < .05} -> {g.loc[s, 'p_holm'] < .05})"
                      if (base.loc[s, "p_holm"] < .05) != (g.loc[s, "p_holm"] < .05) else "")
                   for s in relevant
                   if g.loc[s, "verdict"] != base.loc[s, "verdict"] or (base.loc[s, "p_holm"] < .05) != (g.loc[s, "p_holm"] < .05)]
        print(f"- {name}: " + ("no change" if not changed else "\n    " + "\n    ".join(changed)))
    print("\nSaved: outputs/v2_main.csv, v2_robustness.csv, v2_reactions_by_event.csv")


if __name__ == "__main__":
    main()
