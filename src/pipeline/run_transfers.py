"""Chạy PHẦN IV: thu thập chuyển nhượng (Người 10) rồi ước lượng giá trị."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from config import settings
from src.analysis.valuation import estimate_player_value
from src.common.io_utils import read_table, save_csv
from src.common.paths import PATHS
from src.common.schema import validate_foreign_keys
from src.common.sources import write_sources
from src.common.logging_utils import log
from src.scrapers.transfers.scraper import scrape_transfers


def run_transfers(source: str = "fbref", delay: float = settings.REQUEST_DELAY,
                  transfer_file: Optional[str] = None) -> pd.DataFrame:
    PATHS.make()
    players, teams = read_table("players"), read_table("teams")
    transfers = scrape_transfers(players, teams, source, delay, transfer_file)
    save_csv(transfers, PATHS.tables["transfers"])
    for issue in validate_foreign_keys({"players": players, "teams": teams, "transfers": transfers}):
        log(f"   ⚠ {issue}")
    write_sources()
    return transfers


def run_valuation() -> pd.DataFrame:
    return estimate_player_value()
