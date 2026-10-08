# Appendix

*Draft, 2026-10-08. A1 and A6 below; tables A2 to A5 (all specifications, robustness, Holm-adjusted
p-values, exploratory specifications) are generated from the result files in `appendix_tables.md`
by `src/appendix_tables.py`.*

## A0. Data sources (full table)

| Series | Source | Frequency | Coverage used | Version |
|---|---|---|---|---|
| Chip exports, first 20 days of the month (y/y %) | KCS press releases | Monthly, ~21st | 2016-07 to 2026-09 (120 releases) | First release |
| Release dates, full-month exports | MOTIE press releases | Monthly, 1st | 2016-01 to 2026-10 (130); 2003-2015 by rule | Dates only |
| Chip export value index (2020 = 100, USD) | Bank of Korea, ECOS | Monthly | 2000-01 to 2026-08 | Revised (2026 provisional) |
| Revenue and operating profit | OpenDART preliminary filings | Quarterly | Samsung 2009Q4, SK Hynix 2010Q1, to 2026Q2 | First release |
| Revenue and operating profit, final | OpenDART quarterly reports | Quarterly | 2016Q1 to 2026Q2 | Final |
| Exports of integrated circuits (HS 8542) | UN Comtrade | Monthly | 2013-01 to 2025-12 | Revised (cross-check) |
| Prices: Samsung, SK Hynix, KOSPI | Yahoo Finance | Daily | 2000 to 2026-09-30 (SK Hynix from 2003-04-15) | Adjusted |
| KRW/USD, SOX index | Yahoo Finance | Daily | 2003-12 / 2000 to 2026-09 | Robustness only |

*Download dates and series codes are in the project's `data/SOURCES.md`.*

**Checks of the rebuilt first-20-days series.** The semiconductor export growth of the first 20 days
was extracted from the attachments (HWP, HWPX and PDF files) of 120 of the 121 customs releases; the
June 2016 release gives only integrated circuits and is left missing. The 35 releases published in
several formats give the same figure in each, eight values match press reports of the time, and the
series follows the full-month ECOS growth closely (correlation 0.977).

**Cross-check of the ECOS index.** Year-on-year growth of the ECOS index tracks UN Comtrade exports of
integrated circuits (HS 8542, the customs code for integrated circuits, 2013 to 2025) with a
correlation of 0.992, which validates its processing (not the underlying customs data, common to both)
and indicates that it is in US dollars, while earnings are in won.

## A1. Building the release calendar: traps found

- **Posting lag (KCS).** The KCS website shows the date a release was posted, which can lag the
  actual release by up to six days (figures for 1 to 20 May 2026: released on 21 May, posted on
  27 May, confirmed by press reports). 104 of the 121 first-20-days releases are dated by the date
  written at the start of their attachment file names; the other 17 keep the posting date, 16 of
  which fall on the expected trading day (one unverified case, September 2016).
- **Site migration (MOTIE).** The MOTIE website shows 9 December 2016 for every release before 2016.
  Monthly dates before 2016 are therefore set by rule (first day of the month); on 2016-2026 the rule
  falls on the right trading day for all 129 sourced releases with price data.
- **Unit error (Samsung filings).** Samsung's preliminary filings of 2010 to 2016 state "millions of
  won" while the figures are in trillions of won (e.g. revenue "57.00" for 2013Q2); corrected by a
  plausibility rule in 29 quarters and flagged.
- **Layout change (filings from 2025Q3).** Preliminary filings add a sign-change column after each
  percentage column; the prior-year figures of 2025Q3 to 2026Q2 were first misread, detected from the
  sample size and corrected before any interpretation.
- **Overlaps.** SK Hynix releases its results around the 25th, often one or two trading days after
  the first-20-days release: 13 of its 42 earnings events of 2016-2026 overlap and are excluded from
  the main specification.

## A6. Definitions and construction

- **Exports known at date t** (part 1). t is the first-20-days release of the quarter's last month.
  Known at t: full-month year-on-year growth of months 1 and 2 (ECOS index, revised series) and of the
  first 20 days of month 3 (KCS, first release). Quarterly growth = sum over the three months of
  (level a year earlier x (1 + growth)) / sum of levels a year earlier - 1.
