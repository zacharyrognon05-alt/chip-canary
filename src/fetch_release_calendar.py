"""Build the calendar of Korean export releases used as events in the market study (part 2).

Three event types:
  - "monthly": full-month trade release by the trade ministry (MOTIE, now MOTIR), usually on the
    1st of the following month. Source: press release board of motir.go.kr.
  - "first20": Korea Customs Service release of exports for days 1-20 of the month, usually on the
    21st. Source: KCS press release board (customs.go.kr). First release found: 2016-06-21.
  - "earnings": first earnings release of each quarter by Samsung Electronics (early-month
    guidance) and SK Hynix (around the 25th). Source: OpenDART filing dates, read from
    data/processed/earnings.csv (run src/fetch_earnings.py first).

Every date comes from the issuing body (board listing, file name or filing date), never from a rule
such as "the 1st", with one exception: monthly releases of 2003-2015 (extension sample), whose
dates cannot be sourced (MOTIE board migration). They follow the rule "1st of the following month"
and carry date_source = "rule". On 2016-2026 the rule falls on the right KRX trading day for all
129 sourced releases with price data; before 2016 it remains a hypothesis.
Raw listings are cached in data/raw/calendar/ and reused unless --refresh is passed.

Usage:
    .venv/bin/python src/fetch_release_calendar.py
    .venv/bin/python src/fetch_release_calendar.py --refresh
"""

import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "calendar"
KCS_RAW = RAW_DIR / "kcs_press_titles.csv"
KCS_ATTACH_RAW = RAW_DIR / "kcs_first20_attachments.csv"
MOTIE_RAW = RAW_DIR / "motie_trade_titles.csv"
EARNINGS_FILE = ROOT / "data" / "processed" / "earnings.csv"
OUT_FILE = ROOT / "data" / "processed" / "release_calendar.csv"
DART_VIEW = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}"
FIRM_NAMES = {"samsung": "Samsung Electronics", "skhynix": "SK Hynix"}
# Rule-based monthly dates (decision of 2026-10-02): releases from 2003-01-01 to the last month
# before the first sourced release (2016-01-04)
RULE_FIRST_RELEASE = "2003-01-01"

HEADERS = {"User-Agent": "Mozilla/5.0 (research project; chip-canary)"}
PAUSE = 0.5  # seconds between requests, to stay polite with government servers

KCS_LIST = "https://www.customs.go.kr/kcs/na/ntt/selectNttList.do"
KCS_VIEW = "https://www.customs.go.kr/kcs/na/ntt/selectNttInfo.do?mi=2891&bbsId=1362&nttSn={}&nttSnUrl={}"
KCS_FORM = {
    "confmUseAt": "N", "bbsId": "1362", "minSn": "0", "menuId": "2891", "newHour": "24",
    "cntntsId": "1362", "maxSn": "10", "manageAt": "N", "wrterId": "1", "sysId": "kcs",
    "menuTy": "BBS", "listUseAt": "Y", "authChk": "false", "bbsTy": "NORMAL", "useAt": "Y",
    "mi": "2891", "noticeAt": "N",
}
KCS_STOP = "2016-05-01"  # no "first 20 days" release exists before June 2016 (checked 2026-10-02)

MOTIE_LIST = "https://www.motir.go.kr/kor/article/ATCL3f49a5a8c"
MOTIE_VIEW = MOTIE_LIST + "/{}/view"
# Older posts were migrated: the board shows 2016-12-09 for all of them, so their dates are unusable.
# First reliable monthly release: 2016-01-04 (December 2015 figures). Checked 2026-10-02.
MOTIE_MIGRATION_DATE = "2016-12-09"
MOTIE_RELIABLE_FROM = "2016-01-01"
# Titles are written both ways ("수출입 동향" and "수출입동향"): search both
MOTIE_KEYWORDS = ["수출입 동향", "수출입동향"]


# ---------------------------------------------------------------- scraping

