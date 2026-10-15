"""NGƯỜI 1 — core: chuẩn hóa, ID, schema, merge, tích hợp end-to-end."""
import pandas as pd
import pytest

from config import settings
from src.common.fetcher import Fetcher
from src.common.ids import make_player_id, make_team_id, match_team_id
from src.common.schema import SCHEMA, columns_of, enforce_schema, validate_foreign_keys, validate_table
from src.preprocessing.cleaning import clean_age, clean_nation, normalize_player_name, player_key, to_number
from src.preprocessing.filters import sort_players
from src.preprocessing.merge import merge_modules
from src.scrapers.player_stats.scraper import expected_result_columns


def test_cleaning():
    assert player_key("Rodri Hernández ") == player_key("Rodri Hernandez")
    assert normalize_player_name("  Mohamed   Salah ") == "Mohamed Salah"
    assert to_number(pd.Series(["1,234", "45.2%"])).tolist() == [1234.0, 45.2]
    assert to_number(pd.Series(["N/a", ""])).isna().all(), "N/a không được thành 0"
    assert clean_age("24-123") == 24 and clean_nation("eng ENG") == "ENG"


def test_sort_first_name_then_age_desc():
    df = pd.DataFrame({"Player": ["Ben Z", "Alex B", "Alex A", "alex B"], "Squad": list("WXYZ"), "Age": [30, 20, 25, 33]})
    assert sort_players(df)["Player"].tolist() == ["alex B", "Alex A", "Alex B", "Ben Z"]


def test_season_format():
    assert settings.normalize_season("2024-2025") == "2024/2025"
    assert settings.season_slug("2024/2025") == "2024-2025"
    with pytest.raises(ValueError):
        settings.normalize_season("24/25")


def test_fetcher_urls():
    f = Fetcher("fbref")
    assert f.fbref_url("stats").endswith("/2024-2025/stats/2024-2025-Premier-League-Stats")
    assert f.fbref_url("schedule").endswith("/schedule/2024-2025-Premier-League-Scores-and-Fixtures")
    assert "web.archive.org" in Fetcher("wayback").url_for("stats")


def test_ids_stable():
    assert make_team_id("Manchester City") == "manchester-city"
    assert make_player_id("Rodri Hernández", "ESP") == "rodri-hernandez-esp"
    teams = pd.DataFrame({"team_id": ["manchester-united", "nottingham-forest"],
                          "team_name": ["Manchester Utd", "Nott'ham Forest"]})
    assert match_team_id("Man United", teams) == "manchester-united"
    assert match_team_id("Nottingham Forest", teams) == "nottingham-forest"
    assert match_team_id("Real Madrid", teams) is None


def test_schema_matches_data_dictionary():
    assert columns_of("players") == ["player_id", "player_name", "date_of_birth", "nationality", "position", "team_id"]
    assert columns_of("matches") == ["match_id", "date", "league", "season", "home_team_id", "away_team_id",
                                     "home_score", "away_score", "result"]
    assert len(SCHEMA["player_stats"]) == 20 and len(SCHEMA["team_stats"]) == 15 and len(SCHEMA["transfers"]) == 6


def test_enforce_and_validate_schema():
    df = enforce_schema(pd.DataFrame({"team_id": ["a", "a"], "team_name": ["A", "A"]}), "teams")
    issues = validate_table(df, "teams")
    assert any("league" in i for i in issues) and any("trùng khóa" in i for i in issues)
    fk = validate_foreign_keys({"teams": pd.DataFrame({"team_id": ["a"]}),
                                "players": pd.DataFrame({"team_id": ["a", "zzz"]})})
    assert len(fk) == 1 and "zzz" in fk[0]


def test_merge_by_key_not_row_order():
    master = pd.DataFrame({"Player": ["A", "B"], "Squad": ["X", "Y"], "Min": [100, 200]})
    other = pd.DataFrame({"Player": ["B", "A"], "Squad": ["Y", "X"], "Sh_Gls": [2, 1]})
    m = merge_modules(master, [other]).set_index("Player")
    assert m.loc["A", "Sh_Gls"] == 1 and m.loc["B", "Sh_Gls"] == 2


def test_expected_columns_unique():
    cols = expected_result_columns()
    assert len(cols) == len(set(cols)) and cols[:5] == ["Player", "Nation", "Squad", "Pos", "Age"]


def test_end_to_end_demo(demo_env, isolated_paths):
    results = pd.read_csv(isolated_paths.results, keep_default_na=False)
    assert list(results.columns) == expected_result_columns()
    assert (pd.to_numeric(results["Min"]) > settings.MIN_MINUTES).all()
    assert (results.astype(str) == settings.NA).any().any(), "ô thiếu phải ghi 'N/a' ở file nộp"
    ext = pd.read_csv(isolated_paths.extended)
    assert ext.isna().any().any() and not (ext.astype(str) == settings.NA).any().any(), "processed dùng ô trống, không dùng 'N/a'"
    for name, path in isolated_paths.tables.items():
        if name != "transfers":
            assert path.exists(), name
    from src.pipeline.build_dataset import load_tables, validate_all
    assert validate_all(load_tables()) == []
