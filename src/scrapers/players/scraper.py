"""NGƯỜI 2 — bảng `players` (player_id, player_name, date_of_birth, nationality, position, team_id).

Nguồn: bảng 'standard' của FBref (Player, Nation, Pos, Squad). FBref chỉ có NĂM SINH nên date_of_birth
để thiếu (không bịa ngày). Nếu cần ngày sinh đầy đủ: báo Người 1 để thêm nguồn (Transfermarkt...).
"""
from __future__ import annotations

import pandas as pd

from src.common.logging_utils import log
from src.common.schema import validate_table
from src.preprocessing.canonical_tables import build_players


def scrape_players(extended: pd.DataFrame) -> pd.DataFrame:
    players = build_players(extended)
    for issue in validate_table(players, "players"):
        log(f"   ⚠ {issue}")
    log(f"[Người 2] players: {len(players)} cầu thủ")
    return players
