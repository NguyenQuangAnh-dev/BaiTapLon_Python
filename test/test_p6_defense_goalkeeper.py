"""NGƯỜI 6 — defense + goalkeeper."""
import pandas as pd

from src.common.fbref_parser import extract_by_spec
from src.scrapers.player_stats.defense import SPEC_DEFENSE
from src.scrapers.player_stats.goalkeeper import SPEC_GOALKEEPER
from tests.helpers import _fake_raw, selftest_spec


def test_defense_and_goalkeeper_parsers():
    selftest_spec(SPEC_DEFENSE, must_numeric=["Tkl_Tkl", "Chall_Tkl%", "Blk_Int", "Blk_Tkl+Int"])
    selftest_spec(SPEC_GOALKEEPER, must_numeric=["GK_GA", "GK_Save%", "GKPK_PKsv"])
    df, _ = extract_by_spec(_fake_raw(SPEC_DEFENSE, 6), SPEC_DEFENSE)
    assert not df.duplicated(["Player", "Squad"]).any()


def test_outfield_players_have_missing_gk_stats(demo_env):
    ext = pd.read_csv(__import__("src.common.paths", fromlist=["PATHS"]).PATHS.extended)
    outfield = ext[~ext["Pos"].astype(str).str.startswith("GK")]
    assert outfield["GK_GA"].isna().all(), "cầu thủ ngoài sân phải thiếu (không phải 0) ở thống kê thủ môn"
