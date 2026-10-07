# Appendix

*Draft, 2026-10-07. Sections to be completed: all specifications, robustness, Holm-adjusted p-values.*

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
