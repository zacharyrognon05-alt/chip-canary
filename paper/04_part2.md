# 4. Do markets react on release days?

*Draft for Zach's review, 2026-10-07. Figures from `outputs/v2_main.csv` and `outputs/v2_robustness.csv`;
specifications pre-registered in `QUESTION.md` (V2-1 to V2-4).*

*In plain terms: on the days these figures are published, share prices move somewhat more than on an
ordinary day, but not much more, and the pattern looks like a reaction to general economic news
rather than to chips specifically.*

**Method.** The question is whether prices move unusually around each release. This is the classic
*event study* (MacKinlay, 1997): compare what happens around a known date with what would normally
happen. For each release and each stock (SK Hynix, Samsung, the KOSPI), the normal daily return is
estimated over the 250 trading days before the release, leaving out the days around other releases.
The return in excess of this normal level is the *abnormal return*; summed over the day before, the
day of and the day after the release, it gives the *cumulative abnormal return* (CAR). Because the
question is the size of the move, not its direction, the reaction is measured as the absolute CAR and
divided by the average absolute move over three ordinary days of the same period. The resulting
*reaction ratio* reads simply: 1 means an ordinary day, 2 means twice as much movement. Computing the
"ordinary day" over the preceding year, rather than over the whole period, matters because volatility
varies a lot (2026 was far more volatile than 2017). Statistical significance is assessed by a
*permutation test*: the observed reaction is compared with thousands of reactions computed on random
ordinary days. With 22 tests in this part, p-values are again Holm-adjusted. The main sample covers
2016 to 2026; a release whose window overlaps that of another type of release is left out, which
removes 13 of the 42 SK Hynix earnings releases (published a few days after the first-20-days figure).

**Release days are somewhat busier, never much busier.** All reaction ratios lie between 1 and 2
(Figure 3). The monthly export release is followed by moves 22% (SK Hynix), 35% (Samsung) and 25%
(KOSPI) larger than on an ordinary day, all three significant after Holm. The first-20-days release
gives 19%, 15% and 3%, none significant after Holm. First earnings releases, included for comparison,
give 50% (Samsung) and 63% (SK Hynix). None reaches the pre-registered threshold of "much stronger"
(a ratio of 2). One caveat concerns 31 July 2026, the largest daily rise in the KOSPI's history: it is
the day before a monthly release published on a Saturday, so it falls in that release's window.
Without it, the estimates barely change (SK Hynix 1.22 to 1.20, KOSPI 1.25 to 1.22), but they no
longer pass the Holm threshold (adjusted p-values 0.08 and 0.10).

**The pre-registered contrasts are not found.** The first-20-days figure arrives first and already
covers two thirds of the month, so it was expected to move markets more than the monthly figure. It
does not: the monthly figure produces, if anything, slightly larger moves (differences of -0.03,
-0.20 and -0.22 ordinary days, all intervals below the pre-registered gap of 0.5). SK Hynix, the
purest chip company, was expected to react more than Samsung, and Samsung more than the index. Once
each stock's move is scaled by its own ordinary volatility, the three react about equally. The
comparison of reactions before and after 2016 cannot be interpreted: before 2016 the release dates
are set by rule, and a wrong date measures an ordinary day, which pushes the ratio toward 1, the level
actually observed (0.91 to 1.10).

**A possible reading, not tested.** These patterns are compatible with markets responding to the
overall economic signal of the trade figures rather than to chips. The monthly release covers all
Korean exports, not only semiconductors, and the index reacts as much as the two chip stocks. The
first trading day of the month also brings other news, such as purchasing managers' surveys of
manufacturing (PMIs) for Korea and other economies, which could explain part of the reaction to the
monthly figure. The note does not separate these explanations.

**Robustness.** The conclusions on export releases hold when the reaction window is lengthened to four
days (from the release day to three days after), when the release of September 2016 (whose date could
not be verified) is dropped, and when overlapping releases are kept. Earnings results are less robust:
with the four-day window, almost all SK Hynix earnings releases overlap with the first-20-days figure
and cannot be measured, and Samsung's earnings reaction is no longer significant after Holm.
One result is fragile: measured against the US semiconductor index (SOX) of the previous night rather
than against each stock's own average, SK Hynix's reaction to the first-20-days figure rises to 1.30
and becomes significant after Holm. Details are in the appendix.

*Figure 3: `figures/fig3_reactions.png`.*
