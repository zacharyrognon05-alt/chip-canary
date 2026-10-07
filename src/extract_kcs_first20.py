"""Extract the first-20-days semiconductor export growth from the KCS press releases.

For each "1-20 days" release in data/processed/release_calendar.csv, the attachments (HWP, HWPX,
PDF) are downloaded once into data/raw/kcs_releases/ and read. The figure kept is the year-on-year
growth of semiconductor exports written in the export "(주요품목)" paragraph, e.g.
"전년 동기 대비 반도체(28.5%), ..." (a "△" sign means a decline). This is the first-release figure
as published, not a revised series.

Checks: the export paragraph is the first "(주요품목)" paragraph, before the import section; when
several formats exist, they must give the same figure. Releases where the pattern is missing or
formats disagree are flagged for a manual check.

Usage:
    .venv/bin/python src/extract_kcs_first20.py
"""

import re
import struct
import time
import zipfile
import zlib
from pathlib import Path

import olefile
import pandas as pd
import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CALENDAR = ROOT / "data" / "processed" / "release_calendar.csv"
RAW_DIR = ROOT / "data" / "raw" / "kcs_releases"
OUT_FILE = ROOT / "data" / "processed" / "kcs_first20_semis.csv"

HEADERS = {"User-Agent": "Mozilla/5.0 (research project; chip-canary)"}
DOWNLOAD = "https://www.customs.go.kr/common/nttFileDownload.do?fileKey={}"
PAUSE = 0.5

# "반도체(28.5%)", "반도체(△25.0%)", and from mid-2023 "반도체(△35.4%↓)"
CHIP_YOY = re.compile(r"반도체\s*\(\s*(△)?\s*([\d.]+)\s*%\s*[↑↓]?\s*\)")


# ---------------------------------------------------------------- download

def download(ref_month: str, url: str, session: requests.Session) -> list[Path]:
    """Download all attachments of one release (cached: skipped if already on disk)."""
    cached = sorted(RAW_DIR.glob(f"{ref_month}.*"))
    if cached:
        return cached
    page = session.get(url, headers=HEADERS, timeout=30).text
    files = []
    for key, title in re.findall(r'href="/common/nttFileDownload\.do\?fileKey=(\w+)" title="([^"]+?) 다운로드"', page):
        content = session.get(DOWNLOAD.format(key), headers=HEADERS, timeout=60).content
        path = RAW_DIR / f"{ref_month}.{title.rsplit('.', 1)[-1].lower()}"
        if path.exists():  # same extension twice: keep both
            path = path.with_name(f"{ref_month}_{len(files)}{path.suffix}")
        path.write_bytes(content)
        files.append(path)
        time.sleep(PAUSE)
    return files


# ---------------------------------------------------------------- text extraction

def hwp5_paragraphs(path: Path) -> list[str]:
    """Paragraph texts of an HWP 5 file: OLE container, BodyText/SectionN record streams."""
    ole = olefile.OleFileIO(str(path))
    flags = struct.unpack("<I", ole.openstream("FileHeader").read()[36:40])[0]
    sections = sorted((e for e in ole.listdir() if e[0] == "BodyText"), key=lambda e: int(e[1][7:]))
    paragraphs = []
    for entry in sections:
        data = ole.openstream(entry).read()
        if flags & 1:  # compressed body
            data = zlib.decompress(data, -15)
        i = 0
        while i < len(data):
            header = struct.unpack("<I", data[i:i + 4])[0]
            i += 4
            tag, size = header & 0x3FF, (header >> 20) & 0xFFF
            if size == 0xFFF:
                size = struct.unpack("<I", data[i:i + 4])[0]
                i += 4
            if tag == 67:  # HWPTAG_PARA_TEXT
                paragraphs.append(decode_hwp_text(data[i:i + size]))
            i += size
    return paragraphs


