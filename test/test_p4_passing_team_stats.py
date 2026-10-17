"""NGƯỜI 4 — passing + team_stats."""
import pandas as pd

from src.scrapers.player_stats.passing import SPEC_PASSING
from src.scrapers.team_stats.scraper import compute_from_matches
from tests.helpers import selftest_spec


def test_passing_parser():
    selftest_spec(SPEC_PASSING, must_numeric=["PassTot_Cmp", "PassLong_Att", "PassExp_xA", "PassExp_PrgP"])


def test_team_stats_from_matches():
    m = pd.DataFrame({"home_team_id": ["a", "b"], "away_team_id": ["b", "a"], "home_score": [2, 0], "away_score": [0, 0]})
    t = compute_from_matches(m).set_index("team_id")
    assert t.loc["a", "points"] == 4 and t.loc["a", "clean_sheets"] == 2 and t.loc["a", "goal_difference"] == 2
    assert t.loc["b", "points"] == 1 and t.loc["b", "losses"] == 1 and t.loc["b", "matches"] == 2


def test_team_stats_demo(demo_env):
    ts = demo_env["team_stats"]
    assert len(ts) == 20 and (ts["matches"] == 38).all()
    assert (ts["points"] == 3 * ts["wins"] + ts["draws"]).all()
    assert ts["possession"].notna().all(), "bảng đội phải có possession"
