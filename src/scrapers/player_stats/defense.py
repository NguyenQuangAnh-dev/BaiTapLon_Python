"""NGƯỜI 6 — Defense (Tackles, Challenges, Blocks, Int, Clr, Err)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_DEFENSE = TableSpec(
    key="defense", page="defense", table_id="stats_defense", owner=6,
    columns=(
        cols("Tackles", "Tkl", "Tkl", "TklW", "Def 3rd", "Mid 3rd", "Att 3rd")
        + cols("Challenges", "Chall", "Tkl", "Att", "Tkl%", "Lost")
        + cols("Blocks", "Blk", "Blocks", "Sh", "Pass")
        + cols(None, "Blk", "Int", "Tkl+Int", "Clr", "Err")
    ))


def scrape_defense(fetcher: Fetcher) -> pd.DataFrame:
    """Lưu ý: không suy diễn giá trị — nguồn không có thì để N/a."""
    return scrape_spec(fetcher, SPEC_DEFENSE)
