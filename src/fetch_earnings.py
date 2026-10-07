"""Quarterly earnings of Samsung Electronics and SK Hynix from OpenDART, with release dates.

Two sources per quarter:
  - first release: the "연결재무제표기준영업(잠정)실적(공정공시)" filing (preliminary consolidated
    results, unaudited). Samsung files twice per quarter (early-month guidance, then detailed
    results at the end of the month); SK Hynix files once (around the 25th). The FIRST filing of each
    quarter is the moment the market learns the figures. Its table gives revenue and operating
    profit for the quarter, the same quarter a year earlier, and the y/y change as published.
  - final figures: quarterly / annual reports via the key-accounts API (fnlttSinglAcnt, 2015+).
    Q4 = annual minus 9-month cumulative.

Raw API answers are cached in data/raw/dart/ and reused unless --refresh is passed.
Requires DART_API_KEY in .env.

Usage:
    .venv/bin/python src/fetch_earnings.py
"""

import argparse
import html
import io
import json
import os
import re
import time
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "dart"
OUT_FILE = ROOT / "data" / "processed" / "earnings.csv"

API = "https://opendart.fss.or.kr/api/"
# corp_code from OpenDART corpCode.xml (checked 2026-10-04): stock codes 005930 and 000660
FIRMS = {"samsung": "00126380", "skhynix": "00164779"}
FIRST_YEAR = 2010
# Preliminary results: "연결재무제표기준영업(잠정)실적" (consolidated); before 2011 Samsung's early-month
# guidance was filed as "영업(잠정)실적" (basis not stated in the title): both are first releases
PRELIM = r"영업\(잠정\)실적"
REPORTS = {"11013": 1, "11012": 2, "11014": 3, "11011": 4}  # report code -> quarter
PAUSE = 0.7

UNITS = {"조원": 1e12, "억원": 1e8, "백만원": 1e6, "천원": 1e3}


# ---------------------------------------------------------------- API with cache

def call(endpoint: str, params: dict, cache: Path, key: str, refresh: bool, binary: bool = False):
    if cache.exists() and not refresh:
        return cache.read_bytes() if binary else json.loads(cache.read_text())
    r = requests.get(API + endpoint, params={"crtfc_key": key, **params}, timeout=120)
    r.raise_for_status()
    time.sleep(PAUSE)
    if binary:
        cache.write_bytes(r.content)
        return r.content
    payload = r.json()
    if payload.get("status") not in ("000", "013"):  # 013 = no data
        raise RuntimeError(f"{endpoint} {params}: {payload.get('status')} {payload.get('message')}")
    cache.write_text(json.dumps(payload, ensure_ascii=False))
    return payload


def filings(firm: str, key: str, refresh: bool) -> pd.DataFrame:
    rows = []
    for year in range(FIRST_YEAR, date.today().year + 1):
        page = 1
        while True:
            # The current year is always re-asked: new filings arrive
            cache = RAW_DIR / f"list_{firm}_{year}_p{page}.json"
            payload = call("list.json", {"corp_code": FIRMS[firm], "bgn_de": f"{year}0101",
                                         "end_de": f"{year}1231", "page_no": page, "page_count": 100},
                           cache, key, refresh or year == date.today().year)
            rows += payload.get("list", [])
            if page >= int(payload.get("total_page", 1)):
                break
            page += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- preliminary filings

def number(tok: str) -> float | None:
    tok = tok.replace(",", "").replace("+", "")
    try:
        return float(tok)
    except ValueError:
        return None  # "-", "흑자전환" (turned to profit), "적자전환" (turned to loss)


