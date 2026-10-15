"""Xuất sản phẩm NỘP của đề bài: data/final/results.csv (lọc Min > 90, sắp xếp, 'N/a')."""
from __future__ import annotations

import pandas as pd

from src.common.io_utils import save_with_na
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.preprocessing.filters import filter_min_minutes, sort_players
from src.preprocessing.validation import validate_dataset
from src.scrapers.player_stats.scraper import expected_result_columns


def export_results(extended: pd.DataFrame) -> pd.DataFrame:
    expected = expected_result_columns()
    df = filter_min_minutes(extended)[expected]
    df = sort_players(df)
    for issue in validate_dataset(df, expected):
        log(f"   ⚠ kiểm tra dữ liệu: {issue}")
    save_with_na(df, PATHS.results)
    log(f"== Đã lưu {PATHS.results}  ({len(df)} cầu thủ × {df.shape[1]} cột; thiếu = 'N/a') ==")
    return df
