"""Download monthly Korean exports of HS 8542 (electronic integrated circuits) from UN Comtrade.

Reporter: Republic of Korea (code 410), partner: World (0), flow: exports (X), value in current USD.
One raw JSON file per calendar year is cached in data/raw/comtrade/ and reused unless --refresh.
Requires COMTRADE_API_KEY in .env.

Usage:
    .venv/bin/python src/fetch_comtrade.py
    .venv/bin/python src/fetch_comtrade.py --refresh
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "comtrade"
OUT_FILE = ROOT / "data" / "processed" / "comtrade_kor_hs8542_exports.csv"

URL = "https://comtradeapi.un.org/data/v1/get/C/M/HS"  # commodities, monthly, HS as reported
PARAMS = {"reporterCode": 410, "partnerCode": 0, "flowCode": "X", "cmdCode": "8542"}
FIRST_YEAR = 2013  # no Korean monthly data in Comtrade before 2013-01
PAUSE = 1.5  # seconds between calls (free tier rate limit)


def fetch_year(year: int, key: str) -> dict:
    periods = ",".join(f"{year}{m:02d}" for m in range(1, 13))
    r = requests.get(URL, params={**PARAMS, "period": periods},
                     headers={"Ocp-Apim-Subscription-Key": key}, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if payload.get("error"):
        raise RuntimeError(f"{year}: {payload['error']}")
    payload["_downloaded_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    return payload


def load_raw() -> pd.DataFrame:
    rows = []
    for path in sorted(RAW_DIR.glob("kor_hs8542_*.json")):
        payload = json.loads(path.read_text())
        for d in payload["data"]:
            # Keep only the plain total: all customs procedures, all transport modes, no 2nd partner
            if (d["customsCode"], d["motCode"], d["partner2Code"]) != ("C00", 0, 0):
                continue
            rows.append({
                "date": pd.Timestamp(f"{d['period'][:4]}-{d['period'][4:]}-01"),
                "value_usd": d["primaryValue"],
                "hs_version": d["classificationCode"],
                "is_reported": d["isReported"],
                "downloaded_utc": payload["_downloaded_utc"],
            })
    df = pd.DataFrame(rows).sort_values("date")
    if df["date"].duplicated().any():
        raise ValueError(f"Duplicate months: {df.loc[df['date'].duplicated(), 'date'].dt.strftime('%Y-%m').tolist()}")
    return df.set_index("date")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-download cached years")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    key = os.environ.get("COMTRADE_API_KEY")
    if not key:
        raise SystemExit("COMTRADE_API_KEY missing: see .env.example")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in range(FIRST_YEAR, datetime.now().year + 1):
        path = RAW_DIR / f"kor_hs8542_{year}.json"
        # A cached year is reused only if complete (12 months); partial years are re-asked
        if path.exists() and not args.refresh and json.loads(path.read_text())["count"] >= 12:
            continue
        payload = fetch_year(year, key)
        print(f"{year}: {payload['count']} records")
        # Korean monthly data start in 2013-01 (Comtrade availability, checked 2026-10-02).
        # Empty years are not cached, so that a later run picks up newly published months.
        if payload["count"]:
            path.write_text(json.dumps(payload))
        time.sleep(PAUSE)

    df = load_raw()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE)

    span = pd.date_range(df.index.min(), df.index.max(), freq="MS")
    missing = span.difference(df.index)
    print(f"\nMonths: {len(df)}  |  {df.index.min():%Y-%m} -> {df.index.max():%Y-%m}")
    print(f"Missing months inside the span: {[d.strftime('%Y-%m') for d in missing] or 'none'}")
    print("HS versions:", df["hs_version"].value_counts().sort_index().to_dict())
    print("Reported as such (not aggregated by Comtrade):", int(df["is_reported"].sum()))
    show = df.assign(value_usd_bn=df["value_usd"] / 1e9)[["value_usd_bn", "hs_version"]]
    print("\nFirst rows:\n" + show.head(4).round(3).to_string())
    print("\nLast rows:\n" + show.tail(4).round(3).to_string())
    print(f"\nSaved: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
