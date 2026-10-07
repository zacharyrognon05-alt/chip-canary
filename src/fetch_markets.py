"""Download daily prices for Samsung Electronics, SK Hynix, the KOSPI and KRW/USD from Yahoo Finance.

Raw data are cached in data/raw/markets/ and never overwritten unless --refresh is passed,
so that every later step runs on the same snapshot.

Usage:
    .venv/bin/python src/fetch_markets.py            # download missing files only
    .venv/bin/python src/fetch_markets.py --refresh  # re-download everything
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "markets"
MANIFEST = RAW_DIR / "_manifest.csv"

TICKERS = {
    "samsung": "005930.KS",
    "skhynix": "000660.KS",
    "kospi": "^KS11",
    "krwusd": "KRW=X",  # KRW per USD, for the exchange-rate control (robustness)
}
START = "2000-01-01"

# A daily move larger than this is suspicious (split not adjusted, bad tick)
JUMP_THRESHOLD = 0.25


def download(ticker: str) -> pd.DataFrame:
    """Fetch the full daily history, keeping both unadjusted and adjusted prices."""
    df = yf.Ticker(ticker).history(start=START, auto_adjust=False, actions=True)
    if df.empty:
        raise RuntimeError(f"No data returned for {ticker}")
    # Keep only the calendar date (Yahoo returns Asia/Seoul timestamps)
    df.index = df.index.tz_localize(None).normalize()
    df.index.name = "date"
    return df


def check(name: str, df: pd.DataFrame) -> None:
    """Print basic sanity checks: coverage, missing values, splits, suspicious jumps."""
    print(f"\n=== {name} ===")
    print(f"Rows: {len(df)}  |  {df.index.min().date()} -> {df.index.max().date()}")

    missing = df[["Open", "High", "Low", "Close", "Adj Close"]].isna().sum()
    print("Missing values:", dict(missing[missing > 0]) or "none")

    if "Volume" in df and name not in ("kospi", "krwusd"):
        print(f"Zero-volume days: {(df['Volume'] == 0).sum()}")

    if "Stock Splits" in df:
        splits = df.loc[df["Stock Splits"] != 0, "Stock Splits"]
        print("Splits:", {str(d.date()): v for d, v in splits.items()} or "none")

    for col in ["Close", "Adj Close"]:
        ret = df[col].pct_change()
        jumps = ret[ret.abs() > JUMP_THRESHOLD]
        label = f"|daily return| > {JUMP_THRESHOLD:.0%} on {col}"
        print(f"{label}: {len(jumps)}")
        for d, r in jumps.items():
            print(f"    {d.date()}  {r:+.1%}")

    print(df[["Close", "Adj Close", "Volume"]].head(3).to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-download cached files")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    log = []

    for name, ticker in TICKERS.items():
        path = RAW_DIR / f"{name}.csv"
        if path.exists() and not args.refresh:
            print(f"{name}: using cached {path.relative_to(ROOT)}")
            df = pd.read_csv(path, index_col="date", parse_dates=True)
        else:
            print(f"{name}: downloading {ticker} ...")
            df = download(ticker)
            df.to_csv(path)
            log.append({
                "file": path.name,
                "ticker": ticker,
                "downloaded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "first_date": df.index.min().date(),
                "last_date": df.index.max().date(),
                "rows": len(df),
            })
        check(name, df)

    if log:
        new = pd.DataFrame(log)
        if MANIFEST.exists():
            new = pd.concat([pd.read_csv(MANIFEST), new], ignore_index=True)
        new.to_csv(MANIFEST, index=False)
        print(f"\nManifest updated: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