def parse_prelim(xml_zip: bytes) -> dict:
    """Revenue and operating profit of the quarter from a preliminary-results filing."""
    archive = zipfile.ZipFile(io.BytesIO(xml_zip))
    raw = archive.read(archive.namelist()[0])
    for enc in ("utf-8", "euc-kr"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))

    unit_match = re.search(r"단위\s*[:：]?\s*(조원|억원|백만원|천원|원)", text)
    declared = unit_match.group(1) if unit_match else None
    unit = declared
    # Samsung's filings of 2010-2016 declare "백만원" while the figures are in 조원 (e.g. revenue
    # "57.00" for 2013Q2). If the declared unit gives an impossible quarterly revenue for these firms
    # (outside 1 to 500 trillion KRW), use the unit that gives a plausible one, and record it.
    rev = re.search(r"매출액\s*당해실적\s+(\S+)", text)
    rev_value = number(rev.group(1)) if rev else None
    if rev_value and not (1e12 <= rev_value * UNITS.get(declared, 0) <= 5e14):
        plausible = [u for u, f in UNITS.items() if 1e12 <= rev_value * f <= 5e14]
        unit = plausible[0] if len(plausible) == 1 else None
    out = {"unit_declared": declared, "unit": unit, "unit_corrected": unit != declared}
    for label, name in [("매출액", "revenue"), ("영업이익", "op")]:
        # Row up to "누계실적". Two layouts:
        #   5 cells: current, previous quarter, q/q %, same quarter last year, y/y %
        #   7 cells (from 2025Q3): current, previous, q/q %, sign-change flag, last year, y/y %, flag
        m = re.search(label + r"\s*당해실적\s+(.*?)\s+누계실적", text)
        cells = m.group(1).split() if m else []
        if len(cells) == 7:
            cur, ly, yoy = cells[0], cells[4], cells[5]
        elif len(cells) == 5:
            cur, ly, yoy = cells[0], cells[3], cells[4]
        else:
            out[f"{name}_prelim"] = out[f"{name}_prelim_ly"] = out[f"{name}_prelim_yoy_pub"] = None
            out["layout_error"] = f"{label}: {len(cells)} cells"
            continue
        scale = UNITS.get(unit)
        cur, ly = number(cur), number(ly)
        out[f"{name}_prelim"] = cur * scale if cur is not None and scale else None
        out[f"{name}_prelim_ly"] = ly * scale if ly is not None and scale else None
        out[f"{name}_prelim_yoy_pub"] = number(yoy)  # as published (None if sign change)
    return out


def quarter_of(filing_date: str) -> str:
    """A results filing refers to the last quarter that ended before it (e.g. 2024-04-05 -> 2024Q1)."""
    d = pd.Timestamp(filing_date)
    return str((d.to_period("Q") - 1))


