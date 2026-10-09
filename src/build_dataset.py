"""Assemble the analysis datasets from the processed sources. No estimation here.

Outputs (data/processed/):
  - daily_returns.csv: daily simple returns (Adj Close) of Samsung, SK Hynix and the KOSPI on KRX
    trading days. A day where a stock has zero volume is bad data (Yahoo): its return is missing,
    not zero, and so is the return of the next day.
  - events.csv: the release calendar, each event mapped to its event day (first KRX trading day on
    or after the release date), with sample flags.
  - quarterly.csv (part 1): one row per firm and quarter, with the information timeline (dates),
    the exports known at each date, and earnings growth as first released.

Exports known at the main starting date t (first-20-days release of the quarter's last month T3):
months T1 and T2 from ECOS (revised series, the only one available), month T3 from the first-20-days
release (first release). They are combined into a quarterly y/y growth with prior-year ECOS levels as
weights: g = sum(L_{m,-12} * (1 + g_m)) / sum(L_{m,-12}) - 1.

Usage:
    .venv/bin/python src/build_dataset.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
MARKETS = ROOT / "data" / "raw" / "markets"

STOCKS = {"samsung": "samsung", "skhynix": "skhynix", "kospi": "kospi"}
SKHYNIX_FIRST_RETURN = "2003-04-15"  # first session after the 1:21 reverse split (decision 30.09.2026)
EXTREME_DAY = "2026-07-31"           # KOSPI +17.9%: every market result with and without it
UNVERIFIED_EVENT = ("first20", "2016-09")  # board date only (22nd instead of the 21st)
MAIN_SAMPLE_FROM = "2016-01-01"      # part 2 main sample: sourced dates only
# Fixed end of the sample, so that a later re-run reproduces the note exactly (decision of 2026-10-09):
# prices and events up to 30 September 2026, earnings up to the second quarter of 2026. Data published
# after these dates (e.g. Samsung's 2026Q3 guidance of 2026-10-08) are ignored even if downloaded.
SAMPLE_END_DATE = "2026-09-30"
SAMPLE_END_QUARTER = "2026Q2"


# ---------------------------------------------------------------- markets

def load_prices() -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(MARKETS / f"{file}.csv", index_col="date", parse_dates=True)
            for name, file in STOCKS.items()}


def trading_days(prices: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    """KRX trading days: any series with positive volume that day (stock files contain zero-volume
    holiday rows filled by Yahoo; the KOSPI file lacks its last day)."""
    days = set()
    for df in prices.values():
        days |= set(df.index[df["Volume"] > 0])
    return pd.DatetimeIndex(sorted(days))


def daily_returns(prices: dict[str, pd.DataFrame], days: pd.DatetimeIndex) -> pd.DataFrame:
    out = pd.DataFrame(index=days)
    for name, df in prices.items():
        px = df["Adj Close"].reindex(days)
        px[df["Volume"].reindex(days).fillna(0) <= 0] = np.nan  # bad or missing day
        ret = px / px.shift(1) - 1  # NaN if either day is missing: no return spans a gap
        if name == "skhynix":
            ret[ret.index < SKHYNIX_FIRST_RETURN] = np.nan
        out[f"ret_{name}"] = ret
    out["extreme_day"] = out.index == EXTREME_DAY
    out.index.name = "date"
    return out


# ---------------------------------------------------------------- events

def map_events(cal: pd.DataFrame, days: pd.DatetimeIndex) -> pd.DataFrame:
    ev = cal.copy()
    rel = pd.to_datetime(ev["release_date"])
    pos = days.searchsorted(rel)
    ev["event_day"] = [days[i].date() if i < len(days) else pd.NaT for i in pos]
    ev["days_to_event_day"] = (pd.to_datetime(ev["event_day"]) - rel).dt.days
    ev["rule_based_date"] = ev["date_source"].eq("rule")
    ev["unverified_date"] = ev["date_source"].eq("board listing (unverified)")
    ev["main_sample"] = (ev["release_date"] >= MAIN_SAMPLE_FROM) & ~ev["rule_based_date"]
    return ev


# ---------------------------------------------------------------- quarterly dataset (part 1)

def quarterly(cal: pd.DataFrame) -> pd.DataFrame:
    ecos = pd.read_csv(PROC / "ecos_semis_export_value_index.csv", index_col=0, parse_dates=True)["value"]
    ecos.index = ecos.index.to_period("M")
    ecos_yoy = ecos / ecos.shift(12) - 1
    f20 = pd.read_csv(PROC / "kcs_first20_semis.csv").set_index("ref_month")["chip_export_yoy_pct"] / 100
    f20.index = pd.PeriodIndex(f20.index, freq="M")

    earn = pd.read_csv(PROC / "earnings.csv")
    earn = earn[earn["quarter"] <= SAMPLE_END_QUARTER]
    fx = pd.read_csv(MARKETS / "krwusd.csv", index_col="date", parse_dates=True)["Close"]
    fx_q = fx.groupby(fx.index.to_period("Q")).mean()

    dates = {kind: cal[cal["event_type"] == kind].set_index("ref_month")["release_date"]
             for kind in ("first20", "monthly")}

    rows = []
    for r in earn.itertuples():
        q = pd.Period(r.quarter, freq="Q")
        months = [q.asfreq("M", "start") + k for k in range(3)]
        t1, t2, t3 = months
        w = [ecos.get(m - 12, np.nan) for m in months]  # prior-year levels as weights

        def combine(growths):
            if any(pd.isna(g) for g in growths) or any(pd.isna(x) for x in w):
                return np.nan
            return sum(wi * (1 + gi) for wi, gi in zip(w, growths)) / sum(w) - 1

        rev_yoy = r.revenue_prelim / r.revenue_prelim_ly - 1 if r.revenue_prelim_ly else np.nan
        rows.append({
            "firm": r.firm, "quarter": r.quarter,
            # Information timeline
            "date_first20_T3": dates["first20"].get(str(t3)),        # main starting point (i)
            "date_monthly_T3": dates["monthly"].get(str(t3)),        # alternative starting point (ii)
            "date_monthly_T3_source": cal[(cal["event_type"] == "monthly") & (cal["ref_month"] == str(t3))]["date_source"].squeeze() if str(t3) in dates["monthly"] else None,
            "date_first_earnings": pd.Timestamp(str(int(r.first_release_date))).date() if not pd.isna(r.first_release_date) else None,
            # Exports known at each starting point (y/y)
            "exports_known_first20": combine([ecos_yoy.get(t1), ecos_yoy.get(t2), f20.get(t3, np.nan)]),
            "exports_full_quarter_ecos": combine([ecos_yoy.get(t1), ecos_yoy.get(t2), ecos_yoy.get(t3)]),
            # Earnings, first release (prior-year figures as stated in the same filing)
            "revenue_yoy_first": rev_yoy,
            "op_change_scaled_first": (r.op_prelim - r.op_prelim_ly) / r.revenue_prelim_ly if r.revenue_prelim_ly else np.nan,
            "revenue_yoy_pub_pct": r.revenue_prelim_yoy_pub,
            "first_release_consolidated": r.first_release_consolidated,
            "amendment_dates": r.amendment_dates,
            # Exchange-rate control: quarterly mean KRW per USD and its y/y change
            "krwusd_q": fx_q.get(q, np.nan),
            "krwusd_yoy": fx_q.get(q, np.nan) / fx_q.get(q - 4, np.nan) - 1,
        })
    df = pd.DataFrame(rows)
    for col in ("date_first20_T3", "date_monthly_T3", "date_first_earnings"):
        df[col] = pd.to_datetime(df[col])
    # Lead times in calendar days (V1-1 main definition, and the alternative)
    df["lead_days_main"] = (df["date_first_earnings"] - df["date_first20_T3"]).dt.days
    df["lead_days_from_monthly"] = (df["date_first_earnings"] - df["date_monthly_T3"]).dt.days
    return df.sort_values(["firm", "quarter"]).reset_index(drop=True)


def main() -> None:
    prices = load_prices()
    days = trading_days(prices)
    days = days[days <= SAMPLE_END_DATE]
    ret = daily_returns(prices, days)
    ret.to_csv(PROC / "daily_returns.csv")

    cal = pd.read_csv(PROC / "release_calendar.csv", dtype=str)
    cal = cal[cal["release_date"] <= SAMPLE_END_DATE]
    ev = map_events(cal, days)
    ev.to_csv(PROC / "events.csv", index=False)

    q = quarterly(cal)
    q.to_csv(PROC / "quarterly.csv", index=False)

    # ---- Checks only (no result is computed or printed here)
    print(f"Sample end: prices and events up to {SAMPLE_END_DATE}, earnings up to {SAMPLE_END_QUARTER}")
    print(f"Trading days: {len(days)}, {days.min().date()} -> {days.max().date()}")
    print("Missing daily returns:", ret.filter(like="ret_").isna().sum().to_dict())
    print(f"\nEvents: {len(ev)}; not mapped to a trading day: {ev['event_day'].isna().sum()} "
          f"(after the last price date)")
    print(ev.groupby("event_type")["days_to_event_day"].describe()[["count", "min", "50%", "max"]])
    print("Main sample events:", ev[ev["main_sample"]].groupby("event_type").size().to_dict())
    print("Rule-based dates:", int(ev["rule_based_date"].sum()), "| unverified dates:", int(ev["unverified_date"].sum()))

    print(f"\nQuarterly rows: {len(q)}")
    filled = q.notna().groupby(q["firm"]).sum()[["date_first20_T3", "exports_known_first20",
                                                 "revenue_yoy_first", "op_change_scaled_first", "krwusd_yoy"]]
    print("Non-missing values per firm:\n" + filled.to_string())
    gap = (q["revenue_yoy_first"] * 100 - q["revenue_yoy_pub_pct"]).abs()
    print(f"Computed vs published revenue y/y: max gap {gap.max():.2f} pp over {gap.notna().sum()} quarters")
    print("\nFirst rows (structure check):")
    print(q[["firm", "quarter", "date_first20_T3", "date_first_earnings", "exports_known_first20",
             "revenue_yoy_first", "op_change_scaled_first"]].dropna().head(3).round({"exports_known_first20": 3, "revenue_yoy_first": 3, "op_change_scaled_first": 3}).to_string(index=False))
    print("\nSaved: daily_returns.csv, events.csv, quarterly.csv in data/processed/")


if __name__ == "__main__":
    main()
