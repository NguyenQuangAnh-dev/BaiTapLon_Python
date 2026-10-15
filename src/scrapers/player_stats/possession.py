"""NGƯỜI 7 — Possession (Touches, Take-Ons, Carries, Receiving)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_POSSESSION = TableSpec(
    key="possession", page="possession", table_id="stats_possession", owner=7,
    columns=(
        cols("Touches", "Touch", "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Att 3rd", "Att Pen", "Live")
        + cols("Take-Ons", "TakeOn", "Att", "Succ", "Succ%", "Tkld", "Tkld%")
        # Đề ghi 'ProDist' và 'ProgC' = PrgDist, PrgC của FBref
        + cols("Carries", "Carry", "Carries", "TotDist", ("PrgDist", "ProDist"), ("PrgC", "ProgC"),
               "1/3", "CPA", "Mis", "Dis")
        + cols("Receiving", "Recv", "Rec", "PrgR")
    ))


def scrape_possession(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_POSSESSION)
