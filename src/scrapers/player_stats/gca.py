"""NGƯỜI 5 — Goal and Shot Creation (SCA/GCA)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


_ACTIONS = ("PassLive", "PassDead", "TO", "Sh", "Fld", "Def")


SPEC_SCA_GCA = TableSpec(
    key="sca_gca", page="gca", table_id="stats_gca", owner=5,
    columns=(
        cols("SCA", "SCA", "SCA", "SCA90")
        + cols("SCA Types", "SCAType", *_ACTIONS)
        + cols("GCA", "GCA", "GCA", "GCA90")
        + cols("GCA Types", "GCAType", *_ACTIONS)
    ))


def scrape_sca_gca(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_SCA_GCA)
