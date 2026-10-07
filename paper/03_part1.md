# 3. Who knows first? Exports versus earnings

*Draft for Zach's review, 2026-10-07. Figures from `outputs/v1_*` and `outputs/e3_*`; specifications
pre-registered in `QUESTION.md` (V1-1 to V1-3, E-3).*

*In plain terms: Korea's chip export figures are public several weeks before Samsung and SK Hynix
announce their results, and they move very closely with those results, for both companies.*

**Setting.** For each quarter, the information date t is the release of the first-20-days figure for
the quarter's last month (around the 21st of March, June, September or December). At that date, the
market knows the full-month exports of the first two months and the first 20 days of the third: about
eight ninths of the quarter. These three figures are combined into one quarterly year-on-year growth
rate, each month weighted by its level a year earlier (so that bigger months count more). On the earnings side, the note uses each firm's
first release: Samsung's early-month guidance, and SK Hynix's single preliminary filing. Revenue enters
as year-on-year growth. Operating profit changes sign in 16 SK Hynix quarters, where a growth rate is
meaningless, so it enters as the year-on-year change in operating profit divided by revenue of the
same quarter a year earlier. The sample runs from 2016Q3 to 2026Q2 (39 quarters per firm; 2016Q4 has no
December first-20-days release).

**The lead is weeks, not days.** The first earnings release follows the first-20-days figure by a
median of 35 days for SK Hynix (range 31 to 44) and 16 days for Samsung (range 14 to 22) (Figure 1).
For SK Hynix the lead is long in every quarter. For Samsung it is just above the threshold of 15 days, which was
*pre-registered* (written down before any result was computed, to avoid adjusting the bar after the
fact), and it depends on the starting point: measured from the monthly release on the
1st, Samsung's guidance arrives a median of 6 days later, below the 7-day threshold. The lead barely
varies across quarters, because it is set by fixed publication calendars rather than by events.

**The link is very strong.** Exports known at t are very strongly correlated with the earnings released
two to five weeks later, for both firms and both measures (Table 2, Figure 2). The correlations range
from 0.90 to 0.95. All four are *statistically significant* (very unlikely to arise by chance), even
after a *Holm correction*, a standard adjustment that makes each test stricter when several tests are
run, so that some do not come out positive by luck alone. Each correlation comes with a 95%
*confidence interval*, the range of values compatible with the data. The table gives two versions:
the standard formula (Fisher) and a *block bootstrap*, a resampling method that keeps consecutive
quarters together because growth rates persist from one quarter to the next. The bootstrap intervals
are wider but stay mostly within the "very strong" range.

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

**No clear gap between firms or measures.** The pre-registered expectation was that the link would be
weaker for Samsung, whose chips are only part of a group that also sells phones, screens and
appliances, and weaker for operating profit, which also depends on costs. Neither gap is confirmed.
SK Hynix's revenue correlation exceeds Samsung's by 0.05 (bootstrap interval -0.003 to 0.22, not
significant after Holm), and operating profit tracks exports as closely as revenue does. A possible
reading, not tested here, is that memory prices drive both sales and margins.

**Structural for SK Hynix; the AI boom may matter for Samsung.** Restricting the sample to quarters
before 2023 (n = 25) leaves SK Hynix's correlations unchanged (0.94 for revenue). For Samsung's revenue
the correlation falls to 0.72 (95% CI 0.45 to 0.87), consistent with a link that strengthened when
chips came to dominate the group's results during the AI boom. This comparison is *descriptive* (shown, not
formally tested): the intervals of the two periods overlap. The results are robust to converting earnings into US dollars.
Replacing ECOS by UN Comtrade data lowers the correlations to 0.79 to 0.89, mostly because Comtrade
ends in 2025 and misses the two most extreme quarters of 2026; on the same quarters, the source itself
changes the correlations by about 0.02.

**What this part does not show.** A very strong correlation is not news. SK Hynix's sales are, to a
large extent, Korea's chip exports, so part of the link is an accounting overlap rather than a
forecast. What the market already knows at t, and whether exports add anything to it, is the subject
of sections 4 and 5.

*Figure 1: `figures/fig1_lead_time.png`. Figure 2: `figures/fig2_correlations.png` (appendix if space
runs short; Table 2 stays).*
