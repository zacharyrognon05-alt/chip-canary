# 5. Is the predictable part already priced in?

*Draft for Zach's review, 2026-10-07. Figures from `outputs/v2_main.csv` and `outputs/v2_robustness.csv`;
specification pre-registered in `QUESTION.md` (V2-5).*

*In plain terms: if investors had already used the export figures, share prices should not react on
results day to the part of the results those figures announced; the data are compatible with this,
but they are too few to prove it.*

**The test.** Sections 3 and 4 leave one question open. Exports announce much of the results, and
results days move prices; but does the market react, on results day, to the part it could have
predicted from exports? If that part was already *priced in* (incorporated in the share price before
the announcement), the reaction should not depend on it. For each quarter, the part of earnings
predicted by exports is obtained from a *regression*, a straight line fitted between export growth
and earnings growth. To avoid look-ahead, the line is fitted on an *expanding window*: for each
quarter, only the quarters whose results were already public at that date are used, and the first
prediction is made after eight quarters of history. The reaction on the day of each firm's first
earnings release is measured as in section 4, but with its sign (a fall counts as negative), in units
of an ordinary day. The test asks whether this signed reaction rises with the predicted part, that is,
whether the slope of a line fitted between the two differs from zero. Operating profit is the earnings
measure, since profit is the figure markets watch most on results day.

**A result compatible with "priced in", but not informative.** For both firms, the slope is not
significantly different from zero (Figure 4). For SK Hynix (22 quarters, 2018Q4 to 2026Q2), the
estimated slope is -1.90, with a 95% confidence interval from -2.71 to +1.74 and a Holm-adjusted
p-value of 0.38. For Samsung (31 quarters), it is -1.96, from -7.09 to +6.18, p-value 1.00. Read
literally, the data do not reject the idea that the market had already absorbed what exports
announced. They do not establish it either, for two reasons.

**Two reasons for caution.** First, the estimates rest on very few quarters. For SK Hynix a single
point, the second quarter of 2026, drives the slope: its predicted part is far above all others, and
its results release of 29 July 2026 fell in the turbulent days before the record session of 31 July,
with an abnormal return of about -33% over three days. Without that quarter the slope is -0.07, close to zero.
For Samsung the sign of the slope depends on the first or the second quarter of 2026. These checks
are diagnostics, not pre-registered tests, and are reported as such. Second, the confidence intervals
are wide: they cannot exclude an effect of up to 1.6 ordinary days (SK Hynix) and 1.1 ordinary days
(Samsung) for a typical difference in the predicted part. The results are therefore compatible both
with a market that had already priced the information in and with one that still reacted strongly
to it. The conclusion does not change when
revenue replaces operating profit, when exports come from UN Comtrade, or when earnings are converted
into US dollars.

**What would settle it.** Three additions would sharpen the test: more quarters, which only time will
provide; the time of day of each release, to measure the reaction within the session rather than over
three days; and analysts' forecasts of results, which would allow the reaction to be related to the
*surprise* relative to expectations, the approach used for macroeconomic announcements by Andersen,
Bollerslev, Diebold and Vega (2003). Such forecasts are sold by commercial data providers and were not
available for this note.

*Figure 4: `figures/fig4_priced_in.png`.*
