"""Sinh ID ỔN ĐỊNH cho player/team (docs/scraper_guide.md mục 5: cùng thực thể -> cùng ID mọi bảng).

team_id   = slug(tên đội)               vd. "manchester-city"
player_id = slug(tên cầu thủ)-<quốc tịch> vd. "mohamed-salah-egy"
(Cầu thủ chuyển đội giữa mùa vẫn giữ MỘT player_id vì ID không chứa tên đội.)
"""
from __future__ import annotations

import re
from difflib import get_close_matches
from typing import Optional

import pandas as pd

from config.team_aliases import TEAM_ALIASES
from src.preprocessing.cleaning import player_key, strip_accents, team_key


def slugify(text) -> str:
    t = strip_accents(str(text)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def make_team_id(team_name) -> str:
    return slugify(team_name)


def make_player_id(player_name, nation=None) -> str:
    base = slugify(player_name)
    nat = slugify(nation) if nation is not None and not (isinstance(nation, float) and pd.isna(nation)) else ""
    return f"{base}-{nat}" if nat else base


def canonical_team_key(name) -> str:
    k = team_key(name)
    return TEAM_ALIASES.get(k, k)


def match_team_id(name, teams: pd.DataFrame, cutoff: float = 0.85) -> Optional[str]:
    """Tìm team_id từ tên đội ở website khác (alias -> khớp chính xác -> gần đúng). Không có -> None."""
    if name is None or (isinstance(name, float) and pd.isna(name)) or not str(name).strip():
        return None
    keys = {canonical_team_key(n): tid for n, tid in zip(teams["team_name"], teams["team_id"])}
    k = canonical_team_key(name)
    if k in keys:
        return keys[k]
    near = get_close_matches(k, list(keys), n=1, cutoff=cutoff)
    return keys[near[0]] if near else None


def match_player_id(name, players: pd.DataFrame, team_id: Optional[str] = None, cutoff: float = 0.9) -> Optional[str]:
    """Tìm player_id từ tên cầu thủ (ưu tiên cùng đội nếu có team_id)."""
    k = player_key(name)
    if not k:
        return None
    pk = players["player_name"].map(player_key)
    hit = players[pk == k]
    if hit.empty:
        near = get_close_matches(k, pk.unique().tolist(), n=1, cutoff=cutoff)
        hit = players[pk.isin(near)] if near else hit
    if hit.empty:
        return None
    if len(hit) > 1 and team_id is not None:
        same = hit[hit["team_id"] == team_id]
        hit = same if not same.empty else hit
    return str(hit.iloc[0]["player_id"])


def assign_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm player_id, team_id (đặt ở đầu bảng) cho bảng có Player, Nation, Squad."""
    df = df.copy()
    tid = df["Squad"].map(make_team_id)
    pid = [make_player_id(p, n) for p, n in zip(df["Player"], df["Nation"] if "Nation" in df else [None] * len(df))]
    df.insert(0, "team_id", tid.values)
    df.insert(0, "player_id", pid)
    return df
