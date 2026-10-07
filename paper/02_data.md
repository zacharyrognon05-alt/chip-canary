# 2. Data and the information calendar

*Draft for Zach's review, 2026-10-07. Figures from `data/SOURCES.md` and the project outputs.*

The note rests on one rule: every figure is dated by the day it became public, not by the period it
describes. A chip export figure for March is information about March, but the market only knows it
from its release date onwards. Dating data by the period covered would let the analysis use
information that nobody had at the time, a look-ahead bias that would flatter any "leading
indicator". The work behind this note is therefore mostly a calendar: when each number was
released, by whom, and in which version.

**Sources.** Market participants follow these releases as an early signal: the first-20-days report is
"closely watched as an early indicator of global trade" (Bloomberg, republished by Infobae, 21 January
2021). Table 1 lists the series. Exports come from three publications. The Korea Customs
Service (KCS) releases exports for the first 20 days of each month, usually on the 21st; this release
started on 21 June 2016. The trade ministry (MOTIE) releases the full month on the first day of the
following month. The Bank of Korea's ECOS database provides a monthly export value index for
semiconductors since January 2000, in a revised version. Earnings come from the electronic disclosure
system OpenDART: for each quarter, the first preliminary results filing of Samsung Electronics
(early-month guidance) and of SK Hynix (around the 25th, its only release before the quarterly
report). Daily prices of both firms and of the KOSPI come from Yahoo Finance.

**First release, not revised data.** Where possible, the note uses the figure as first published. The
semiconductor export growth of the first 20 days was extracted from the attachments of 120 of the 121
KCS releases (HWP, HWPX and PDF files); the June 2016 release gives only integrated circuits and is
left missing. The extraction was checked in three ways: the 35 releases published in several formats
give the same figure in each, eight values match press reports of the time, and the series follows
the full-month ECOS growth closely (correlation 0.977). Earnings growth is taken from the first
preliminary filing, which states the same quarter a year earlier. The full-month export figure is the
exception: the MOTIE releases could not be parsed reliably, so the revised ECOS index is used instead.
Box 1 shows why the distinction matters.

**The calendar.** The release calendar holds 540 events: 130 monthly releases (January 2016 to
October 2026), 121 first-20-days releases, and 133 first earnings releases of the two firms. Each date
comes from the issuer, never from a rule, with one exception: monthly dates before 2016 cannot be
sourced, and an extension sample (2003 to 2015) sets them to the first day of the month; results on
that sample are reported separately. A release on a weekend or holiday is assigned to the next
trading day. Building the calendar exposed several traps (posting dates up to six days late, a site
migration, a unit error and a layout change in company filings), described in the appendix.

**Cross-check.** Year-on-year growth of the ECOS index tracks UN Comtrade exports of integrated circuits
(HS 8542, 2013 to 2025) with a correlation of 0.992, which validates its processing (not the
underlying customs data, common to both) and indicates that it is in US dollars, while earnings are
in won.

> **Box 1. Why the first release matters: Samsung, third quarter of 2016.**
> On 7 October 2016, Samsung's first preliminary filing put third-quarter operating profit at about KRW
> 7.8 trillion. On 12 October 2016, after stopping sales, exchanges and production of the Galaxy Note 7,
> Samsung issued a revised guidance of about KRW 5.2 trillion (Samsung Newsroom, 12 October 2016; CNBC,
> 12 October 2016); the detailed results of 27 October 2016 confirmed KRW 5.20 trillion. A revised
> series records only 5.2, while from 7 to 12 October the market knew only 7.8. A study using revised data would
> date the bad news wrongly.

**Table 1. Data sources**

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

*Main sample of the analysis: 2016 to 2026, sourced dates only. Download dates and series codes are
in the project's `data/SOURCES.md`.*
