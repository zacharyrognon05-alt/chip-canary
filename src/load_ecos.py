"""Read the ECOS (Bank of Korea) export value index for semiconductors, downloaded by hand.

The raw CSV is the file exported as-is from ecos.bok.or.kr: one row per series, one column per
month ("1988/01", ..., "2026/08 p)"). This script turns it into a tidy monthly series and keeps
the "p)" (provisional) flag as a column. The raw file is never modified.

Usage:
    .venv/bin/python src/load_ecos.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "ecos" / "Export Value Indices_02183427.csv"
OUT_FILE = ROOT / "data" / "processed" / "ecos_semis_export_value_index.csv"

# Expected metadata: the script stops if the file is not the series we think it is
EXPECTED = {
    "StatisticalTable": "3.3.1.1.1. Export Value Indices",
    "ItemNames1": "Semi-conductors",
    "Unit": "2020=100",
    "Conversion": "Original Data",
}
META_COLS = list(EXPECTED)


def load(path: Path = RAW_FILE) -> pd.DataFrame:
    """Return a monthly DataFrame indexed by month-start date: value, provisional."""
    # Everything read as text so that empty cells and the "p)" suffix are handled explicitly
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    if len(raw) != 1:
        raise ValueError(f"Expected one series in {path.name}, found {len(raw)} rows")

    row = raw.iloc[0]
    for col, expected in EXPECTED.items():
        if row[col].strip() != expected:
            raise ValueError(f"{col}: expected {expected!r}, found {row[col].strip()!r}")

    values = row.drop(META_COLS)
    df = pd.DataFrame({"label": values.index, "raw_value": values.str.strip().values})
    # ECOS marks provisional months in the column header, e.g. "2026/08 p)"
    df["provisional"] = df["label"].str.contains("p)", regex=False)
    df["date"] = pd.to_datetime(df["label"].str[:7], format="%Y/%m")
    df["value"] = pd.to_numeric(df["raw_value"].replace("", None), errors="raise")

    # ECOS exports the full announced range (1988.01-2026.12) even where cells are empty:
    # keep only the span between the first and last observed value
    observed = df["value"].notna()
    first, last = observed.idxmax(), observed[::-1].idxmax()
    df = df.loc[first:last]

    gaps = df.loc[df["value"].isna(), "label"].tolist()
    if gaps:
        raise ValueError(f"Missing values inside the observed span: {gaps}")
    if not df["date"].diff().dropna().dt.days.between(28, 31).all():
        raise ValueError("Months are not consecutive")

    return df.set_index("date")[["value", "provisional"]]


def main() -> None:
    df = load()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE)

    print(f"Source: {RAW_FILE.relative_to(ROOT)}")
    print(f"Months: {len(df)}  |  {df.index.min():%Y-%m} -> {df.index.max():%Y-%m}")
    prov = df.index[df["provisional"]]
    print(f"Provisional (p): {len(prov)} months, {prov.min():%Y-%m} -> {prov.max():%Y-%m}")
    print("\nFirst rows:\n" + df.head(6).to_string())
    print("\nLast rows:\n" + df.tail(10).to_string())
    print(f"\nSaved: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
