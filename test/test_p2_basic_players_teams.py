"""NGƯỜI 2 — bảng standard, players, teams."""
import pandas as pd

from src.preprocessing.canonical_tables import build_players, build_teams
from src.preprocessing.filters import filter_min_minutes
from src.scrapers.player_stats.basic import SPEC_BASIC
from tests.helpers import selftest_spec


def test_basic_parser():
    selftest_spec(SPEC_BASIC, must_numeric=["MP", "Starts", "Min", "Perf_Ast", "P90_xG"])


def test_min_filter_is_strict():
    df = pd.DataFrame({"Player": list("ABC"), "Min": [90, 91, 2000]})
    assert filter_min_minutes(df)["Player"].tolist() == ["B", "C"]


def test_players_one_row_per_player_team_with_most_minutes():
    ext = pd.DataFrame({"player_id": ["p1", "p1", "p2"], "team_id": ["a", "b", "a"], "Player": ["P1", "P1", "P2"],
                        "Nation": ["ENG"] * 3, "Pos": ["FW", "FW", "DF"], "Min": [500, 1500, 900]})
    p = build_players(ext)
    assert len(p) == 2 and p.set_index("player_id").loc["p1", "team_id"] == "b"
    assert p["date_of_birth"].isna().all(), "không bịa ngày sinh"


def test_teams():
    t = build_teams(["Arsenal", "Chelsea", "Arsenal", None])
    assert t["team_id"].tolist() == ["arsenal", "chelsea"] and (t["league"] == "Premier League").all()
