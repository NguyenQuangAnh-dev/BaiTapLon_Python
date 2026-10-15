"""NGƯỜI 5 — pass types + SCA/GCA."""
import numpy as np

from src.common.fbref_parser import extract_by_spec, find_col
from src.scrapers.player_stats.gca import SPEC_SCA_GCA
from src.scrapers.player_stats.passing_types import SPEC_PASS_TYPES
from tests.helpers import _fake_raw, selftest_spec


def test_pass_types_and_gca_parsers():
    selftest_spec(SPEC_PASS_TYPES, must_numeric=["PTyp_Live", "Corner_In", "POut_Blocks"])
    selftest_spec(SPEC_SCA_GCA, must_numeric=["SCA_SCA", "SCA_SCA90", "GCA_GCA", "GCAType_Def"])


def test_missing_stays_nan_not_zero():
    raw = _fake_raw(SPEC_SCA_GCA, 3)
    raw.iloc[0, find_col(list(raw.columns), "GCA", "GCA")] = np.nan
    df, _ = extract_by_spec(raw, SPEC_SCA_GCA)
    assert df["GCA_GCA"].isna().iloc[0]
