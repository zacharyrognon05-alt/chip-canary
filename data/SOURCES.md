# Data sources

One entry per series. Dates are download dates (YYYY-MM-DD). Nothing is assumed: if a field is
unknown, it says so.

## Market prices (Yahoo Finance via `yfinance`)

Fetched by `src/fetch_markets.py`. Raw files in `data/raw/markets/`, download log in
`data/raw/markets/_manifest.csv`.

| Series | Ticker | Unit | Frequency | Downloaded |
|---|---|---|---|---|
| Samsung Electronics (common) | `005930.KS` | KRW per share | Daily (KRX trading days) | see manifest |
| SK Hynix | `000660.KS` | KRW per share | Daily (KRX trading days) | see manifest |
| KOSPI Composite | `^KS11` | Index points | Daily (KRX trading days) | see manifest |
| KRW per USD | `KRW=X` | KRW per USD | Daily, from 2003-12-01 | see manifest (2026-10-04) |
| PHLX Semiconductor index (SOX) | `^SOX` | Index points | Daily (US trading days), from 2000-01-03 | see manifest (2026-10-07); last row 2026-10-07 = incomplete session, not used |

Notes:
- Both `Close` (unadjusted) and `Adj Close` (split and dividend adjusted) are kept.
- Yahoo revises adjusted prices retroactively when new dividends are paid: re-downloading later
  can change `Adj Close`. The cached file is the reference for this project.
- `Close` is already split-adjusted by Yahoo (e.g. Samsung before its 50:1 split of 2018-05-04);
  only dividends separate `Close` from `Adj Close`.

Known issues in the snapshot of 2026-09-30 (raw files left untouched, handled in `build_dataset.py`):
- **SK Hynix `Adj Close` is negative before 2002-12-27.** Yahoo records a "dividend" of 12,600 KRW
  on that date while the share traded near 6,000 KRW: a data error. The 1:21 reverse split of
  2003-04-14 (capital reduction during the restructuring) comes with a trading halt just before it.
  Pre-2003 Hynix data are unusable as they stand.
- **Zero-volume rows with an unchanged price** (127 for Samsung, 140 for SK Hynix): mostly Korean
  holidays filled by Yahoo, plus a gap in February and March 2022 on ordinary trading days. These rows
  must be dropped before computing returns, otherwise they create artificial zero returns.
- Samsung is missing 2025-09-19; KOSPI is missing 2026-09-30 (not yet updated at download time).
- 2026-07-31: KOSPI +17.9%, Samsung +26.8%, SK Hynix +30.0%, after three days of sharp declines.
  Genuine (record KOSPI daily gain, confirmed in press coverage; not cross-checked against KRX files).
  Kept in the data; every market analysis is reported with and without this day.

Sample decisions:
- SK Hynix is used from 2003-04-14 (first session after the 1:21 reverse split); first daily return
  on 2003-04-15.
- Files in `data/raw/markets/` are not committed (Yahoo data redistribution). Snapshot used in this
  project: downloaded 2026-09-30 21:21 UTC. Re-running `fetch_markets.py` later may give slightly
  different `Adj Close` values.

## Analysis datasets (built by `src/build_dataset.py`, 2026-10-04)

No estimation, only assembly. All in `data/processed/` (regenerated, not committed).

| File | Content |
|---|---|
| `daily_returns.csv` | Simple daily returns (Adj Close) of Samsung, SK Hynix, KOSPI on KRX trading days; `extreme_day` flags 2026-07-31 |
| `events.csv` | The 540 calendar events, each with `event_day` (first KRX trading day on or after the release date) and flags `main_sample`, `rule_based_date`, `unverified_date` |
| `quarterly.csv` | Part 1, one row per firm and quarter (133): dates of the information timeline, exports known at each date, first-release earnings growth, KRW/USD, lead times in days |

Construction rules:
- KRX trading days: days where any of the three series has positive volume (stock files contain
  Yahoo-filled holidays with zero volume; the KOSPI file lacks 2026-09-30). 6,587 days.
- A stock day with zero volume on a trading day (Samsung: 29 days, incl. 2022-01-26 to 2022-03-17)
  is bad data: its return and the next day's return are missing, never zero. SK Hynix returns start
  on 2003-04-15.
- Event day: release on a non-trading day moves to the next trading day (up to 9 days for the
  Chuseok closure of October 2017).
