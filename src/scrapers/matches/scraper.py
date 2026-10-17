"""NGƯỜI 3 — bảng `matches` từ trang lịch thi đấu/kết quả của FBref.

Chỉ lấy trận ĐÃ ĐÁ (có tỷ số). result: H (đội nhà thắng) / D (hòa) / A (đội khách thắng).
"""
from __future__ import annotations


import numpy as np
import pandas as pd

from config import settings
from src.common.fetcher import Fetcher
from src.common.ids import make_team_id
from src.common.logging_utils import log
from src.common.schema import enforce_schema, validate_table
from src.common.table_spec import TableSpec
from src.scrapers.base import scrape_spec


def schedule_spec() -> TableSpec:
    slug = settings.season_slug()
    return TableSpec(
        key="matches", page="schedule", table_id=f"sched_{slug}_{settings.FBREF_COMP_ID}_1", owner=3,
        with_player=False, levels=1, anchor="Date",
        columns=[(None, "Date", "Date"), (None, "Home", "Home"), (None, "Score", "Score"), (None, "Away", "Away")],
        text_cols=("Date", "Home", "Score", "Away"))


def build_matches(raw: pd.DataFrame) -> pd.DataFrame:
    """raw có cột Date, Home, Score, Away (dạng chữ) -> bảng matches đúng schema."""
    d = raw.dropna(subset=["Date", "Home", "Away", "Score"]).copy()
    sc = d["Score"].astype(str).str.extract(r"(\d+)\s*[–—\-]\s*(\d+)")        # bỏ qua trận chưa đá / dòng ngăn cách
    d = d.loc[sc.notna().all(axis=1)].copy()
    sc = sc.loc[d.index].astype(int)
    d["home_score"], d["away_score"] = sc[0].values, sc[1].values
    d["date"] = pd.to_datetime(d["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    d = d.dropna(subset=["date"])
    d["home_team_id"] = d["Home"].map(make_team_id)
    d["away_team_id"] = d["Away"].map(make_team_id)
    d["result"] = np.where(d["home_score"] > d["away_score"], "H", np.where(d["home_score"] < d["away_score"], "A", "D"))
    d["match_id"] = [f"{dt}_{h}_{a}" for dt, h, a in zip(d["date"], d["home_team_id"], d["away_team_id"])]
    d["season"], d["league"] = settings.SEASON, settings.LEAGUE
    return enforce_schema(d.sort_values(["date", "match_id"]), "matches")


def scrape_matches(fetcher: Fetcher) -> pd.DataFrame:
    matches = build_matches(scrape_spec(fetcher, schedule_spec()))
    for issue in validate_table(matches, "matches"):
        log(f"   ⚠ {issue}")
    if len(matches) and len(matches) != 380:
        log(f"   ⚠ Có {len(matches)} trận (một mùa Premier League đầy đủ có 380 trận; mùa đang diễn ra thì ít hơn)")
    log(f"[Người 3] matches: {len(matches)} trận")
    return matches
