"""Export the figures of the research note as PNG into paper/figures/ (requires kaleido).

Body: Figure 1 (lead time), Figure 2 (reaction ratios), Figure 3 (priced-in test).
Appendix: Figure A1 (exports vs earnings, four panels).

Usage:
    .venv/bin/python src/export_figures.py
"""

from pathlib import Path

import pandas as pd

import event_study as E
import leadlag as L

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "paper" / "figures"


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    corr = pd.read_csv(ROOT / "outputs" / "v1_2_correlations.csv")
    main_r = pd.read_csv(ROOT / "outputs" / "v2_main.csv")
    use = pd.read_csv(ROOT / "outputs" / "v2_reactions_by_event.csv", parse_dates=["release_date", "event_day"])
    L.figure(L.lead_times()).write_image(FIG / "fig1_lead_time.png", width=1000, height=520, scale=2)
    E.figure_reactions(main_r).write_image(FIG / "fig2_reactions.png", width=1000, height=640, scale=2)
    E.figure_priced_in(use, main_r).write_image(FIG / "fig3_priced_in.png", width=1100, height=540, scale=2)
    L.figure_v1_2(pd.read_csv(ROOT / "data" / "processed" / "quarterly.csv"), corr).write_image(
        FIG / "figA1_correlations.png", width=1000, height=760, scale=2)
    print("Saved: fig1_lead_time.png, fig2_reactions.png, fig3_priced_in.png, figA1_correlations.png")


if __name__ == "__main__":
    main()
