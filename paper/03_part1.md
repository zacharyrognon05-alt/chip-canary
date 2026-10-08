# 3. Who knows first? Exports versus earnings

*Draft for Zach's review, 2026-10-08 (after the cutting pass). Figures from `outputs/v1_*` and `outputs/e3_*`; specifications
pre-registered in `QUESTION.md` (V1-1 to V1-3, E-3).*

*In plain terms: Korea's chip export figures are public several weeks before Samsung and SK Hynix
announce their results, and they move very closely with those results, for both companies.*

**Setting.** The information date t is the first-20-days release for the quarter's last month. At t the
market knows about eight ninths of the quarter's exports, combined into one year-on-year growth rate.
Earnings are each firm's first release; operating profit, which sometimes changes sign, enters as its
year-on-year change divided by revenue a year earlier. Sample: 2016Q3 to 2026Q2, 39 quarters per firm.

**The lead is weeks, not days.** Results follow the first-20-days figure by a median of 35 days for SK
Hynix and 16 days for Samsung (Figure 1), just above Samsung's *pre-registered* threshold of 15 days
(written down before any result, so the bar could not be moved). From the monthly release on the 1st,
Samsung's guidance follows after only 6 days.

**The link is very strong** (Table 2). The *correlation* (from -1 to 1, how closely two series move
together) between exports known at t and the results released two to five weeks later is 0.90 to 0.95,
*statistically significant* (very unlikely by chance) even after a *Holm correction*, which makes each
test stricter when many are run. The 95% *confidence interval*, the range of values compatible with the
data, is given by the standard formula (Fisher) and by a *block bootstrap*, a resampling method that
keeps consecutive quarters together.

**Table 2. Exports known at t and first-release earnings, 2016Q3-2026Q2 (n = 39 per cell)**

| Firm | Earnings measure | r | 95% CI (Fisher) | 95% CI (block bootstrap) | Expected | Outcome |
|---|---|---|---|---|---|---|
| SK Hynix | Revenue growth | 0.95 | 0.90 to 0.97 | 0.82 to 0.98 | very strong | as expected |
| SK Hynix | Operating profit change | 0.94 | 0.89 to 0.97 | 0.79 to 0.98 | medium or strong | stronger than expected |
| Samsung | Revenue growth | 0.90 | 0.81 to 0.95 | 0.65 to 0.94 | medium or strong | stronger than expected |
| Samsung | Operating profit change | 0.92 | 0.86 to 0.96 | 0.82 to 0.96 | weak or medium | stronger than expected |

*Categories: weak < 0.3, medium 0.3 to 0.6, strong 0.6 to 0.8, very strong 0.8 or more, fixed before the
results. For the second and third rows the bootstrap interval reaches "strong", so the outcome is
conclusive with the Fisher interval only.*

**No clear gap between firms or measures.** The link was expected to be weaker for Samsung, whose chips
are only part of the group, and for operating profit, which also depends on costs. Neither gap is
confirmed. A possible reading, not tested here: memory prices drive both sales and margins.

**Structural for SK Hynix; the AI boom may matter for Samsung.** Before 2023, SK Hynix's correlations
are unchanged (0.94), while Samsung's revenue correlation falls to 0.72 (95% CI 0.45 to 0.87). This is
*descriptive* (shown, not formally tested): the intervals overlap. Results are robust to other checks
(appendix A4).

**What this part does not show.** SK Hynix's sales largely are Korea's chip exports, so part of the link
is accounting, not forecasting. Whether exports tell the market anything new is the subject of
sections 4 and 5.

*Figure 1: `figures/fig1_lead_time.png`. Figure 2 (four panels): appendix A2.*