def get(session: requests.Session, url: str, method: str = "GET", **kwargs) -> str:
    for attempt in range(3):
        try:
            r = session.request(method, url, headers=HEADERS, timeout=30, **kwargs)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5)


def scrape_kcs() -> pd.DataFrame:
    """Walk the KCS press board backwards until KCS_STOP; return date, title and post ids."""
    s = requests.Session()
    get(s, KCS_LIST + "?mi=2891&bbsId=1362")  # session cookie required for paging
    rows, page = [], 1
    while True:
        html = get(s, KCS_LIST, method="POST", data={**KCS_FORM, "currPage": page})
        posts = re.findall(r'data-id="(\d+)" data-url="(\w+)" class="nttInfoBtn" title="([^"]*)"', html)
        dates = re.findall(r'data-table="date">(\d{4}\.\d\d\.\d\d)', html)
        if not posts or len(posts) != len(dates):
            raise RuntimeError(f"KCS page {page}: unexpected layout ({len(posts)} posts, {len(dates)} dates)")
        for (sn, key, title), d in zip(posts, dates):
            rows.append({"date": d.replace(".", "-"), "title": title, "ntt_sn": sn, "ntt_key": key})
        print(f"  KCS page {page}: oldest {dates[-1]}", flush=True)
        if dates[-1].replace(".", "-") < KCS_STOP:
            break
        page += 1
        time.sleep(PAUSE)
    return pd.DataFrame(rows)


def scrape_kcs_attachments(kcs: pd.DataFrame) -> pd.DataFrame:
    """Attachment names of each "first 20 days" release.

    The board date is the posting date, which can lag the actual release by up to 6 days
    (e.g. days 1-20 of May 2026: released 2026-05-21, posted 2026-05-27). The file names usually
    start with the real release date ("260521 26년 5월 1일 - 5월 20일 수출입현황.pdf").
    """
    s = requests.Session()
    rows = []
    for r in kcs[kcs["title"].map(lambda t: parse_kcs_first20(t) is not None)].itertuples():
        html = get(s, KCS_VIEW.format(r.ntt_sn, r.ntt_key))
        names = re.findall(r'([^<>"\n]{3,150}?\.(?:hwpx|hwp|pdf))', html)
        names = dict.fromkeys(n.strip() for n in names if "javascript" not in n)
        rows.append({"ntt_sn": r.ntt_sn, "attachments": " | ".join(names)})
        time.sleep(PAUSE)
    return pd.DataFrame(rows)


def scrape_motie() -> pd.DataFrame:
    """Search the MOTIE board for "수출입 동향" and read each hit's attachment names (release time)."""
    s = requests.Session()
    rows = []
    for keyword in MOTIE_KEYWORDS:
        page = 1
        while True:
            html = get(s, MOTIE_LIST, params={"searchCondition": "1", "searchKeyword": keyword, "pageIndex": page})
            hits = re.findall(
                r"article\.view\('(\d+)'\); return false;\">(.*?)</a>.*?(\d{4}-\d\d-\d\d)", html, re.S)
            if not hits:
                break
            for art_id, title, d in hits:
                title = re.sub(r"<[^>]+>|\s+", " ", title).replace("&#039;", "'").strip()
                rows.append({"date": d, "title": title, "article_id": art_id})
            print(f"  MOTIE '{keyword}' page {page}: oldest {hits[-1][2]}", flush=True)
            page += 1
            time.sleep(PAUSE)
    df = pd.DataFrame(rows).drop_duplicates("article_id").sort_values("date", ascending=False)

    # Attachment names often carry the embargo time, e.g. "0201 (1일11시) 수출입과, '16년 1월 ..."
    files = []
    for art_id in df["article_id"]:
        if not is_motie_monthly(df.loc[df["article_id"] == art_id, "title"].iloc[0]):
            files.append("")
            continue
        html = get(s, MOTIE_VIEW.format(art_id))
        names = re.findall(r"([^<>\n]+?\.(?:hwpx|hwp|pdf))\s*\[", html)
        files.append(" | ".join(dict.fromkeys(n.strip() for n in names)))
        time.sleep(PAUSE)
    df["attachments"] = files
    return df


