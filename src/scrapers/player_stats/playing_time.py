"""NGƯỜI 7 — Playing Time bổ sung (Starts, Subs, Team Success)."""
from __future__ import annotations

import pandas as pd

from src.common.fetcher import Fetcher
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec


SPEC_PLAYING_TIME = TableSpec(
    key="playing_time", page="playingtime", table_id="stats_playing_time", owner=7,
    columns=(
        cols("Starts", "Start", "Starts", "Mn/Start", "Compl")
        + cols("Subs", "Sub", "Subs", "Mn/Sub", "unSub")
        + cols("Team Success", "Team", "PPM", "onG", "onGA")
        + cols("Team Success (xG)", "TeamxG", "onxG", "onxGA")
    ))


def scrape_playing_time(fetcher: Fetcher) -> pd.DataFrame:
    return scrape_spec(fetcher, SPEC_PLAYING_TIME)
