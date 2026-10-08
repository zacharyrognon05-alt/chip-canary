# Appendix

*Draft, 2026-10-08. A1 and A6 below; tables A2 to A5 (all specifications, robustness, Holm-adjusted
p-values, exploratory specifications) are generated from the result files in `appendix_tables.md`
by `src/appendix_tables.py`.*

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