- **Earnings measures** (first release). Revenue: year-on-year growth. Operating profit: (OP of the
  quarter - OP of the same quarter a year earlier) / revenue of the same quarter a year earlier,
  because operating profit changes sign in 16 SK Hynix quarters and 1 Samsung quarter.
- **Lead time** (V1-1). Calendar days from t to each firm's first earnings release.
- **Trading days.** Days on which any of the three series (Samsung, SK Hynix, KOSPI) has positive
  volume. A stock day with zero volume on a trading day is treated as missing (Samsung: 29 days, incl.
  26 January to 17 March 2022); the return of that day and of the next one is left out.
- **Reaction ratio** (part 2). For each event and stock: estimation window = the 250 trading days
  before the event window, excluding the windows of all events; normal return = mean over that window;
  abnormal return = return - normal return; CAR = sum of abnormal returns from the day before to the
  day after the release (main window); ordinary day = mean absolute CAR over all 3-day windows of the
  estimation window without any event; ratio = absolute CAR / ordinary day.
- **Inference.** Reaction levels: permutation against random ordinary windows of each event's
  estimation period (5,000 draws). Gaps between groups: permutation of group labels. Gaps between
  stocks on the same events: random sign flips. 95% intervals by bootstrap over events (5,000 draws).
  Fixed random seed, so a re-run gives identical figures.
- **Priced-in test** (V2-5). Predicted part = fit of operating profit change on exports known at t,
  estimated each quarter only on quarters whose results were already public (expanding window, 8
  quarters minimum); signed reaction = CAR / ordinary day on the firm's first earnings release; slope
  by ordinary least squares, p-value by permutation of the predicted parts.
- **Multiple testing.** Holm correction within each part: 8 tests (part 1), 22 tests (part 2).

## Figure A1. Exports known at t and earnings, four panels

Figure A1: `figures/figA1_correlations.png` (moved from section 3 in the cutting pass of 2026-10-08,
formerly Figure 2; renumbered 2026-10-08).
The full tables of part 1 are in `appendix_tables.md` (A2).

## A4 (text). Robustness, in words

- **Part 1.** The correlations are robust to converting earnings into US dollars (changes below 0.03).
  Replacing ECOS by UN Comtrade data lowers them to 0.79 to 0.89, mostly because Comtrade ends in 2025
  and misses the two most extreme quarters of 2026; on the same quarters, the source itself changes the
  correlations by about 0.02.
- **Part 2.** The conclusions on export releases hold when the reaction window is lengthened to four
  days (from the release day to three days after), when the release of September 2016 (whose date could
  not be verified) is dropped, and when overlapping releases are kept. Earnings results are less robust:
  with the four-day window, almost all SK Hynix earnings releases overlap with the first-20-days figure
  and cannot be measured, and Samsung's earnings reaction is no longer significant after Holm.
- **Priced-in test (section 5), diagnostics.** For SK Hynix, the second quarter of 2026 has a predicted
  part far above all others, and its results release of 29 July 2026 fell in the turbulent days before
  the record session of 31 July, with an abnormal return of about -33% over three days; without that
  quarter the slope is -0.07. For Samsung the sign of the slope depends on the first or the second
  quarter of 2026. The confidence intervals cannot exclude an effect of up to 1.6 ordinary days (SK
  Hynix) and 1.1 ordinary days (Samsung) for a typical difference (one standard deviation) in the
  predicted part. The conclusion does not change with revenue instead of operating profit, with UN
  Comtrade exports, or with earnings in US dollars.

## A7. Other limitations

- *Excluded events.* Releases whose windows overlap are left out, which removes a third of SK Hynix's
  results releases.
- *Daily data.* Without the time of day of each release, reactions are measured over three days.
- *Unadjusted 20-day figures.* Holidays such as the Lunar New Year shift working days between years and
  distort some first-20-days growth rates.
- *Prices.* Yahoo Finance data, adjusted for dividends and splits, cannot be redistributed; a
  re-download may give slightly different adjusted prices.
