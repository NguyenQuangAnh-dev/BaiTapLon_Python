"""NGƯỜI 8 — statistics, results2, đội tốt nhất, histogram."""
import numpy as np
import pandas as pd

from src.analysis.statistics import build_results2, numeric_stats, top_bottom
from src.analysis.team_ranking import best_team_per_stat
from src.visualization.histograms import plot_histograms


def _df():
    return pd.DataFrame({"Player": list("abcdefgh"), "Squad": list("XXXXYYYY"),
                         "Gls": [1, 2, 3, 4, 5, 6, 7, np.nan], "Perf_CrdY": [0, 1, 2, 3, 4, 5, 6, 7]})


def test_top_bottom_and_results2():
    df = _df()
    assert numeric_stats(df) == ["Gls", "Perf_CrdY"]
    tb = top_bottom(df, ["Gls"])
    assert tb[(tb.Type == "Top") & (tb.Rank == 1)]["Player"].iloc[0] == "g"
    assert tb[(tb.Type == "Bottom") & (tb.Rank == 1)]["Player"].iloc[0] == "a"
    r2 = build_results2(df, ["Gls"])
    assert list(r2.iloc[:, 1]) == ["all", "X", "Y"] and r2["Mean of Gls"].iloc[0] == 4.0


def test_lower_is_better_for_cards():
    best = best_team_per_stat(_df(), ["Gls", "Perf_CrdY"]).set_index("Statistic")
    assert best.loc["Gls", "Best team"] == "Y" and best.loc["Perf_CrdY", "Best team"] == "X"


def test_histograms_created(demo_env, isolated_paths):
    from src.common.io_utils import load_results
    n = plot_histograms(load_results(), ["Min", "Perf_Ast"], limit=2)
    assert n == 2 and (isolated_paths.plots / "hist_all" / "Min.png").exists()
    assert (isolated_paths.plots / "hist_teams" / "Perf_Ast.png").exists()


def test_run_stats_writes_results2(demo_env, isolated_paths):
    from src.common.io_utils import load_results
    from src.pipeline.run_statistics import run_stats
    run_stats(load_results(), hist=False)
    r2 = pd.read_csv(isolated_paths.results2, keep_default_na=False)
    assert len(r2) == 21 and r2.iloc[0]["Team"] == "all"
