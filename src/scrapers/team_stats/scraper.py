"""NGƯỜI 4 — bảng `team_stats`.

* wins/draws/losses/goals/points/clean_sheets: TÍNH TỪ bảng `matches` (nguồn duy nhất -> luôn khớp nhau).
* possession, shots, shots_on_target: bảng đội của FBref ('stats_squads_standard_for', 'stats_squads_shooting_for').
  Nếu nguồn không có -> giá trị thiếu (không điền 0).
"""
from __future__ import annotations

import pandas as pd

from config import settings
from src.common.fetcher import Fetcher, ScrapeBlocked
from src.common.ids import make_team_id
from src.common.logging_utils import log
from src.common.schema import enforce_schema, validate_table
from src.common.table_spec import TableSpec, cols
from src.scrapers.base import scrape_spec

SPEC_SQUAD_POSSESSION = TableSpec(key="squad_possession", page="stats", table_id="stats_squads_standard_for",
                                  owner=4, with_player=False, columns=[(None, "Poss", "Poss")])
SPEC_SQUAD_SHOOTING = TableSpec(key="squad_shooting", page="shooting", table_id="stats_squads_shooting_for",
                                owner=4, with_player=False, columns=cols("Standard", "", "Sh", "SoT"))


def compute_from_matches(matches: pd.DataFrame) -> pd.DataFrame:
    """Bảng thành tích mỗi đội, tính từ tất cả trận đã đá (đội nhà + đội khách)."""
    m = matches.copy()
    for c in ("home_score", "away_score"):
        m[c] = pd.to_numeric(m[c])
    home = pd.DataFrame({"team_id": m["home_team_id"], "gf": m["home_score"], "ga": m["away_score"]})
    away = pd.DataFrame({"team_id": m["away_team_id"], "gf": m["away_score"], "ga": m["home_score"]})
    g = pd.concat([home, away], ignore_index=True)
    g["w"], g["d"], g["l"] = (g.gf > g.ga).astype(int), (g.gf == g.ga).astype(int), (g.gf < g.ga).astype(int)
    g["cs"] = (g.ga == 0).astype(int)
    t = g.groupby("team_id").agg(matches=("gf", "size"), wins=("w", "sum"), draws=("d", "sum"), losses=("l", "sum"),
                                 goals_for=("gf", "sum"), goals_against=("ga", "sum"), clean_sheets=("cs", "sum"))
    t["goal_difference"] = t["goals_for"] - t["goals_against"]
    t["points"] = 3 * t["wins"] + t["draws"]
    return t.reset_index()


def scrape_team_stats(fetcher: Fetcher, matches: pd.DataFrame) -> pd.DataFrame:
    t = compute_from_matches(matches) if len(matches) else pd.DataFrame({"team_id": []})
    extra = []
    for spec in (SPEC_SQUAD_POSSESSION, SPEC_SQUAD_SHOOTING):
        try:
            extra.append(scrape_spec(fetcher, spec))
        except (ScrapeBlocked, FileNotFoundError) as exc:
            log(f"   !! BỎ QUA {spec.key}: {str(exc).splitlines()[0]}")
    for e in extra:
        if e.empty:
            continue
        e = e.copy()
        e["team_id"] = e["Squad"].map(make_team_id)
        t = t.merge(e.drop(columns=["Squad"]), on="team_id", how="outer")
    t = t.rename(columns={"Poss": "possession", "Sh": "shots", "SoT": "shots_on_target"})
    t["season"], t["league"] = settings.SEASON, settings.LEAGUE
    out = enforce_schema(t, "team_stats")
    for issue in validate_table(out, "team_stats"):
        log(f"   ⚠ {issue}")
    log(f"[Người 4] team_stats: {len(out)} đội")
    return out
