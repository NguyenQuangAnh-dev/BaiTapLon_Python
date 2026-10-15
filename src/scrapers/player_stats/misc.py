"""NGƯỜI 7 — Miscellaneous (Fls, Fld, Off, Crs, OG, Recov, Aerial Duels)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_MISC = TableSpec(
    key="misc", page="misc", table_id="stats_misc", owner=7,
    columns=(
        cols("Performance", "Misc", "Fls", "Fld", "Off", "Crs", "OG", "Recov")
        + cols("Aerial Duels", "Aerial", "Won", "Lost", "Won%")      # Thắng, Thua, % thắng
    ))


def scrape_misc(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_MISC)
