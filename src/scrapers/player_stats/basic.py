"""NGƯỜI 2 — bảng 'standard' FBref: thông tin cơ bản, thời gian thi đấu, hiệu suất, dự kiến, tiến triển, /90 phút."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_BASIC = TableSpec(
    key="basic", page="stats", table_id="stats_standard", owner=2,
    columns=(
        [(None, "Player", "Player"), (None, "Nation", "Nation"), (None, "Squad", "Squad"),
         (None, "Pos", "Pos"), (None, "Age", "Age")]
        # Thời gian thi đấu
        + cols("Playing Time", "", "MP", "Starts", "Min")
        # Hiệu suất: bàn thắng không phạt đền (G-PK), phạt đền (PK), kiến tạo, thẻ vàng, thẻ đỏ
        + cols("Performance", "Perf", "G-PK", "PK", "Ast", "CrdY", "CrdR")
        # Dự kiến
        + cols("Expected", "Exp", "xG", "npxG", "xAG")
        # Tiến triển
        + cols("Progression", "Prog", "PrgC", "PrgP", "PrgR")
        # Theo 90 phút
        + cols("Per 90 Minutes", "P90", "Gls", "Ast", "G+A", "G-PK", "G+A-PK",
               "xG", "xAG", "xG+xAG", "npxG", "npxG+xAG")
    ))


def scrape_basic(fetcher: Fetcher) -> pd.DataFrame:
    """Lấy toàn bộ cầu thủ (CHƯA lọc phút)."""
    return scrape_spec(fetcher, SPEC_BASIC)
