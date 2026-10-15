"""Schema 6 bảng chuẩn — khớp CHÍNH XÁC docs/DATA_DICTIONARY.md (NGƯỜI 1 — Core/Schema).

Không tự ý đổi tên/thêm/xóa cột. Muốn đổi: báo Người 1 sửa DATA_DICTIONARY.md và file này cùng lúc.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

# (tên cột, kiểu, bắt buộc)
SCHEMA: dict[str, list[tuple[str, str, bool]]] = {
    "players": [("player_id", "string", True), ("player_name", "string", True), ("date_of_birth", "date", False),
                ("nationality", "string", False), ("position", "string", False), ("team_id", "string", True)],
    "teams": [("team_id", "string", True), ("team_name", "string", True), ("league", "string", True),
              ("country", "string", True)],
    "player_stats": [("player_id", "string", True), ("season", "string", True), ("matches", "int", False),
                     ("starts", "int", False), ("minutes", "int", False), ("goals", "int", False),
                     ("assists", "int", False), ("shots", "int", False), ("shots_on_target", "int", False),
                     ("passes", "int", False), ("key_passes", "int", False), ("pass_accuracy", "float", False),
                     ("tackles", "int", False), ("interceptions", "int", False), ("clearances", "int", False),
                     ("blocks", "int", False), ("duels_won", "int", False), ("yellow_cards", "int", False),
                     ("red_cards", "int", False), ("league", "string", True)],
    "team_stats": [("team_id", "string", True), ("season", "string", True), ("matches", "int", False),
                   ("wins", "int", False), ("draws", "int", False), ("losses", "int", False),
                   ("goals_for", "int", False), ("goals_against", "int", False),
                   ("goal_difference", "int", False), ("points", "int", False), ("clean_sheets", "int", False),
                   ("possession", "float", False), ("shots", "int", False), ("shots_on_target", "int", False),
                   ("league", "string", True)],
    "matches": [("match_id", "string", True), ("date", "date", True), ("league", "string", True),
                ("season", "string", True), ("home_team_id", "string", True), ("away_team_id", "string", True),
                ("home_score", "int", True), ("away_score", "int", True), ("result", "string", True)],
    "transfers": [("transfer_id", "string", True), ("player_id", "string", True), ("transfer_date", "date", False),
                  ("from_team_id", "string", False), ("to_team_id", "string", False),
                  ("transfer_fee", "float", False)],
}

PRIMARY_KEYS = {"players": ["player_id"], "teams": ["team_id"], "player_stats": ["player_id", "season", "league"],
                "team_stats": ["team_id", "season", "league"], "matches": ["match_id"], "transfers": ["transfer_id"]}

# (bảng, cột) -> (bảng được tham chiếu, cột)
FOREIGN_KEYS = [("players", "team_id", "teams", "team_id"),
                ("player_stats", "player_id", "players", "player_id"),
                ("team_stats", "team_id", "teams", "team_id"),
                ("matches", "home_team_id", "teams", "team_id"),
                ("matches", "away_team_id", "teams", "team_id"),
                ("transfers", "player_id", "players", "player_id"),
                ("transfers", "from_team_id", "teams", "team_id"),
                ("transfers", "to_team_id", "teams", "team_id")]

SEASON_RE = re.compile(r"^\d{4}/\d{4}$")


def columns_of(table: str) -> list[str]:
    return [c for c, _, _ in SCHEMA[table]]


def empty_table(table: str) -> pd.DataFrame:
    return enforce_schema(pd.DataFrame(), table)


def enforce_schema(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """Đúng tên + đúng thứ tự cột + đúng kiểu. Cột thiếu -> giá trị thiếu (không phải 0/Unknown)."""
    out = pd.DataFrame(index=df.index)
    for name, typ, _ in SCHEMA[table]:
        s = df[name] if name in df.columns else pd.Series([np.nan] * len(df), index=df.index)
        if typ == "string":
            out[name] = s.astype("string")
        elif typ == "int":
            out[name] = pd.to_numeric(s, errors="coerce").round().astype("Int64")
        elif typ == "float":
            out[name] = pd.to_numeric(s, errors="coerce").astype(float)
        elif typ == "date":
            d = pd.to_datetime(s, errors="coerce")
            out[name] = d.dt.strftime("%Y-%m-%d").astype("string")      # ISO yyyy-mm-dd
    return out.reset_index(drop=True)


def validate_table(df: pd.DataFrame, table: str) -> list[str]:
    """Checklist 'Schema' + 'ID' + 'Dữ liệu' của scraper_guide mục 11."""
    issues, expected = [], columns_of(table)
    if list(df.columns) != expected:
        issues.append(f"[{table}] sai cột/thứ tự. Cần {expected}, có {list(df.columns)}")
        return issues
    for name, typ, required in SCHEMA[table]:
        if required and df[name].isna().any():
            issues.append(f"[{table}] cột bắt buộc '{name}' có {int(df[name].isna().sum())} giá trị thiếu")
    pk = PRIMARY_KEYS[table]
    if len(df) and df.duplicated(pk).any():
        issues.append(f"[{table}] {int(df.duplicated(pk).sum())} dòng trùng khóa chính {pk}")
    if "season" in df.columns and len(df) and not df["season"].dropna().map(lambda x: bool(SEASON_RE.match(str(x)))).all():
        issues.append(f"[{table}] season phải có dạng 2024/2025")
    if table == "matches" and len(df):
        if not df["result"].dropna().isin(["H", "D", "A"]).all():
            issues.append("[matches] result chỉ được là H, D hoặc A")
        calc = np.where(df["home_score"] > df["away_score"], "H", np.where(df["home_score"] < df["away_score"], "A", "D"))
        if (calc != df["result"].astype(str).values).any():
            issues.append("[matches] result không khớp tỷ số")
    return issues


def validate_foreign_keys(tables: dict[str, pd.DataFrame]) -> list[str]:
    """Mọi ID tham chiếu phải tồn tại ở bảng gốc (cùng một thực thể -> cùng một ID)."""
    issues = []
    for t, col, rt, rcol in FOREIGN_KEYS:
        if t not in tables or rt not in tables or tables[t].empty:
            continue
        ref = set(tables[rt][rcol].dropna().astype(str))
        vals = tables[t][col].dropna().astype(str)
        bad = vals[~vals.isin(ref)]
        if len(bad):
            issues.append(f"[{t}.{col}] {len(bad)} giá trị không có trong {rt}.{rcol} (vd. {bad.iloc[0]})")
    return issues