def decode_hwp_text(raw: bytes) -> str:
    """UTF-16 paragraph text; control codes take 1 or 8 characters (HWP 5 format spec)."""
    chars = struct.unpack(f"<{len(raw) // 2}H", raw[: len(raw) // 2 * 2])
    units, k = [], 0
    while k < len(chars):
        c = chars[k]
        if c >= 32:
            units.append(c)
            k += 1
        elif c in (0, 10, 13) or c >= 24:
            if c in (10, 13):
                units.append(32)
            k += 1
        else:
            k += 8
    # Decode as a whole so that surrogate pairs (symbols outside the BMP) are joined
    text = struct.pack(f"<{len(units)}H", *units).decode("utf-16-le", errors="replace")
    return text.strip()


def hwpx_paragraphs(path: Path) -> list[str]:
    archive = zipfile.ZipFile(path)
    paragraphs = []
    for name in sorted(n for n in archive.namelist() if re.match(r"Contents/section\d+\.xml", n)):
        xml = archive.read(name).decode("utf-8")
        for p in re.findall(r"<hp:p[ >].*?</hp:p>", xml, re.S):
            text = "".join(re.findall(r"<hp:t>([^<]*)</hp:t>", p)).strip()
            if text:
                paragraphs.append(text)
    return paragraphs


def pdf_paragraphs(path: Path) -> list[str]:
    # PDF lines break inside sentences: join everything, the regex does not need line structure
    text = " ".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)
    return [re.sub(r"\s+", " ", text)]


def read(path: Path) -> list[str]:
    signature = path.read_bytes()[:4]
    if signature == b"%PDF":
        return pdf_paragraphs(path)
    if signature == b"PK\x03\x04":
        return hwpx_paragraphs(path)
    if signature == b"\xd0\xcf\x11\xe0":
        return hwp5_paragraphs(path)
    raise ValueError(f"Unknown format: {path.name}")


def chip_export_yoy(paragraphs: list[str]) -> tuple[float | None, str]:
    """Y/y growth of chip exports from the first "(주요품목)" passage, which is the export one."""
    text = " ".join(paragraphs)
    start = text.find("(주요품목)")
    if start < 0:
        return None, "no (주요품목) passage"
    # The export passage ends where the next "(주요품목)" (imports) begins
    end = text.find("(주요품목)", start + 1)
    passage = text[start:end if end > 0 else start + 600]
    m = CHIP_YOY.search(passage)
    if not m:
        return None, "no chip figure in export passage"
    value = float(m.group(2))
    return (-value if m.group(1) else value), passage[:200]


# ---------------------------------------------------------------- main

def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cal = pd.read_csv(CALENDAR, dtype=str)
    cal = cal[cal["event_type"] == "first20"]
    session = requests.Session()
    rows = []
    for r in cal.itertuples():
        files = download(r.ref_month, r.url, session)
        by_format = {}
        for f in files:
            try:
                value, context = chip_export_yoy(read(f))
            except Exception as exc:  # unreadable file: recorded, not fatal
                value, context = None, f"read error: {exc}"
            by_format[f.suffix.lstrip(".")] = (value, context)
        values = {fmt: v for fmt, (v, _) in by_format.items() if v is not None}
        distinct = set(values.values())
        if len(distinct) == 1:
            status = "ok" if len(values) == len(by_format) else "ok, some formats unreadable"
        else:
            status = "formats disagree" if distinct else "not found"
        # Preference when several formats agree: HWP family first (always present), then PDF
        chosen = next((values[f] for f in ("hwp", "hwpx", "pdf") if f in values), None)
        rows.append({
            "ref_month": r.ref_month, "release_date": r.release_date,
            "chip_export_yoy_pct": chosen if len(distinct) == 1 else None,
            "status": status, "formats": "+".join(sorted(by_format)),
            "values_by_format": "; ".join(f"{k}={v}" for k, v in sorted(values.items())),
            "context": next((c for _, c in by_format.values() if c), ""),
        })
        print(f"{r.ref_month}  {status:<28} {values}", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(OUT_FILE, index=False)
    print(f"\nReleases: {len(out)}")
    print("Status:", out["status"].value_counts().to_dict())
    flagged = out[~out["status"].str.startswith("ok")]
    if len(flagged):
        print("To check by hand:\n" + flagged[["ref_month", "status", "values_by_format", "context"]].to_string(index=False))
    print(f"Saved: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
