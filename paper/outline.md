# Research note: outline (validated by Zach on 2026-10-07)

**Title:** Chip Canary: Are Korea's Semiconductor Export Figures Already Priced In?
**Subtitle:** Release timing, earnings and market reactions, 2016-2026
**Length:** 5-6 pages, English. Appendix not counted.
**Wording rule:** the cautious formulations of the global summary in `CLAUDE.md` (2026-10-07).
"Descriptive" and "compatible with, not tested" are written as such.
**Writing split:** Zach writes sections 1 and 7; the other sections are drafted for Zach to review,
one at a time, in the order 2, 3, 4, 5, 6.

## Summary (5-6 lines, no jargon, at the top of the note; to be rewritten by Zach with the introduction)

To cover, in plain words: what the export figures are and why investors watch them; that they come
out weeks before the two companies' results and move very closely with them; that share prices move
only a little more than usual on publication days, apparently in response to the overall economic
news rather than to chips; and that whether investors had already absorbed this information remains
open, because ten years of quarterly data are not enough to tell.

**Style rule for all sections (Zach, 2026-10-07):** each section opens with one sentence in plain
language saying what it shows; each technical term is explained in a few words at its first
appearance (look-ahead bias, first release, event study, confidence interval, etc.). Readers include
non-specialists, such as professors from other disciplines.

## 1. Introduction (1/2 page, written by Zach)

- Korea publishes chip export figures weeks before Samsung and SK Hynix report earnings; they are
  watched as an early signal of the global chip cycle.
- The question is not whether exports predict earnings (partly mechanical) but whether they still
  carry news on the day each figure becomes public.
- Preview: a strong and early link, modest market reactions, an open answer on "priced in".

## 2. Data and the information calendar (1 page)

- Every figure is dated by its release date, not by the period it covers: this is what avoids
  look-ahead.
- Calendar of 540 events from three issuers, first-release chip figures from 120 customs releases,
  first-release earnings from 133 filings.
- Pitfalls found: board posting dates up to 6 days late, a site migration that erased pre-2016
  dates, a unit error in Samsung's filings, a table layout change in 2025.
- **Table 1:** sources, coverage, frequency, vintage.
- **Box 1, why the first release matters (Samsung 2016Q3):** first preliminary filing on 7 October
  2016, operating profit about KRW 7.8 trillion; revised guidance on 12 October 2016, about KRW 5.2
  trillion, after Samsung stopped sales, exchanges and production of the Galaxy Note 7 (Samsung
  Newsroom and CNBC, 12 October 2016, verified 2026-10-07); detailed results of 27 October 2016: 5.20.
- Section 2 cuts (validated 2026-10-07): cross-check in one sentence; calendar traps in appendix A1.

## 3. Who knows first? Exports versus earnings (1 1/4 pages)

- The first-20-days figure precedes the first earnings release by 35 days (SK Hynix) and 16 days
  (Samsung); Samsung's lead falls to 6 days from the monthly figure.
- Exports known at that date are very strongly correlated with earnings growth (r = 0.90-0.95);
  structural for SK Hynix (0.94 before 2023).
- For Samsung's revenue the link appears stronger during the AI boom (0.72 before 2023):
  descriptive. Expected gaps between firms and measures not confirmed.
- **Figure 1:** lead time per quarter (`paper/figures/fig1_lead_time.png`).
- **Figure 2:** exports vs earnings, four panels (`fig2_correlations.png`); first candidate for the
  appendix if space runs short (Table 2 then stays).
- **Table 2:** the four correlations, CIs, expected category, verdict.

## 4. Do markets react on release days? (1 1/4 pages)

- Method: event study, reaction relative to each stock's normal day on a rolling 250-day window,
  permutation tests, Holm over 22 tests.
- Release days are somewhat busier than normal days (1.2-1.6x), never "much stronger"; the
  monthly-release result for SK Hynix and the KOSPI depends on 31 July 2026.
- The first-20-days figure does not move markets more than the monthly one; SK Hynix does not react
  more than Samsung or the index. Compatible with, not tested: a reaction to the broad macro signal
  (all exports, other start-of-month releases such as PMIs) rather than to chips.
- The pre-2016 comparison is not interpretable (rule-based dates).
- **Figure 3:** reaction ratios (`fig3_reactions.png`).

## 5. Is the predictable part already priced in? (1/2 page)

- Test: does the earnings-day reaction depend on the part of earnings exports already predicted
  (expanding window, no look-ahead)?
- Compatible with "priced in", not informative: the slope rests on one or two quarters of 2026, the
  CI allows a sizeable effect.
- What would settle it: more quarters, intraday timing, analyst expectations.
- **Figure 4:** V2-5 scatter (`fig4_priced_in.png`).

## 6. Pre-registration and limitations (1/2 page)

- Expectations, thresholds and 32 specifications written before any result; the commit history
  shows the order.
- **Table 3, scorecard:** each expectation, verdict, CI.
- Limitations: revised ECOS figures for the monthly release; short sample dominated by 2026;
  excluded overlapping events; Yahoo prices.

## 7. Conclusion (1/4 page, written by Zach)

The four points of the global summary in `CLAUDE.md`.

## References (verified online on 2026-10-07)

- Andersen, T. G., Bollerslev, T., Diebold, F. X. and Vega, C. (2003). Micro Effects of Macro
  Announcements: Real-Time Price Discovery in Foreign Exchange. *American Economic Review*, 93(1),
  38-62. https://doi.org/10.1257/000282803321455151
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*,
  35(1), 13-39. https://EconPapers.repec.org/RePEc:aea:jeclit:v:35:y:1997:i:1:p:13-39

- Samsung Electronics (2016). [Update] Samsung Electronics Announces Revised Earnings Guidance for Q3
  2016. Samsung Global Newsroom, 12 October 2016.
  https://news.samsung.com/global/samsung-electronics-announces-earnings-guidance-for-q3-2016
- CNBC (2016). Samsung cuts $2.3 billion off its profit guidance due to Galaxy Note 7 crisis.
  12 October 2016. https://www.cnbc.com/2016/10/12/samsung-cuts-2-billion-off-its-profit-guidance-due-to-galaxy-note-7-crisis.html
- Bloomberg, republished by Infobae (2021). Korea's Exports Extend Recovery in January, Early Data
  Show. 21 January 2021. https://www.infobae.com/en/2021/01/21/koreas-exports-extend-recovery-in-january-early-data-show
  (source for the market practice: the first-20-days report is "closely watched as an early
  indicator of global trade"; a press report, not a study). The Korea Times article of 21 September
  2026 was checked and does not make this point.

## Closing line (end of the note)

Analysis in Python (pandas, statsmodels, plotly); code written with the help of Claude Code
(Anthropic). All data sources, scripts and the pre-registration log are in the project repository.

## Appendix (not counted)

All specifications, robustness checks, Holm-adjusted p-values, data construction details.
