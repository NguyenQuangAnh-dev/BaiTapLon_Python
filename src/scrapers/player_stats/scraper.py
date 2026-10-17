"""NGƯỜI 1 (tích hợp) — gom 10 bảng thống kê cầu thủ của FBref do Người 2–7 phụ trách.

Đầu ra: bảng MỞ RỘNG `player_stats_extended` (mọi cầu thủ, KHÔNG lọc phút; có player_id, team_id).
Bảng chuẩn `players`/`player_stats` và file nộp `results.csv` đều dẫn xuất từ bảng này.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from src.common.fetcher import Fetcher, ScrapeBlocked
from src.common.ids import assign_ids
from src.common.logging_utils import log
from src.common.sources import log_source
from src.preprocessing.merge import add_keys, apply_supplements, merge_modules
from src.scrapers.player_stats.basic import SPEC_BASIC, scrape_basic
from src.scrapers.player_stats.defense import SPEC_DEFENSE, scrape_defense
from src.scrapers.player_stats.gca import SPEC_SCA_GCA, scrape_sca_gca
from src.scrapers.player_stats.goalkeeper import SPEC_GOALKEEPER, scrape_goalkeeper
from src.scrapers.player_stats.misc import SPEC_MISC, scrape_misc
from src.scrapers.player_stats.passing import SPEC_PASSING, scrape_passing
from src.scrapers.player_stats.passing_types import SPEC_PASS_TYPES, scrape_pass_types
from src.scrapers.player_stats.playing_time import SPEC_PLAYING_TIME, scrape_playing_time
from src.scrapers.player_stats.possession import SPEC_POSSESSION, scrape_possession
from src.scrapers.player_stats.shooting import SPEC_SHOOTING, scrape_shooting

# Thứ tự cột trong results.csv: theo thứ tự liệt kê của đề bài
ALL_SPECS = [SPEC_BASIC, SPEC_GOALKEEPER, SPEC_SHOOTING, SPEC_PASSING, SPEC_PASS_TYPES,
             SPEC_SCA_GCA, SPEC_DEFENSE, SPEC_POSSESSION, SPEC_PLAYING_TIME, SPEC_MISC]
SCRAPERS: dict[str, Callable[[Fetcher], pd.DataFrame]] = {
    "basic": scrape_basic, "goalkeeper": scrape_goalkeeper, "shooting": scrape_shooting,
    "passing": scrape_passing, "pass_types": scrape_pass_types, "sca_gca": scrape_sca_gca,
    "defense": scrape_defense, "possession": scrape_possession,
    "playing_time": scrape_playing_time, "misc": scrape_misc,
}


def expected_result_columns() -> list[str]:
    """Các cột thống kê theo thứ tự của đề (Player, Nation, Squad, Pos, Age, ...)."""
    seen, out = set(), []
    for spec in ALL_SPECS:
        for c in spec.out_columns():
            if c not in seen:
                seen.add(c)
                out.append(c)
    return out


def scrape_player_stats(fetcher: Fetcher) -> pd.DataFrame:
    """Thu thập 10 bảng -> ghép theo (Player, Squad) -> bảng mở rộng (NaN = thiếu)."""
    frames: dict[str, pd.DataFrame] = {}
    for key, fn in SCRAPERS.items():
        try:
            frames[key] = fn(fetcher)
        except (ScrapeBlocked, FileNotFoundError) as exc:
            if key == "basic":
                raise                                    # không có danh sách cầu thủ thì không làm tiếp được
            log(f"   !! BỎ QUA module '{key}': {str(exc).splitlines()[0]}  -> các cột sẽ thiếu")
            log_source(key, "(không lấy được)", "-", "", notes=str(exc).splitlines()[0])
    basic = frames["basic"].dropna(subset=["Player", "Squad"])
    master = basic.sort_values("Min", ascending=False, na_position="last")
    master = add_keys(master).drop_duplicates(["_pk", "_sk"]).drop(columns=["_pk", "_sk"])
    master = assign_ids(master)
    merged = merge_modules(master, [frames[k] for k in SCRAPERS if k != "basic" and k in frames])
    merged = apply_supplements(merged)
    expected = expected_result_columns()
    for c in expected:
        if c not in merged.columns:
            merged[c] = np.nan
    return merged[["player_id", "team_id"] + expected].reset_index(drop=True)