# ---------------------------------------------------------------- parsing

MONTHLY_EXCLUDE = re.compile(r"ICT|정보통신|기업규모|기업특성|지역|지자체|농|수산|식품|에너지|자동차|점검|동영상|1일\s*[~∼]")


def is_motie_monthly(title: str) -> bool:
    return bool(re.search(r"수출입\s*동향", title)) and not MONTHLY_EXCLUDE.search(title)


def title_month(title: str) -> int | None:
    """Month named in the title, e.g. "'18.6월 및 상반기" -> 6, "2018년 수출입동향" (annual) -> 12."""
    m = re.search(r"(\d{1,2})월", title)
    if m:
        return int(m.group(1))
    return 12 if re.search(r"\d{2,4}년\s*(연간\s*)?수출입", title) else None


def release_time(attachments: str) -> str | None:
    """Embargo hour from file names such as '(1일11시)' or '(11시 엠바고)'."""
    m = re.search(r"(\d{1,2})시", attachments or "")
    if m:
        return f"{int(m.group(1)):02d}:00"
    # "조간" = embargoed for the morning papers: public before the market opens
    return "morning" if "조간" in (attachments or "") else None


FIRST20 = re.compile(
    r"(\d{1,2})월\s*\(?\s*1\s*일?\s*[~∼～\-]\s*(?:\d{1,2}월\s*)?20일"  # "9월 1일 ~ 9월 20일", "6월(1∼20일)"
    r"|(\d{1,2})\.\s*1\s*[~∼～\-]\s*(?:\d{1,2}\.)?\s*20"            # "8.1~20", "8.1~8.20"
)


def parse_kcs_first20(title: str) -> int | None:
    m = FIRST20.search(title)
    if not m:
        return None
    return int(m.group(1) or m.group(2))


def date_from_files(attachments: str, board_date: str) -> str | None:
    """Release date written at the start of a file name: "260521 ...", "20170421...", "1201(...".

    Accepted only if it falls within the 10 days up to the board date (otherwise it is probably a
    different number, and the board date is kept).
    """
    board = pd.Timestamp(board_date)
    candidates = []
    for name in (attachments or "").split(" | "):
        name = re.sub(r"^\(.*?\)\s*", "", name.strip())  # drop prefixes like "(홈페이지) " or "(수정) "
        if m := re.match(r"(20\d{2})(\d{2})(\d{2})", name):
            candidates.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
        elif m := re.match(r"(\d{2})(\d{2})(\d{2})(?!\d)", name):
            candidates.append((2000 + int(m.group(1)), int(m.group(2)), int(m.group(3))))
        elif m := re.match(r"(\d{2})(\d{2})(?!\d)", name):  # MMDD only: year of the board date
            candidates.append((board.year, int(m.group(1)), int(m.group(2))))
    for y, mo, d in candidates:
        try:
            date = pd.Timestamp(year=y, month=mo, day=d)
        except ValueError:
            continue
        if pd.Timedelta(0) <= board - date <= pd.Timedelta(days=10):
            return str(date.date())
    return None


def earnings_events(earnings: pd.DataFrame) -> list[dict]:
    """First earnings release of each quarter (date of the first preliminary-results filing)."""
    events = []
    for r in earnings.dropna(subset=["first_release_date"]).itertuples():
        q = pd.Period(r.quarter, freq="Q")
        release = pd.Timestamp(str(int(r.first_release_date)))
        events.append({
            # Reference month = last month of the quarter, so that months_after_ref is comparable
            "event_type": "earnings", "ref_month": str(q.asfreq("M", "end")), "ref_quarter": r.quarter,
            "release_date": str(release.date()), "board_date": None, "file_date": None,
            "date_source": "DART filing date",
            "title_month_ok": True, "release_time_kst": None, "issuer": FIRM_NAMES[r.firm],
            "title": "연결재무제표기준영업(잠정)실적(공정공시)",
            "url": DART_VIEW.format(r.first_release_rcept_no),
        })
    return events


