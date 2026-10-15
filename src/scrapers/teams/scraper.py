"""NGƯỜI 2 — bảng `teams` (team_id, team_name, league, country).

Nguồn: bảng đội 'stats_squads_standard_for' trên cùng trang 'stats' của FBref (20 đội). Nếu bảng này
không có, lấy danh sách đội từ bảng cầu thủ.
"""
from __future__ import annotations

import pandas as pd

from src.common.fbref_parser import read_fbref_table
from src.common.fetcher import Fetcher
from src.common.logging_utils import log
from src.common.schema import validate_table
from src.preprocessing.canonical_tables import build_teams


def scrape_teams(fetcher: Fetcher, extended: pd.DataFrame) -> pd.DataFrame:
    squads: list[str] = []
    raw = read_fbref_table(fetcher.get_html("stats"), "stats_squads_standard_for")
    if raw is not None:
        col = [i for i, (_, s) in enumerate(raw.columns) if s == "Squad"]
        if col:
            squads = [str(x) for x in raw.iloc[:, col[0]] if str(x) not in ("Squad", "nan")]
    if not squads:
        squads = list(extended["Squad"].dropna().unique())
    teams = build_teams(squads)
    for issue in validate_table(teams, "teams"):
        log(f"   ⚠ {issue}")
    log(f"[Người 2] teams: {len(teams)} đội")
    return teams
