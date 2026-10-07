# Research question

To be written by Zach **before** looking at any result. Do not edit sections 2 and 3 after the
analysis has started; add a dated note at the bottom instead.

Sections 2 and 3 were written by Zach in French on 2026-10-04 (answers to questions, without
suggested answers) and translated into English by Claude. Notes in italics are methodological
remarks added at the time of writing; they do not change the expectations.

## 1. The question (one sentence)

Is the information contained in Korea's semiconductor export data already priced in when it is
released?

## 2. What I expect to find (written on: 2026-10-04)

### Part 1 (information timing)

- **Lead time.** I am unsure: possibly a few days, but more likely a few weeks between the moment
  most of the quarter's exports are known and the earnings release. Caveat: knowing most of the
  quarter's exports is not knowing the total, whereas earnings include the whole quarter. Despite
  this, I expect the lead to be long enough for investors to have priced the information in before
  earnings are released. Low confidence.

  *Note: the last sentence implies no reaction, on earnings day, to the part of earnings
  predictable from exports. The current design does not test this (it only studies export release
  dates). Update 2026-10-04: now tested, earnings releases added as a third event type in part 2
  (see section 3).*

- **Predictive power.** Chip exports should track SK Hynix (almost only memory chips) better than
  Samsung, whose chips are only part of a business that also includes smartphones, TVs, home
  appliances and displays. Expected strength of the link: very strong for SK Hynix, medium for
  Samsung. The link should be stronger with revenue, since exports measure sales, than with
  operating profit, which also depends on costs: strong to very strong for revenue, medium to weak
  for operating profit.

  *Note: a very strong link with SK Hynix revenue is partly mechanical (Hynix sales are part of the
  exports) and would not by itself show informational value.*

- **Thresholds.**
  - Lead time, main definition: from the first-20-days release of the quarter's last month (around
    the 21st) to each firm's **first** earnings release (Samsung: preliminary earnings; SK Hynix:
    final results, its only release). Under 7 days: I was wrong. 7 to 14 days: intermediate.
    15 days or more: I was right. Other combinations (monthly release as starting point, final
    results as end point) are reported for comparison only.

    *Note: available from 2016Q2 (first first-20-days release: 2016-06-21); 2016Q4 has no
    first-20-days release for December. About 40 quarters. That SK Hynix publishes no preliminary
    earnings, and the timing of Samsung's preliminary earnings, are to be checked against OpenDART
    filing dates; if wrong, this definition may be revised with a dated note.*

    *Check (2026-10-04, OpenDART filings; definition unchanged): SK Hynix does file a
    "preliminary results" disclosure (unaudited), once per quarter around the 25th; it is its only
    release before the quarterly report, so its first release is that filing. Samsung files
    early-month guidance, then detailed results at the end of the month; its first release is the
    guidance.*
  - Correlation, computed on year-on-year growth rates (not levels, to avoid spurious correlation
    from trends): weak < 0.3; medium [0.3, 0.6); strong [0.6, 0.8); very strong >= 0.8. Classified
    on the point estimate; the 95% confidence interval is always reported, with a flag when it spans
    two categories.

  *Measure of operating profit (decided by Zach on 2026-10-04, before any result): the y/y growth of
  operating profit is not defined when it changes sign (27 SK Hynix quarters, e.g. 2012, 2023).
  For all quarters and both firms, "operating profit growth" in V1-2 and V1-3 is replaced by the y/y
  change in operating profit scaled by revenue of the same quarter a year earlier:
  (OP_t - OP_t-4) / Revenue_t-4. Revenue growth is unchanged. The correlation thresholds above apply
  as written. Expectations unchanged.*

### Part 2 (market reaction)

Two event types: (a) monthly export release (1st of the following month); (b) first-20-days release
(around the 21st, since June 2016). *(2026-10-04: a third type, (c) first earnings releases, was
added after these expectations were written; see section 3.)*

- **Day 21 vs day 1:** the first-20-days release should move the market more than the monthly
  release, because it already covers two thirds of the month and comes first. The monthly figure on
  the 1st brings less news.
- **Before vs after June 2016:** the reaction to the monthly release should have weakened. Before
  2016 it was the only source on the month; since then it comes after the 20-day figures, so it
  surprises less.
- **Who reacts most:** SK Hynix, then Samsung, then the KOSPI. The KOSPI still reacts somewhat,
  because Samsung and SK Hynix weigh heavily in it.
