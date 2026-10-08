# 5. Is the predictable part already priced in?

*Draft for Zach's review, 2026-10-08 (after the cutting pass). Figures from `outputs/v2_main.csv` and `outputs/v2_robustness.csv`;
specification pre-registered in `QUESTION.md` (V2-5).*

*In plain terms: if investors had already used the export figures, share prices should not react on
results day to the part of the results those figures announced; the data are compatible with this,
but they are too few to prove it.*

**The test.** If the part of results that exports announced was *priced in* (already in the share price),
the reaction on results day should not depend on it. This predicted part comes from a *regression* (a
line fitted between export growth and operating profit) on an *expanding window*, using only quarters
already public, to avoid look-ahead. The test asks whether the signed reaction rises with it.

**Compatible with "priced in", but not informative.** Neither slope differs significantly from zero
(Figure 3): -1.90 for SK Hynix (95% CI -2.71 to +1.74, 22 quarters), -1.96 for Samsung (-7.09 to +6.18,
31 quarters). But SK Hynix's slope rests on one quarter, 2026Q2 (without it, -0.07), and Samsung's sign
depends on 2026 (diagnostics, appendix A4). With such wide intervals, the data fit both a market that
had priced the information in and one that still reacted strongly to it.

**What would settle it:** more quarters, release times, and analysts' forecasts, to measure the
*surprise* relative to expectations (Andersen, Bollerslev, Diebold and Vega, 2003); such forecasts are
commercial and were not available.

*Figure 3: `figures/fig3_priced_in.png`.*
