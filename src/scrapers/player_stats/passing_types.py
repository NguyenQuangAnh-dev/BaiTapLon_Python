"""NGƯỜI 5 — Pass Types (Live, Dead, FK, TB, Sw, Crs, TI, CK, Corner, Outcomes)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_PASS_TYPES = TableSpec(
    key="pass_types", page="passing_types", table_id="stats_passing_types", owner=5,
    columns=(
        cols("Pass Types", "PTyp", "Live", "Dead", "FK", "TB", "Sw", "Crs", "TI", "CK")
        + cols("Corner Kicks", "Corner", "In", "Out", "Str")
        + cols("Outcomes", "POut", "Cmp", "Off", "Blocks")
    ))


def scrape_pass_types(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_PASS_TYPES)
