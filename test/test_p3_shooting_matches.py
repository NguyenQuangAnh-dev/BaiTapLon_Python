"""NGƯỜI 3 — shooting + matches."""
import numpy as np
import pandas as pd

from src.common.fbref_parser import extract_by_spec
from src.scrapers.matches.scraper import build_matches
from src.scrapers.player_stats.shooting import SPEC_SHOOTING
from tests.helpers import _fake_raw, selftest_spec


def test_shooting_parser():
    selftest_spec(SPEC_SHOOTING, must_numeric=["Sh_Sh", "Sh_SoT%", "ShExp_xG"])
    df, _ = extract_by_spec(_fake_raw(SPEC_SHOOTING, 5), SPEC_SHOOTING)
    assert df["Sh_SoT%"].between(0, 100).all()


def test_build_matches_filters_and_result():
    raw = pd.DataFrame({"Date": ["2024-08-16", "2024-08-17", "2024-08-18", np.nan, "2024-08-20"],
                        "Home": ["Man Utd", "Arsenal", "Chelsea", np.nan, "Spurs"],
                        "Score": ["1–0", "2-2", "0–3", np.nan, ""],         # en dash, gạch ngang, trống
                        "Away": ["Fulham", "Wolves", "City", np.nan, "Leeds"]})
    m = build_matches(raw)
    assert len(m) == 3 and m["result"].tolist() == ["H", "D", "A"]
    assert m["match_id"].is_unique and m["season"].eq("2024/2025").all()
    assert m["date"].iloc[0] == "2024-08-16"