def prelim_table(firm: str, fl: pd.DataFrame, key: str, refresh: bool) -> pd.DataFrame:
    all_prelim = fl[fl["report_nm"].str.contains(PRELIM, regex=True)].copy()
    all_prelim["quarter"] = all_prelim["rcept_dt"].map(quarter_of)
    # Amendments ([기재정정]) can change the figures after the first release (e.g. Samsung 2016Q3:
    # revised guidance on 2016-10-12, operating profit about 7.8 -> 5.2 trillion KRW after the Galaxy
    # Note 7 stop, per Samsung Newsroom): kept as dates, a separate news event
    is_amend = all_prelim["report_nm"].str.contains("정정", regex=False)
    amendments = all_prelim[is_amend].groupby("quarter")["rcept_dt"].apply(lambda d: " ".join(sorted(set(d))))
    f = all_prelim[~is_amend]
    f = f.sort_values(["quarter", "rcept_dt", "rcept_no"])
    rows = []
    for q, grp in f.groupby("quarter"):
        first = grp.iloc[0]
        doc = call("document.xml", {"rcept_no": first["rcept_no"]},
                   RAW_DIR / f"doc_{first['rcept_no']}.zip", key, refresh, binary=True)
        rows.append({"firm": firm, "quarter": q, "first_release_date": first["rcept_dt"],
                     "first_release_rcept_no": first["rcept_no"],
                     "first_release_consolidated": "연결" in first["report_nm"],
                     "n_prelim_filings": len(grp),
                     "last_prelim_date": grp.iloc[-1]["rcept_dt"],
                     "amendment_dates": amendments.get(q, ""),
                     **parse_prelim(doc)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- final figures

def amount(row: dict, field: str) -> float | None:
    v = (row.get(field) or "").replace(",", "")
    return float(v) if v not in ("", "-") else None


def final_table(firm: str, key: str, refresh: bool) -> pd.DataFrame:
    rows = []
    for year in range(2015, date.today().year + 1):
        acc = {}
        for code, qn in REPORTS.items():
            payload = call("fnlttSinglAcnt.json", {"corp_code": FIRMS[firm], "bsns_year": year, "reprt_code": code},
                           RAW_DIR / f"acnt_{firm}_{year}_{code}.json", key, refresh or year >= date.today().year - 1)
            for r in payload.get("list", []):
                if r["fs_div"] == "CFS" and r["account_nm"] in ("매출액", "영업이익"):
                    name = "revenue" if r["account_nm"] == "매출액" else "op"
                    acc[(qn, name)] = (amount(r, "thstrm_amount"), r["rcept_no"])
        for qn in (1, 2, 3, 4):
            row = {"firm": firm, "quarter": f"{year}Q{qn}"}
            for name in ("revenue", "op"):
                if (qn, name) not in acc:
                    row[f"{name}_final"] = None
                    continue
                value, rcept = acc[(qn, name)]
                if qn == 4:  # annual report gives the year: Q4 = year - (Q1 + Q2 + Q3)
                    parts = [acc.get((k, name), (None,))[0] for k in (1, 2, 3)]
                    value = value - sum(parts) if value is not None and None not in parts else None
                row[f"{name}_final"] = value
                row["report_rcept_no"] = rcept
                row["report_date"] = rcept[:8]
            if row.get("revenue_final") is not None or row.get("op_final") is not None:
                rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- main

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-download cached answers")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    key = os.environ.get("DART_API_KEY")
    if not key:
        raise SystemExit("DART_API_KEY missing: see .env.example")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    tables = []
    for firm in FIRMS:
        fl = filings(firm, key, args.refresh)
        prelim = prelim_table(firm, fl, key, args.refresh)
        final = final_table(firm, key, args.refresh)
        tables.append(prelim.merge(final, on=["firm", "quarter"], how="outer"))
    df = pd.concat(tables, ignore_index=True).sort_values(["firm", "quarter"])
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    for firm, d in df.groupby("firm"):
        print(f"\n=== {firm}")
        p = d.dropna(subset=["first_release_date"])
        print(f"Preliminary releases: {len(p)} quarters, {p['quarter'].min()} -> {p['quarter'].max()}")
        print(f"Final figures: {d['revenue_final'].notna().sum()} quarters "
              f"({d.loc[d['revenue_final'].notna(), 'quarter'].min()} -> {d.loc[d['revenue_final'].notna(), 'quarter'].max()})")
        print("Prelim filings per quarter:", p["n_prelim_filings"].value_counts().sort_index().to_dict())
        print("Units used:", p["unit"].value_counts(dropna=False).to_dict(),
              "| corrected from declared unit:", int(p["unit_corrected"].sum()),
              f"({', '.join(p.loc[p['unit_corrected'], 'quarter'].agg(['min', 'max']))})" if p["unit_corrected"].any() else "")
        for name in ("revenue", "op"):
            print(f"{name}: prelim parsed in {p[f'{name}_prelim'].notna().sum()} of {len(p)} quarters")
            no_ly = p.loc[p[f"{name}_prelim_ly"].isna(), "quarter"].tolist()
            print(f"  {name}: quarters without the prior-year figure: {no_ly or 'none'}")
        if "layout_error" in p and p["layout_error"].notna().any():
            print("  Unknown table layout:", p.loc[p["layout_error"].notna(), ["quarter", "layout_error"]].values.tolist())
        # Check: first-release figure vs final figure, where both exist
        both = d.dropna(subset=["revenue_prelim", "revenue_final"])
        gap = (both["revenue_prelim"] / both["revenue_final"] - 1) * 100
        print(f"Revenue prelim vs final ({len(both)} quarters): median gap {gap.abs().median():.2f}%, max {gap.abs().max():.2f}%")
        if len(both) and gap.abs().max() > 2:
            print(both.assign(gap_pct=gap.round(2))[["quarter", "unit", "revenue_prelim", "revenue_final", "gap_pct"]]
                  .loc[gap.abs() > 2].to_string(index=False))
        missing = sorted(set(d.loc[d["revenue_final"].notna(), "quarter"]) - set(p["quarter"]))
        print("Quarters with final figures but no preliminary filing:", missing or "none")
    print(f"\nSaved: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
