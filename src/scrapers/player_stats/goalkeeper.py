"""NGƯỜI 6 — Goalkeeping (v2 chưa giao ai -> gán cho Người 6)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_GOALKEEPER = TableSpec(
    key="goalkeeper", page="keepers", table_id="stats_keeper", owner=6,
    columns=(
        cols("Performance", "GK", "GA", "GA90", "SoTA", "Saves", "Save%", "W", "D", "L", "CS", "CS%")
        + cols("Penalty Kicks", "GKPK", "PKatt", "PKA", "PKsv", "PKm", "Save%")
    ))


def scrape_goalkeeper(fetcher: Fetcher) -> pd.DataFrame:
    """Chỉ thủ môn mới có dòng ở bảng này; cầu thủ khác sẽ là N/a sau khi merge (không phải 0)."""
    return scrape_spec(fetcher, SPEC_GOALKEEPER)
