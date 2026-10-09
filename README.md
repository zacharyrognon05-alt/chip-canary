# Chip Canary: Are Korea's Semiconductor Export Figures Already Priced In?

Korea publishes chip export figures weeks before Samsung and SK Hynix report their earnings; this
project dates every figure by the day it became public and asks whether the market still learns
anything new when the firms report.

## Question

Korea's export figures come out around the 21st (first 20 days of the month) and the 1st (full
month). If these figures already signal how Samsung and SK Hynix are doing, do the two firms' quarterly
earnings still tell the market anything new? The project rebuilds the information calendar, from
export release to earnings release, and tests predictions written down before seeing any result.

## Main results

1. **Early and very close link.** Chip exports known by the 21st of a quarter's last month precede the
   first earnings release by a median of 35 days (SK Hynix) and 16 days (Samsung), and are very strongly
   correlated with first-release earnings growth (r = 0.90 to 0.95, 2016Q3-2026Q2). For SK Hynix the
   link is structural: 0.94 before 2023 already.
2. **The AI boom may matter for Samsung.** Samsung's revenue link appears to have strengthened during
   the AI boom (0.72 before 2023). This is descriptive, not formally tested; the intervals overlap.
3. **Modest market reactions.** Share prices move only moderately more than on an ordinary day on
   export release days (about 1.2 to 1.35 times), and the first-20-days figure does not move markets more than
   the monthly one. A reaction to the broad macro signal rather than to chips is a compatible reading,
   not tested.
4. **"Priced in?" remains open.** The data are consistent with the export information being priced in
   before earnings day, but too few, and too dependent on 2026, to establish it.

![Lead time from the first-20-days export figure to each firm's first earnings release](paper/figures/fig1_lead_time.png)

**Research note (PDF):** [`paper/chip_canary_note.pdf`](paper/chip_canary_note.pdf), 6 pages plus an
appendix. Expectations, thresholds and the log of every specification run are in
[`QUESTION.md`](QUESTION.md); every data series is documented in [`data/SOURCES.md`](data/SOURCES.md).

## Repository

```
src/        data download, extraction, dataset, analysis (leadlag.py: part 1, event_study.py: part 2)
            and note-building scripts
data/       raw/ (downloads, mostly not versioned), processed/ (regenerated), SOURCES.md
outputs/    result tables (CSV) and interactive figures (HTML)
paper/      note sections (Markdown), figures, appendix, PDF
notebooks/  cross-check of the ECOS index against UN Comtrade
QUESTION.md pre-registered expectations, specifications and running log
```

## Reproducing

Python 3.14, in a virtual environment:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env    # then add your own keys: UN Comtrade and OpenDART (free, e-mail registration)
```

**ECOS data, manual download.** The Bank of Korea's ECOS API requires identity verification with a
Korean mobile number, so the chip export index is downloaded by hand from https://ecos.bok.or.kr: table
3.3.1.1.1 Export Value Indices, item "Semi-conductors", monthly, CSV export. Save it as
`data/raw/ecos/Export Value Indices_02183427.csv` (the file name expected by `src/load_ecos.py`).

Then run, in this order, from the repository root (`.venv/bin/python src/<script>.py`):

```
fetch_markets.py  load_ecos.py  fetch_comtrade.py  fetch_earnings.py      # sources
fetch_release_calendar.py  extract_kcs_first20.py  build_dataset.py       # calendar and datasets
leadlag.py  event_study.py                                                # parts 1 and 2
export_figures.py  appendix_tables.py  assemble_note.py  build_pdf.py     # figures, note, PDF
```

**Fixed sample end.** The analysis uses prices and release events up to 30 September 2026 and earnings
up to 2026Q2 (`SAMPLE_END_DATE` and `SAMPLE_END_QUARTER` in `src/build_dataset.py`, `SAMPLE_END` in
`src/fetch_earnings.py`). Data published later are ignored even if downloaded, so a re-run reproduces
the note. To extend the sample, change these parameters and re-run with `--refresh` where needed.

Raw downloads are cached and reused; cached OpenDART answers are final and the API is asked again only
with `--refresh`. If OpenDART answers with an error (e.g. maintenance), the script stops with a message
and caches nothing. Yahoo Finance prices are not redistributed; a new download may
give slightly different adjusted prices, so results can differ in the last decimals (the snapshot
used is dated in `data/SOURCES.md`). `build_pdf.py` uses headless Google Chrome (macOS path in the
script).

## Credits

Analysis in Python (pandas, statsmodels, plotly). Research question, design, pre-registered
expectations and all editorial decisions by the author; code and text drafted with Claude Code
(Anthropic) and reviewed by the author. All data sources, scripts and the pre-registration log are in
the project repository.

**Author:** Zachary Rognon, Global Studies Institute, University of Geneva, 2026.
