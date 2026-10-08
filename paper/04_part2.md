# 4. Do markets react on release days?

*Draft for Zach's review, 2026-10-08 (after the cutting pass). Figures from `outputs/v2_main.csv` and `outputs/v2_robustness.csv`;
specifications pre-registered in `QUESTION.md` (V2-1 to V2-4).*

*In plain terms: on the days these figures are published, share prices move somewhat more than on an
ordinary day, but not much more, and the pattern looks like a reaction to general economic news
rather than to chips specifically.*

**Method.** An *event study* (MacKinlay, 1997) compares what happens around a known date with what
would normally happen. For each release and stock, the normal return is estimated over the preceding
250 trading days; the excess over it is the *abnormal return*, and its sum over the day before, the day
of and the day after the release is the *cumulative abnormal return* (CAR). The *reaction ratio* divides
the absolute CAR by the average move over three ordinary days of the same year: 1 means an ordinary
day, 2 twice as much. Significance comes from a *permutation test* against thousands of random ordinary
days, Holm-adjusted over 22 tests. Releases overlapping another type of release are left out.

**Release days are somewhat busier, never much busier** (Figure 2). Moves are 22% (SK Hynix), 35%
(Samsung) and 25% (KOSPI) larger than usual after the monthly release, all significant after Holm;
19%, 15% and 3% after the first-20-days release, none significant; 50% and 63% after the two firms'
results. No ratio reaches 2. Without 31 July 2026, the KOSPI's record day, which falls in one monthly
window, the monthly estimates barely change but SK Hynix's and the KOSPI's no longer pass Holm.

**The pre-registered contrasts are not found.** The earlier first-20-days figure does not move markets
more than the monthly one, and once scaled by its own volatility SK Hynix reacts no more than Samsung or
the index. The comparison before and after 2016 cannot be interpreted: rule-based dates, if wrong,
measure ordinary days and push the ratio toward 1, the level observed.

**A possible reading, not tested.** Markets may respond to the overall economic signal rather than to
chips: the monthly release covers all exports, and the index reacts as much as the chip stocks. Other
first-of-month news, such as manufacturing surveys (PMIs), may also play a part.

**Robustness.** Against the US chip index (SOX), SK Hynix's reaction to the first-20-days figure becomes
significant (1.30), a fragile result; other checks are in appendix A4.

*Figure 2: `figures/fig2_reactions.png`.*