- **Size:** I cannot say on average, because it should depend mainly on the surprise. Figures in
  line with expectations: almost no reaction. Figures clearly off: a much stronger reaction than on
  a normal day. This can also happen on the monthly release, if the end of the month differs sharply
  from the first 20 days.

  *Notes: (1) testing the role of the surprise requires a surprise measure. For the monthly
  release, the 20-day chip figures would have to be extracted from the 121 KCS releases (not
  collected so far). For the 20-day release, no free expectation exists. (2) Pre-2016 dates are
  rule-based (hypothesis), and other changes after 2016 (AI boom, index weights) prevent attributing
  a change in reaction to the 20-day releases alone.*

- **Thresholds.** σ = standard deviation of daily abnormal returns on non-event days, computed
  separately for SK Hynix, Samsung and the KOSPI.
  - Almost no reaction: below 0.5σ. Much stronger than a normal day: above 2σ.
  - Two reactions differ if the gap between their mean reactions exceeds 0.5σ. Below that, they are
    "the same", provided the confidence interval of the gap is narrow enough to exclude 0.5σ.
  - Large surprise: the 20% of releases with the largest absolute surprise.

  *Point resolved by Zach (2026-10-04). Two measures:*
  - ***Main: absolute reaction** (absolute abnormal return, measurable now), as a ratio to the mean
    absolute reaction on a normal (non-event) day. Almost no reaction: ratio <= 1 (no more than a
    normal day). Much stronger: ratio >= 2. Two reactions differ if their gap is at least 0.5 times
    a normal day; below that they are "the same", with the confidence-interval condition above.*
  - ***Secondary: signed reaction** (abnormal return in the direction of the surprise), for the
    surprise hypothesis, if a surprise measure can be built. Thresholds as above: below 0.5σ, above
    2σ, gap of 0.5σ.*
  - *Why: with an absolute measure an ordinary day already averages about 0.8σ, so the σ thresholds
    only apply as written to a signed measure.*

## 3. What would prove me wrong

### Part 1

- **Lead time:** wrong if only a few days, rather than a few weeks, separate the moment most of the
  quarter's exports are known from the earnings release (under 7 days, see thresholds above).
- **Market reaction on earnings day:** I expect some movement in any case. Wrong if the move is
  clearly larger than usual, which would show the information had not yet been priced in.
  Additional hypothesis: the reaction is stronger when the delay between exports and earnings is
  short, weaker when it is long.

  *Note: not in the current design. Requires an event study around earnings dates, and enough
  variation in the delay across quarters.*

  *Update (2026-10-04, decided by Zach; expectations unchanged): earnings dates are now a third
  event type in part 2: each firm's first earnings release (Samsung preliminary earnings, SK Hynix
  final results), dates from OpenDART filings, same measures and thresholds as the export releases.
  Caveat for interpretation: earnings days carry much news unrelated to exports (margins,
  guidance, non-chip divisions), so a large earnings-day reaction alone does not show that the
  export information was not priced in. The direct test is whether the earnings-day reaction is
  related to the part of earnings that exports already predicted (see section 4). The additional
  hypothesis (stronger reaction when the delay is short) still depends on enough variation in the
  delay across quarters.*
- **Samsung vs SK Hynix:** wrong if the link is as strong or stronger for Samsung than for SK Hynix.
  Possible readings: chips weigh more in Samsung than I think, or Samsung's other businesses follow
  the same global cycle. The DS segment can separate the two.
- **Revenue vs operating profit:** wrong if operating profit tracks exports as well as or better than
  revenue. I doubt it, but it would show I am wrong.

### Part 2

- **Day 21 vs day 1:** wrong if reactions are about the same on the 21st and on the 1st, i.e. if the
  20-day figures do not move the market more than the monthly figure.
- **Before vs after 2016:** wrong if the reaction to the monthly figure is about the same after 2016,
  or stronger. It would mean it did not really lose its "monopoly".
- **Order SK Hynix, Samsung, KOSPI:** wrong if the order changes, e.g. Samsung reacts as much as
  SK Hynix, or the KOSPI as much as or more than the two firms.
- **Surprise:** wrong if even releases with large surprises do not move the stock more than a normal
  day. It would suggest the market does not really follow these figures. This would surprise me a
  lot.

  *Notes: (1) "about the same" follows the 0.5σ rule above: a non-significant difference is not
  evidence of equal reactions. (2) Large measured surprises without reaction can also mean the
  market already had the information from other sources (memory spot prices, company guidance):
  efficiency, not indifference.*

## 4. Specifications (pre-registered 2026-10-04, validated by Zach, before any result)

### 4.1 Common choices for all main specifications

| Choice | Main setting |
|---|---|
| Exports | ECOS semiconductor export value index (USD), year-on-year growth |
| Information known at date t | Only releases published before t, dated by `data/processed/release_calendar.csv` |
| Event window | [-1, +1] trading days (day 0 = first KRX trading day on or after the release) |
| Normal return | Constant mean over non-event days |
| Normal day (for the ratio) | Absolute CAR over random 3-day windows drawn from days with no event of any type |
| Inference | Permutation test against placebo event dates |
| Overlaps | An event is excluded if its window overlaps the window of an event of another type |

