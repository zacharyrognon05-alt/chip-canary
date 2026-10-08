# 6. Pre-registration and limitations

*Draft for Zach's review, 2026-10-08 (after the cutting pass). Expectations and log from `QUESTION.md`.*

*In plain terms: the expected results were written down before any calculation, so that the
analysis could not be bent to confirm them; several turned out to be wrong, and this section says
which.*

**Why write expectations first.** A study can find something "significant" by trying until it works
(*p-hacking*). Here the expectations, thresholds and 32 specifications were written in a dated file
before any result, with a log of every run. The expectations themselves were committed to the
project's version history on 7 October 2026, before the first result. Some precisions were added
later but before the corresponding results (for instance the expected category of each correlation);
they are dated in the file, but were committed together with the results, so for them the file's
log, not the version history, attests the order. The process was self-administered, not registered
with an external body.

**Table 3. Expectations written before the results, and outcomes**

| Expectation | Outcome | Verdict |
|---|---|---|
| Lead of exports over results of 15 days or more | 35 days (SK Hynix), 16 days (Samsung) | Right; just above the threshold for Samsung |
| Very strong link for SK Hynix revenue | r = 0.95 | Right |
| Medium or strong link for SK Hynix operating profit | r = 0.94, very strong | Wrong (stronger) |
| Medium or strong link for Samsung revenue | r = 0.90, very strong (0.72 before 2023) | Wrong (stronger), in range before 2023 |
| Weak or medium link for Samsung operating profit | r = 0.92, very strong | Wrong (stronger) |
| Link stronger for SK Hynix than for Samsung | Difference 0.05 (revenue), 0.01 (profit) | Not confirmed |
| Link stronger for revenue than for operating profit | Difference 0.01 (SK Hynix), -0.03 (Samsung) | Not confirmed |
| First-20-days figure moves prices more than the monthly one | Slightly less, for all three | Wrong |
| Reaction to the monthly figure weaker since 2016 | Stronger, but pre-2016 dates set by rule | Not interpretable |
| SK Hynix reacts more than Samsung, Samsung more than the index | About equal once scaled by volatility | Wrong |
| Some movement on results day, not much larger than usual | Ratios 1.5 (Samsung), 1.6 (SK Hynix) | Right; for SK Hynix the interval reaches 2 |
| Reaction on results day stronger when the lead is short (exploratory) | Slopes slightly positive, intervals include zero; the lead varies by about 2 days only | Not conclusive |
| Much larger reactions to large surprises (exploratory, monthly release only) | Top 20% surprises vs others: -0.02 (SK Hynix), -0.45 (Samsung), -0.54 (KOSPI) standard deviations | Wrong for Samsung and the index, not conclusive for SK Hynix |
| Information already priced in before results | Slope not different from zero, but driven by 2026 | Open |

*Thresholds: correlation categories weak < 0.3, medium 0.3 to 0.6, strong 0.6 to 0.8, very strong 0.8
or more; a reaction gap counts if it reaches half an ordinary day. All p-values Holm-adjusted within
each part, except the two exploratory rows. In the surprise test, the surprise is the full-month
growth (revised series) minus the first-20-days growth, and the reaction is counted in the direction
of the surprise; no surprise can be measured for the first-20-days release itself, for lack of a
published expectation.*

**Limitations.** Revised data for the monthly figure; a short sample dominated by 2023 to 2026; rule-based
dates before 2016; and the accounting overlap between SK Hynix's sales and exports. Others are in
appendix A7.
