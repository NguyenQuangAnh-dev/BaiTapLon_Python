"""Lọc và sắp xếp cầu thủ theo yêu cầu của đề (NGƯỜI 1 / NGƯỜI 2)."""
from __future__ import annotations

import pandas as pd

from config.settings import MIN_MINUTES
from src.preprocessing.cleaning import player_key


def sort_players(df: pd.DataFrame) -> pd.DataFrame:
    """Sắp theo TÊN ĐẦU TIÊN (a→z, không phân biệt dấu/hoa thường); trùng thì TUỔI giảm dần."""
    df = df.copy()
    df["_first"] = df["Player"].map(lambda s: player_key(s).split(" ")[0] if player_key(s) else "")
    df["_full"] = df["Player"].map(player_key)
    df["_age"] = pd.to_numeric(df["Age"], errors="coerce")
    df = df.sort_values(["_first", "_age", "_full"], ascending=[True, False, True],
                        na_position="last", kind="mergesort")
    return df.drop(columns=["_first", "_full", "_age"]).reset_index(drop=True)



def filter_min_minutes(df: pd.DataFrame, minutes: int = MIN_MINUTES) -> pd.DataFrame:
    """Chỉ giữ cầu thủ thi đấu HƠN `minutes` phút (Min > 90, nghiêm ngặt)."""
    return df[pd.to_numeric(df["Min"], errors="coerce") > minutes].reset_index(drop=True)
