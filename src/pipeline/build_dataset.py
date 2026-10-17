"""NGƯỜI 1 — PHẦN I trọn gói: thu thập -> chuẩn hóa -> 6 bảng chuẩn -> kiểm tra schema/ID -> results.csv."""
from __future__ import annotations

import pandas as pd

from config import settings
from src.common.fetcher import Fetcher, ScrapeBlocked
from src.common.io_utils import read_table, save_csv
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.common.schema import empty_table, validate_foreign_keys, validate_table
from src.common.sources import write_sources
from src.pipeline.export_results import export_results
from src.preprocessing.canonical_tables import build_player_stats
from src.scrapers.matches.scraper import scrape_matches
from src.scrapers.player_stats.scraper import scrape_player_stats
from src.scrapers.players.scraper import scrape_players
from src.scrapers.team_stats.scraper import scrape_team_stats
from src.scrapers.teams.scraper import scrape_teams


def validate_all(tables: dict[str, pd.DataFrame]) -> list[str]:
    issues = []
    for name, df in tables.items():
        issues += validate_table(df, name)
    return issues + validate_foreign_keys(tables)


def load_tables() -> dict[str, pd.DataFrame]:
    """Đọc 6 bảng chuẩn đã lưu (thiếu bảng nào -> bảng rỗng đúng schema)."""
    out = {}
    for name in PATHS.tables:
        try:
            out[name] = read_table(name)
        except FileNotFoundError:
            out[name] = empty_table(name)
    return out


def run_scrape(fetcher: Fetcher) -> dict[str, pd.DataFrame]:
    PATHS.make()
    log(f"== PHẦN I: Thu thập dữ liệu mùa {settings.SEASON} (nguồn: {fetcher.source}) ==")
    extended = scrape_player_stats(fetcher)
    save_csv(extended, PATHS.extended)

    teams = scrape_teams(fetcher, extended)
    players = scrape_players(extended)
    player_stats = build_player_stats(extended)
    try:
        matches = scrape_matches(fetcher)
    except (ScrapeBlocked, FileNotFoundError) as exc:
        log(f"   !! BỎ QUA matches: {str(exc).splitlines()[0]}")
        matches = empty_table("matches")
    team_stats = scrape_team_stats(fetcher, matches)

    tables = {"players": players, "teams": teams, "player_stats": player_stats,
              "team_stats": team_stats, "matches": matches}
    try:                                                     # giữ transfers đã thu thập trước đó (nếu có)
        tables["transfers"] = read_table("transfers")
    except FileNotFoundError:
        tables["transfers"] = empty_table("transfers")
    for name, df in tables.items():
        save_csv(df, PATHS.tables[name])
    for issue in validate_all(tables):
        log(f"   ⚠ {issue}")
    export_results(extended)
    write_sources()
    return tables
