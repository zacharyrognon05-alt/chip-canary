"""Assemble the research note into one file for reading: paper/draft_full.md.

Abstract + introduction + sections 2 to 6 + conclusion + references + closing line.
Removes the "Draft for Zach's review" lines and replaces figure pointers by embedded images with
captions. The section files remain the source; re-run this script after any change.

Usage:
    .venv/bin/python src/assemble_note.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
SECTIONS = ["02_data.md", "03_part1.md", "04_part2.md", "05_priced_in.md", "06_preregistration.md"]

FIGURES = {
    "fig1_lead_time.png": "Figure 1. Lead time from the first-20-days export figure of the quarter's last month to "
                          "each firm's first earnings release, by quarter, with the pre-registered thresholds.",
    "fig2_reactions.png": "Figure 2. Reaction ratio by release type and stock (1 = ordinary day), with 95% intervals; "
                          "hollow markers are not significant after Holm correction.",
    "fig3_priced_in.png": "Figure 3. Earnings-day reaction (signed, in ordinary days) against the part of earnings "
                          "predicted by exports; 2026 quarters marked.",
}

REFERENCES = """## References

Andersen, T. G., Bollerslev, T., Diebold, F. X. and Vega, C. (2003). Micro Effects of Macro
Announcements: Real-Time Price Discovery in Foreign Exchange. *American Economic Review*, 93(1), 38-62.
https://doi.org/10.1257/000282803321455151

Bloomberg, republished by Infobae (2021). Korea's Exports Extend Recovery in January, Early Data Show.
21 January 2021. https://www.infobae.com/en/2021/01/21/koreas-exports-extend-recovery-in-january-early-data-show

CNBC (2016). Samsung cuts $2.3 billion off its profit guidance due to Galaxy Note 7 crisis. 12 October
2016. https://www.cnbc.com/2016/10/12/samsung-cuts-2-billion-off-its-profit-guidance-due-to-galaxy-note-7-crisis.html

Korea Customs Service (2023). '23년 12월 1일 ~ 12월 20일 수출입 현황 (Exports and imports, 1-20 December
2023). Press release, 21 December 2023.
https://www.customs.go.kr/kcs/na/ntt/selectNttInfo.do?mi=2891&bbsId=1362&nttSn=10097237&nttSnUrl=c7334bd0c3a799777b5b3a473ef077e8

Korea Customs Service (2026). 2026년 9월 1일 ~ 9월 20일 수출입 현황 [잠정치] (Exports and imports, 1-20
September 2026, provisional). Press release, 21 September 2026.
https://www.customs.go.kr/kcs/na/ntt/selectNttInfo.do?mi=2891&bbsId=1362&nttSn=10177443&nttSnUrl=b76927b3d643e2a959deed83783dc1b8

MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*,
35(1), 13-39. https://EconPapers.repec.org/RePEc:aea:jeclit:v:35:y:1997:i:1:p:13-39

Samsung Electronics (2016). [Update] Samsung Electronics Announces Revised Earnings Guidance for Q3
2016. Samsung Global Newsroom, 12 October 2016.
https://news.samsung.com/global/samsung-electronics-announces-earnings-guidance-for-q3-2016

TrendForce News (2025). HBM Market Heats Up as Three Giants Clash, with HBM4 at the Center. 17 September
2025. https://www.trendforce.com/news/2025/09/17/news-hbm-market-heats-up-as-three-giants-clash-with-hbm4-at-the-center/
"""

CLOSING = ("*Analysis in Python (pandas, statsmodels, plotly); code written with the help of Claude Code "
           "(Anthropic). All data sources, scripts and the pre-registration log are in the project repository.*")


def clean(text: str) -> str:
    text = re.sub(r"^\*Draft for Zach's review.*?\*\n\n", "", text, flags=re.S | re.M)
    out = []
    for line in text.splitlines():
        figs = re.findall(r"figures/(fig\d_\w+\.png)", line)
        if line.startswith("*Figure") and figs:
            for f in figs:
                if f in FIGURES:
                    out += [f"![{FIGURES[f].split('.')[0]}](figures/{f})", "", f"*{FIGURES[f]}*", ""]
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


def main() -> None:
    parts = [(PAPER / "00_abstract.md").read_text().strip(), "",
             clean((PAPER / "01_introduction.md").read_text()).replace("# ", "## ", 1), ""]
    for name in SECTIONS:
        parts += [clean((PAPER / name).read_text()).replace("# ", "## ", 1), ""]
    parts += [clean((PAPER / "07_conclusion.md").read_text()).replace("# ", "## ", 1), "", REFERENCES, CLOSING, "",
              "*Appendix: `appendix.md` and `appendix_tables.md`.*"]
    dest = PAPER / "draft_full.md"
    dest.write_text("\n".join(parts) + "\n")
    words = len(re.findall(r"\w+", "\n".join(l for l in dest.read_text().splitlines()
                                             if not l.startswith("|") and not l.startswith("!["))))
    body = dest.read_text().split("## References")[0]
    main_words = len(re.findall(r"\w+", "\n".join(l for l in body.splitlines()
                                                 if not l.startswith("|") and not l.startswith("!["))))
    print(f"Saved: {dest.relative_to(ROOT)} ({words} words in total; {main_words} before the references, "
          f"tables' rows excluded, notes and captions included)")


if __name__ == "__main__":
    main()