*Definition added on 2026-10-04 (validated by Zach, before any result): **exports known at t** in
part 1. At the main starting date t (first-20-days release of the quarter's last month T3), the
exports known are months T1 and T2 (ECOS y/y, revised series, the only one available) and the first
20 days of T3 (KCS y/y, first release). They are combined into one quarterly y/y growth, weighted by
each month's level a year earlier (ECOS index): g = sum(L_m,-12 * (1 + g_m)) / sum(L_m,-12) - 1.
A plain average of the three growth rates was considered and rejected: it gives a month with a low
base the same weight as a month with a high one. Built in `src/build_dataset.py`
(`exports_known_first20`); 39 quarters per firm (2016Q2 and 2016Q4 missing).*

### 4.2 Main specifications (32, of which 30 tested)

Part 1:

| ID | Specification | Count |
|---|---|---|
| V1-1 | Lead time in days (main definition, section 2), per firm. Descriptive, no test | 2 |
| V1-2 | Correlation of y/y growth: exports known at t vs the quarter's earnings released after t. SK Hynix revenue, SK Hynix operating profit, Samsung revenue, Samsung operating profit | 4 |
| V1-3 | Comparison of correlations (bootstrap CI): Hynix > Samsung (revenue, operating profit); revenue > operating profit (Hynix, Samsung) | 4 |

Horizon: main = the quarter whose earnings are released just after t; next quarters (h = 1, 2)
secondary.

Part 2 (stocks: SK Hynix, Samsung, KOSPI; absolute reaction measure):

| ID | Specification | Count |
|---|---|---|
| V2-1 | Reaction ratio by event type: (a) and (b) for the 3 stocks; (c) Samsung preliminary earnings for Samsung and KOSPI, SK Hynix results for SK Hynix and KOSPI | 10 |
| V2-2 | (b) vs (a), per stock, 2016-2026 | 3 |
| V2-3 | (a) before 2016 (rule-based dates) vs after, per stock | 3 |
| V2-4 | Order SK Hynix > Samsung > KOSPI, for (a) and (b), pairwise | 4 |
| V2-5 | Signed earnings-day reaction regressed on the part of earnings predicted by exports (from part 1). If already priced in: coefficient zero. Per firm | 2 |

### 4.3 Exploratory or conditional (reported, no strong conclusion)

| ID | Specification | Count |
|---|---|---|
| E-1 | Earnings-day reaction vs length of the delay, only if the delay varies enough | 2 |
| E-2 | Top 20% surprises vs others, signed reaction, (a) and (b) x 3 stocks, only if a surprise measure exists | 6 |
| E-3 | Before vs during the AI boom (2023+), descriptive | - |

### 4.4 Robustness (applied to each main specification, all counted and reported)

Window [0, +3]; market model with external benchmark (SOX, previous US session); with and without
2026-07-31; with and without the unverified 2016-09 event; overlapping windows included; UN Comtrade
instead of ECOS (2015-2025); earnings converted to USD (exchange-rate control).

### 4.5 Multiple testing

Holm correction, applied separately to each family of tested main specifications: part 1 (8 tests),
part 2 (22 tests). Headline results below are corrected **within their full family**, not as a
separate smaller family. A result that holds only in some robustness variants, or changes sign
across them, is reported as fragile.

### 4.6 Headline specifications for the body of the paper (chosen before any result)

The paper is 4-6 pages: the body reports these six specifications whatever their result; all the
others go to an appendix.

| # | ID | Specification | Why it is in the body |
|---|---|---|---|
| 1 | V1-1 | Lead time, SK Hynix and Samsung (one figure) | Answers "who knows first", the core of part 1 |
| 2 | V1-2 | Correlation, SK Hynix revenue | Purest chip exposure (risk 3 in `CLAUDE.md`); clearest test of the expectation |
| 3 | V2-1 | Reaction ratio, SK Hynix, event type (b) | Reaction to the earliest public export figure |
| 4 | V2-2 | (b) vs (a), SK Hynix | Tests the anticipation bias that motivated two event types |
| 5-6 | V2-5 | Priced-in test on earnings day, SK Hynix and Samsung | Direct answer to "already priced in?" |

Choosing SK Hynix for 2-4 is a choice of exposure (almost only chips), made before any result; the
same specifications for Samsung and the KOSPI are in the appendix.

### 4.7 Running log (one line per specification actually run)

| Date | Specification | Result kept? |
|---|---|---|
