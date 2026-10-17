"""NGƯỜI 4 — Passing (Total/Short/Medium/Long, KP, PPA...)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_PASSING = TableSpec(
    key="passing", page="passing", table_id="stats_passing", owner=4,
    columns=(
        cols("Total", "PassTot", "Cmp", "Att", "Cmp%", "TotDist", "PrgDist")
        + cols("Short", "PassShort", "Cmp", "Att", "Cmp%")
        + cols("Medium", "PassMed", "Cmp", "Att", "Cmp%")
        + cols("Long", "PassLong", "Cmp", "Att", "Cmp%")
        # Dự kiến / kiến tạo (Ast, KP, 1/3, PPA, CrsPA, PrgP không thuộc nhóm có tên)
        + cols(None, "PassExp", "Ast")
        + cols("Expected", "PassExp", "xAG", "xA", "A-xAG")
        + cols(None, "PassExp", "KP", "1/3", "PPA", "CrsPA", "PrgP")
    ))


def scrape_passing(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_PASSING)