def build(kcs: pd.DataFrame, kcs_files: pd.DataFrame, motie: pd.DataFrame,
          earnings: pd.DataFrame | None = None) -> pd.DataFrame:
    events = []

    for r in motie.itertuples():
        if r.date < MOTIE_RELIABLE_FROM or r.date == MOTIE_MIGRATION_DATE or not is_motie_monthly(r.title):
            continue
        # Titles are too irregular to give the year reliably ("6월 및 상반기", "'17.12월"): the
        # reference month is the month before release, and the month in the title is a check
        rel = pd.Timestamp(r.date)
        ref = (rel.to_period("M") - 1)
        events.append({
            "event_type": "monthly", "ref_month": str(ref), "release_date": r.date,
            "board_date": r.date, "file_date": date_from_files(r.attachments, r.date),
            "date_source": "board listing",
            "title_month_ok": title_month(r.title) == ref.month,
            "release_time_kst": release_time(r.attachments), "issuer": "MOTIE",
            "title": r.title, "url": MOTIE_VIEW.format(r.article_id),
        })

    files = kcs_files.set_index("ntt_sn")["attachments"]
    for r in kcs.itertuples():
        month = parse_kcs_first20(r.title)
        if month is None:
            continue
        # KCS posts can lag the release: use the date in the file name when there is one
        file_date = date_from_files(files.get(r.ntt_sn, ""), r.date)
        release = file_date or r.date
        rel = pd.Timestamp(release)
        # A "days 1-20" release refers to the current month; a mismatch is flagged below
        events.append({
            "event_type": "first20", "ref_month": f"{rel.year}-{month:02d}", "release_date": release,
            "board_date": r.date, "file_date": file_date,
            "date_source": "attachment file name" if file_date else "board listing (unverified)",
            "title_month_ok": month == rel.month,
            "release_time_kst": None, "issuer": "KCS",
            "title": r.title, "url": KCS_VIEW.format(r.ntt_sn, r.ntt_key),
        })

    # Rule-based monthly dates for the extension sample, up to the first sourced monthly release
    first_sourced = min(e["release_date"] for e in events if e["event_type"] == "monthly")
    for release in pd.date_range(RULE_FIRST_RELEASE, first_sourced, freq="MS"):
        if str(release.date()) >= first_sourced[:8] + "01":
            break
        events.append({
            "event_type": "monthly", "ref_month": str(release.to_period("M") - 1),
            "release_date": str(release.date()), "board_date": None, "file_date": None,
            "date_source": "rule", "title_month_ok": True, "release_time_kst": None,
            "issuer": "MOTIE (rule-based date)", "title": None, "url": None,
        })

    if earnings is not None:
        events += earnings_events(earnings)

    cal = pd.DataFrame(events).sort_values(["event_type", "issuer", "release_date"]).reset_index(drop=True)
    rel = pd.to_datetime(cal["release_date"])
    ref = pd.to_datetime(cal["ref_month"])
    # Lag in months between reference month and release: 1 for monthly and earnings, 0 for first20
    cal["months_after_ref"] = (rel.dt.year - ref.dt.year) * 12 + rel.dt.month - ref.dt.month
    cal["weekday"] = rel.dt.day_name()
    return cal


