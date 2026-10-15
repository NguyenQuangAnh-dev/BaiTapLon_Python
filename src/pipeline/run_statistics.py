"""Chạy trọn PHẦN II (Người 8): top/bottom, results2.csv, đội tốt nhất, histogram."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from src.analysis.statistics import build_results2, numeric_stats, top_bottom
from src.analysis.team_ranking import assess_team_form, best_team_per_stat
from src.common.io_utils import load_results, save_with_na
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.visualization.histograms import plot_histograms


def run_stats(df: Optional[pd.DataFrame] = None, hist: bool = True,
              hist_limit: Optional[int] = None) -> None:
    PATHS.make()
    df = load_results() if df is None else df
    stats = numeric_stats(df)
    log(f"== PHẦN II: Thống kê ({len(df)} cầu thủ, {len(stats)} thống kê số) ==")

    tb = top_bottom(df, stats)
    save_with_na(tb, PATHS.final / "top3_bottom3.csv")
    for s in stats[:3]:                                   # in mẫu 3 thống kê đầu
        part = tb[tb["Statistic"] == s]
        log(f"  {s}: Top3 = " + ", ".join(f"{r.Player} ({r.Value:g})" for r in part[part.Type == 'Top'].itertuples())
            + " | Bottom3 = " + ", ".join(f"{r.Player} ({r.Value:g})" for r in part[part.Type == 'Bottom'].itertuples()))
    log(f"  -> đầy đủ: {PATHS.final / 'top3_bottom3.csv'}")

    r2 = build_results2(df, stats)
    save_with_na(r2, PATHS.results2)
    log(f"  -> {PATHS.results2}  ({len(r2)} dòng: 'all' + {len(r2) - 1} đội)")

    best = best_team_per_stat(df, stats)
    save_with_na(best, PATHS.final / "best_team_per_stat.csv")
    table, text = assess_team_form(df, stats, best)
    save_with_na(table, PATHS.final / "team_ranking.csv")
    (PATHS.final / "team_analysis.txt").write_text(text, encoding="utf-8")
    log("\n" + text)

    if hist:
        n = plot_histograms(df, stats, limit=hist_limit)
        log(f"  -> {n} thống kê đã vẽ histogram trong {PATHS.plots}/hist_all và hist_teams")
