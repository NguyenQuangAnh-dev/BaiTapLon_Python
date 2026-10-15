"""Dựng 6 bảng chuẩn từ dữ liệu đã thu thập (NGƯỜI 1 — Core/Schema + Người 2).

* players / player_stats lấy từ bảng mở rộng `player_stats_extended` (có player_id, team_id).
* Cầu thủ chuyển đội giữa mùa (nhiều dòng cùng player_id): cộng dồn thống kê đếm, pass_accuracy tính
  trọng số theo số chuyền, team_id = đội mà cầu thủ ra sân nhiều phút nhất.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import settings
from src.common.ids import make_team_id
from src.common.schema import enforce_schema

# cột player_stats <- cột trong bảng mở rộng (cộng dồn). goals = Perf_G-PK + Perf_PK (bàn thắng gồm penalty)
PLAYER_STATS_SUM = {"matches": "MP", "starts": "Starts", "minutes": "Min", "assists": "Perf_Ast",
                    "shots": "Sh_Sh", "shots_on_target": "Sh_SoT", "passes": "PassTot_Att",
                    "key_passes": "PassExp_KP", "tackles": "Tkl_Tkl", "interceptions": "Blk_Int",
                    "clearances": "Blk_Clr", "blocks": "Blk_Blocks",
                    "duels_won": "Aerial_Won",       # CHỈ không chiến: FBref không có 'duels' tổng (xem docs/EXTENDED_STATS.md)
                    "yellow_cards": "Perf_CrdY", "red_cards": "Perf_CrdR"}


def build_teams(squads) -> pd.DataFrame:
    names = sorted({str(s).strip() for s in squads if isinstance(s, str) and s.strip()})
    df = pd.DataFrame({"team_id": [make_team_id(n) for n in names], "team_name": names,
                       "league": settings.LEAGUE, "country": settings.COUNTRY})
    return enforce_schema(df, "teams")


def build_players(extended: pd.DataFrame) -> pd.DataFrame:
    """Một dòng/cầu thủ; team_id = đội có số phút nhiều nhất. date_of_birth: FBref chỉ có năm sinh -> để thiếu."""
    d = extended.sort_values("Min", ascending=False, na_position="last").drop_duplicates("player_id")
    out = pd.DataFrame({"player_id": d["player_id"], "player_name": d["Player"], "date_of_birth": np.nan,
                        "nationality": d["Nation"], "position": d["Pos"], "team_id": d["team_id"]})
    return enforce_schema(out.sort_values("player_id"), "players")


def _sum(g: pd.DataFrame, col: str) -> pd.Series:
    return g[col].sum(min_count=1)


def build_player_stats(extended: pd.DataFrame) -> pd.DataFrame:
    df = extended.copy()
    df["_goals"] = df["Perf_G-PK"] + df["Perf_PK"]
    rows = []
    for pid, g in df.groupby("player_id", sort=True):
        row = {"player_id": pid, "season": settings.SEASON, "league": settings.LEAGUE}
        for out, src in PLAYER_STATS_SUM.items():
            row[out] = _sum(g, src)
        row["goals"] = _sum(g, "_goals")
        att = g["PassTot_Att"]
        valid = g["PassTot_Cmp%"].notna() & att.notna() & (att > 0)
        row["pass_accuracy"] = (np.average(g.loc[valid, "PassTot_Cmp%"], weights=att[valid]) if valid.any() else np.nan)
        rows.append(row)
    return enforce_schema(pd.DataFrame(rows), "player_stats")