def check(cal: pd.DataFrame) -> None:
    for kind, expected_lag in [("monthly", 1), ("first20", 0)]:
        c = cal[cal["event_type"] == kind]
        print(f"\n=== {kind}: {len(c)} releases, {c['release_date'].min()} -> {c['release_date'].max()}")
        dup = c[c.duplicated("ref_month", keep=False)]
        if len(dup):
            print("Several releases for the same month (kept all, to resolve by hand):")
            print(dup[["ref_month", "release_date", "title"]].to_string(index=False))
        span = pd.period_range(c["ref_month"].min(), c["ref_month"].max(), freq="M").astype(str)
        missing = sorted(set(span) - set(c["ref_month"]))
        print(f"Missing reference months: {missing or 'none'}")
        odd = c[(c["months_after_ref"] != expected_lag) | ~c["title_month_ok"].astype(bool)]
        print(f"Month in title inconsistent with release date: {len(odd)}")
        if len(odd):
            print(odd[["ref_month", "release_date", "title"]].to_string(index=False))
        print("Day of month of release:", c["release_date"].str[8:].value_counts().sort_index().to_dict())
        print("Weekday:", c["weekday"].value_counts().to_dict())
        print("Date source:", c["date_source"].value_counts().to_dict())
        has_file = c["file_date"].notna()
        disagree = c[has_file & (c["file_date"] != c["board_date"])]
        print(f"File-name date found: {has_file.sum()}; differs from board date: {len(disagree)}")
        if kind == "monthly" and len(disagree):
            print(disagree[["ref_month", "board_date", "file_date", "title"]].to_string(index=False))
        if kind == "monthly":
            print("Release time from file names:", c["release_time_kst"].value_counts(dropna=False).to_dict())

    e = cal[cal["event_type"] == "earnings"]
    for firm, c in e.groupby("issuer"):
        print(f"\n=== earnings, {firm}: {len(c)} releases, {c['release_date'].min()} -> {c['release_date'].max()}")
        span = pd.period_range(c["ref_quarter"].min(), c["ref_quarter"].max(), freq="Q").astype(str)
        print(f"Missing quarters: {sorted(set(span) - set(c['ref_quarter'])) or 'none'}")
        print("Duplicated quarters:", c.loc[c["ref_quarter"].duplicated(), "ref_quarter"].tolist() or "none")
        print("Months after quarter end:", c["months_after_ref"].value_counts().sort_index().to_dict())
        print("Day of month of release:", c["release_date"].str[8:].astype(int).describe()[["min", "50%", "max"]].to_dict())
        print("Weekday:", c["weekday"].value_counts().to_dict())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-scrape the boards")
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for path, scraper, name in [(MOTIE_RAW, scrape_motie, "MOTIE"), (KCS_RAW, scrape_kcs, "KCS")]:
        if path.exists() and not args.refresh:
            print(f"{name}: using cached {path.relative_to(ROOT)}")
        else:
            print(f"{name}: scraping ...")
            df = scraper()
            df["scraped_utc"] = stamp
            df.to_csv(path, index=False)

    kcs = pd.read_csv(KCS_RAW, dtype=str)
    if KCS_ATTACH_RAW.exists() and not args.refresh:
        print(f"KCS attachments: using cached {KCS_ATTACH_RAW.relative_to(ROOT)}")
    else:
        print("KCS attachments: scraping ...")
        att = scrape_kcs_attachments(kcs)
        att["scraped_utc"] = stamp
        att.to_csv(KCS_ATTACH_RAW, index=False)
    kcs_files = pd.read_csv(KCS_ATTACH_RAW, dtype=str, keep_default_na=False)
    motie = pd.read_csv(MOTIE_RAW, dtype=str, keep_default_na=False)
    earnings = None
    if EARNINGS_FILE.exists():
        earnings = pd.read_csv(EARNINGS_FILE, dtype={"first_release_rcept_no": str})
    else:
        print(f"Warning: {EARNINGS_FILE.relative_to(ROOT)} missing, no earnings events (run fetch_earnings.py)")
    cal = build(kcs, kcs_files, motie, earnings)
    check(cal)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    cal.to_csv(OUT_FILE, index=False)
    print(f"\nSaved: {OUT_FILE.relative_to(ROOT)} ({len(cal)} rows)")


if __name__ == "__main__":
    main()
