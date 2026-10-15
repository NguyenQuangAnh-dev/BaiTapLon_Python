"""NGƯỜI 3 — Shooting + Expected stats (xG, npxG...)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.logging_utils import log
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_SHOOTING = TableSpec(
    key="shooting", page="shooting", table_id="stats_shooting", owner=3,
    columns=(
        # Chuẩn
        cols("Standard", "Sh", "Gls", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90",
             "G/Sh", "G/SoT", "Dist", "FK", "PK", "PKatt")
        # Dự kiến
        + cols("Expected", "ShExp", "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG")
    ))


def scrape_shooting(fetcher: Fetcher) -> pd.DataFrame:
    """Nếu nguồn chính thiếu xG/npxG: thả CSV nguồn khác vào data/raw/supplement_shooting.csv
    (cột: Player, Squad, ShExp_xG, ShExp_npxG...) -> apply_supplements() sẽ ghép theo Player+Squad."""
    df = scrape_spec(fetcher, SPEC_SHOOTING)
    pct = [c for c in ("Sh_SoT%",) if c in df.columns]
    for c in pct:                                      # kiểm tra phạm vi 0–100
        bad = df[c].dropna()
        if ((bad < 0) | (bad > 100)).any():
            log(f"   ! {c} có giá trị ngoài [0,100]")
    return df