- `exports_known_first20` (exports known at the main starting date t, the first-20-days release of
  the quarter's last month T3): ECOS y/y for T1 and T2 (revised series), first-20-days y/y for T3
  (first release), combined with prior-year ECOS levels as weights. Missing for 2016Q2 (no chip
  figure in the June 2016 release) and 2016Q4 (no December 2016 release): 39 quarters per firm.
- `revenue_yoy_first`: first-release revenue over the same quarter a year earlier as stated in the
  same filing (max gap with the published y/y: 0.46 pp). `op_change_scaled_first`:
  (OP - OP a year earlier) / revenue a year earlier (decision of 2026-10-04).

## Semiconductor exports (ECOS, Bank of Korea)

Manual download from https://ecos.bok.or.kr into `data/raw/ecos/`, read by `src/load_ecos.py`.

| Field | Value |
|---|---|
| Raw file | `data/raw/ecos/Export Value Indices_02183427.csv` (unmodified ECOS CSV export) |
| Table | 3.3.1.1.1 Export Value Indices |
| Item | Semi-conductors |
| ECOS path | 3. Exchange Rate/International Reserves and Trade > 3.3 Trade/Terms of Trade indices > 3.3.1 Trade Value and Volume Indices > 3.3.1.1 Export Value and Volume Indices > 3.3.1.1.1 Export Value Indices |
| Series code | Not included in the CSV export: to be recorded from the ECOS site |
| Unit | Index, 2020 = 100 (checked: the 2020 monthly mean is 100.00) |
| Currency basis | Not stated in the file. Very likely USD: its y/y growth tracks Comtrade in USD (mean gap 2.8 pp) much better than Comtrade converted to KRW (5.6 pp). Inference, still to confirm in the ECOS series notes |
| Frequency | Monthly, original (not seasonally adjusted) data |
| Announced coverage | 1988-01 to 2026-08 |
| **Actual coverage** | **2000-01 to 2026-08** (320 months, no gap). Cells before 2000-01 are empty in the export. |
| Provisional values | 2026-01 to 2026-08, flagged "p)" by ECOS, kept as a `provisional` column |
| ECOS update | 2026-09-15 |
| Downloaded | 2026-10-02 |
| Processed file | `data/processed/ecos_semis_export_value_index.csv` |

Notes:
- **Cross-check against UN Comtrade HS 8542** (`notebooks/check_ecos_vs_comtrade.py`, 2014-01 to
  2025-12, 144 months of y/y growth): correlation 0.992, mean absolute gap 2.8 pp, no lead or lag,
  opposite signs in 4 months only, all within 2.5 pp of zero. This **validates our processing of the
  ECOS file** (no error of unit, date or shift). It is **not an independent confirmation** of the data:
  both series come from Korean customs declarations.
- This is the **latest vintage** (revised series), not the first release the market saw. Not suitable
  as is to measure a "surprise" on the release date.
- The 2026-08 value was available on 2026-09-15 at the latest, i.e. about two weeks after the
  customs release of the 1st of the month: the ECOS index is not the earliest public source.

## Korea Customs Service press release titles (search for a "first 20 days" series)

`data/raw/kcs/kcs_press_titles_2014-05_2017-11.csv`: date, title and post IDs of the 1,290 press
releases posted on the KCS press board (https://www.customs.go.kr, board 보도자료, `bbsId=1362`)
between 2014-05-19 and 2017-11-14. Scraped 2026-10-02 from the board listing pages (one-off check,
script not kept). Used only to establish that the first "1-20 days" release on the board is dated
2016-06-21. See the decision of 2026-10-02 in `CLAUDE.md`.

## Release calendar (event dates for part 2)

Built by `src/fetch_release_calendar.py` (scraped 2026-10-02). Output:
`data/processed/release_calendar.csv`, one row per release.

| Raw file | Source | Content |
|---|---|---|
| `data/raw/calendar/motie_trade_titles.csv` | MOTIE (now MOTIR) press board, https://www.motir.go.kr/kor/article/ATCL3f49a5a8c, searches "수출입 동향" and "수출입동향" | Date, title, article id, attachment names |
| `data/raw/calendar/kcs_press_titles.csv` | KCS press board (보도자료, `bbsId=1362`), 2016-05 → 2026-10 | Date, title, post ids |
| `data/raw/calendar/kcs_first20_attachments.csv` | KCS post pages of each "1-20 days" release | Attachment names |
| `data/processed/earnings.csv` (from `src/fetch_earnings.py`) | OpenDART filing dates | First earnings release of each quarter, Samsung and SK Hynix (event type `earnings`) |

Columns of the calendar: `event_type` (`monthly` / `first20` / `earnings`), `ref_quarter` (earnings only; `ref_month` is then the quarter's last month), `ref_month`, `release_date` (date
used), `board_date`, `file_date` (date at the start of an attachment name, if any), `date_source`,
`release_time_kst` (from MOTIE file names, often missing), `issuer`, `title`, `url`.

Known limits:
- Monthly releases: dated from the board, reliable from 2016-01 only (older posts carry the
  migration date 2016-12-09).
- First-20-days releases: the KCS board date is a posting date that can lag the release by up to
  6 days; the file-name date is used when present (104 of 121). 2016-09 (board date 2016-09-22) is
  unverified.
- No first-20-days release on the board for 2016-12, 2017-10 and 2017-11.
- Earnings events: date = DART filing date of the first preliminary-results filing (Samsung
  2010-01-07 -> 2026-07-07, 67 releases; SK Hynix 2010-04-22 -> 2026-07-29, 66), no missing quarter.
  Time of day not recorded: a filing after the market close (15:30 KST) would belong to the next
  trading day (to check with IR notices).

## First-20-days chip export growth (KCS press releases, first release)

Extracted by `src/extract_kcs_first20.py` from the attachments of the 121 "1-20 days" releases of
the calendar (downloaded 2026-10-04 into `data/raw/kcs_releases/`, not committed: ~50 MB, public
documents, re-downloadable). Output: `data/processed/kcs_first20_semis.csv`.

| Field | Value |
|---|---|
| Variable | `chip_export_yoy_pct`: y/y growth (%) of semiconductor (반도체) exports, days 1-20 of the month vs the same days a year earlier, as written in the export "(주요품목)" passage |
| Vintage | **First release**, as published on the release date (not revised) |
| Coverage | 2016-07 to 2026-09, 120 of 121 releases |
| Missing | 2016-06: the first release gives only "전자집적회로" (integrated circuits, HS 8542, -9.1%), a narrower item; left missing rather than mixing definitions |
| Formats read | HWP 5 (binary), HWPX (zip/XML), PDF |

Checks (2026-10-04):
- Pilot on 5 releases of different formats and years before the full run.
- The 35 releases available in several formats give the same figure in every format.
- The export passage is the first "(주요품목)" passage, before the import section (Korea also
  imports chips: the second passage is not used).
- Confirmed against press articles of the time: 2019-03 (-25.0%), 2023-12 (19.2%), 2024-01 (19.7%),
  2026-01 (70.2%), 2026-05 (202.1%), 2026-06 (188.4%), 2026-07 (180.6%), 2026-09 (259.4%).
- Against the full-month ECOS y/y: correlation 0.977, median gap 6.5 pp, same sign in 94% of
  months. Large gaps (e.g. 2024-01: 19.7 vs 55.5) are genuine differences between the first 20 days
  and the full month, not extraction errors.

Limits:
- Raw y/y growth, not adjusted for working days: holidays (Lunar New Year, Chuseok) falling in the
  20-day window one year and not the other distort the figure. The releases also give working-day
  adjusted totals, not extracted.
- The June 2016 release already tabulates 20-day totals for March-May 2016: such figures existed
  before 2016-06-21, but no release for them was found on the KCS board.

## Monthly chip export growth, first release (MOTIE): not extracted

Pilot on 4 MOTIE monthly releases (2015-12, 2018-06, 2020-03, 2023-12; 2026-09 not downloaded: the
server closed the connection), 2026-10-04: a targeted pattern gives the right figure for 2 of 4 only.
Releases are long (40,000-60,000 characters), mix monthly, quarterly and annual figures, and their
tables change structure across years. KCS monthly provisional releases ("잠정치", 2016-09+) give
totals only, no chip line.

**Decision (Zach, 2026-10-04): the monthly chip figure comes from ECOS (revised series).** Limits, to
be stated in the paper:
- the surprise of the monthly release (E-2) compares a first-release 20-day figure (KCS) with a
  revised full-month figure (ECOS), not with the figure the market saw on the 1st;
- the two items are not strictly the same: KCS "반도체" vs the ECOS "Semi-conductors" index item
  (exact scopes not documented in the files).

## Korean exports of HS 8542 (UN Comtrade)

Fetched by `src/fetch_comtrade.py` via the Comtrade API v1 (`/data/v1/get/C/M/HS`, key in `.env`).
Raw JSON per year in `data/raw/comtrade/` (not committed: redistribution terms not checked),
processed file `data/processed/comtrade_kor_hs8542_exports.csv`.

| Field | Value |
|---|---|
| Reporter / partner / flow | Republic of Korea (410) / World (0) / exports (X) |
| Commodity | HS 8542, electronic integrated circuits (includes memory, 8542.32) |
| Unit | Current USD (`primaryValue`, FOB) |
| Frequency | Monthly |
| Coverage | **2013-01 to 2025-12** (156 months, no gap). Comtrade has no Korean monthly data before 2013 (availability endpoint, checked 2026-10-02); 2026 not yet published |
| HS versions | H4 2013-2016, H5 2017-2021, H6 2022-2025 |
| Aggregation | `isReported = False`: the 4-digit total is aggregated by Comtrade from finer codes |
| Downloaded | 2026-10-02 |

Notes:
- Not an independent source: like ECOS, it comes from Korean customs declarations. It checks the
  ECOS series and is reproducible by script, but it cannot confirm the underlying customs data.
- Narrower scope than the ECOS "Semi-conductors" item (exact ECOS scope unknown). The ratio Comtrade
  / ECOS moves between 0.068 and 0.073 USD bn per index point over 2013-2025.
- Cross-check script: `notebooks/check_ecos_vs_comtrade.py`.

## Quarterly earnings (OpenDART)

Fetched by `src/fetch_earnings.py` (2026-10-04, key in `.env`, e-mail registration only). Raw API
answers in `data/raw/dart/` (not committed), output `data/processed/earnings.csv`, one row per firm
and quarter. corp_code: Samsung Electronics 00126380, SK Hynix 00164779 (from `corpCode.xml`).

| Source | API | Coverage | Content |
|---|---|---|---|
| First release: "연결재무제표기준영업(잠정)실적(공정공시)" filings (before 2011 also "영업(잠정)실적(공정공시)") | `list.json` (dates), `document.xml` (table) | Samsung 2009Q4-2026Q2 (67 quarters), SK Hynix 2010Q1-2026Q2 (66), from filings of 2010 onwards | Revenue and operating profit of the quarter and of the same quarter a year earlier, y/y change as published; filing date (`first_release_date`) |
| Final figures: quarterly and annual reports | `fnlttSinglAcnt.json` | 2016Q1-2026Q2 (42 quarters per firm) | Consolidated revenue and operating profit; Q4 = annual minus 9 months |

Release pattern (from the filings):
- **Samsung** files two preliminary results per quarter: early-month guidance (revenue and operating
  profit, rounded to 0.01 trillion KRW), then detailed results at the end of the month. The first
  filing is the first release.
- **SK Hynix** files one preliminary-results filing per quarter (around the 25th, unaudited): its
  only release before the quarterly report.

Checks and corrections:
- First release vs final figure (2016Q1-2026Q2): revenue gap median 0.75% (Samsung, rounded
  guidance), 0.00% (SK Hynix). Largest: Samsung 2016Q3, 2.5%.
- **Unit error in Samsung's filings 2010-2016**: they declare "백만원" while the figures are in
  trillion KRW (e.g. revenue "57.00" for 2013Q2). Corrected by a plausibility rule (quarterly revenue
  between 1 and 500 trillion KRW) in 29 quarters, flagged in `unit_corrected`.
- **Older title**: until 2010 the first release was filed as "영업(잠정)실적(공정공시)", without
  "consolidated" in the title (4 quarters per firm, 2009Q4-2010Q4, before K-IFRS consolidation in
  2011): figures possibly on another basis, flagged in `first_release_consolidated = False`.
- SK Hynix 2020Q3 released late (2020-11-04): confirmed by its IR notice of 2020-10-15 (results
  call on 2020-11-04 09:00). IR notices give the release time; not extracted yet.
- **Amendments** (`amendment_dates`): almost always filed on a release day (routine). Two exceptions,
  separate news events: Samsung 2016Q3 (first release 2016-10-07: operating profit 7.80 trillion
  KRW; amendment filed 2016-10-12 (not retrievable from OpenDART, API status 014), which is the
  revised guidance of about 5.2 trillion KRW announced that day after Samsung stopped the Galaxy Note 7
  (Samsung Newsroom and CNBC, 12 October 2016, verified 2026-10-07); detailed
  results 2016-10-27: 5.20 trillion KRW; checked 2026-10-07), SK Hynix 2022Q4 (amendment
  2023-02-23, content not checked).
- OpenDART has no quarterly key accounts for 2015 (only the annual report): Q4 2015 cannot be
  derived; final quarterly figures start in 2016Q1.
- The y/y change of operating profit is not defined when it changes sign: SK Hynix 16 quarters,
  Samsung 1 (counted on first-release figures, 2026-10-07). The published y/y cells are missing more
  often (SK Hynix: 29 for operating profit, 16 for revenue) and are not used: growth is recomputed
  from the amounts. *(Corrected 2026-10-07: an earlier version said 27 quarters, a count that mixed
  sign changes with a parsing bug.)*
- **Two table layouts**: from 2025Q3, filings add a sign-change column after each % column (7 cells
  instead of 5). Until 2026-10-07 the script read the old layout only, so the prior-year figures of
  2025Q3-2026Q2 were missing; fixed, and a check now lists quarters without a prior-year figure.
- No segment data: Samsung's DS division is not in OpenDART (manual entry from IR releases, to do).
