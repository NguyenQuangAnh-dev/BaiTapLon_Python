"""Đọc/ghi CSV. Quy ước: tầng processed dùng ô TRỐNG (NaN/NULL); chỉ file nộp cuối dùng 'N/a'."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.settings import NA
from src.common.paths import PATHS

ID_TEXT_COLS = ["Player", "Nation", "Squad", "Pos", "player_id", "team_id"]   # cột chữ (không phải thống kê số)
KEY_COLS = ["Player", "Squad"]


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Ghi tầng processed: thiếu = ô trống (NULL), đúng scraper_guide mục 8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def save_with_na(df: pd.DataFrame, path: Path) -> None:
    """Ghi file NỘP: ô thiếu -> 'N/a' đúng yêu cầu của đề bài."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.astype(object).where(df.notna(), NA)
    out.to_csv(path, index=False, encoding="utf-8-sig")


def stat_columns(df: pd.DataFrame) -> list[str]:
    """Các cột thống kê số = mọi cột trừ Player/Nation/Squad/Pos/player_id/team_id."""
    return [c for c in df.columns if c not in ID_TEXT_COLS]


def _read(path: Path, na_values) -> pd.DataFrame:
    from src.preprocessing.cleaning import to_number
    df = pd.read_csv(path, na_values=na_values, keep_default_na=False, dtype={"player_id": str, "team_id": str})
    for c in stat_columns(df):
        if df[c].dtype == object:
            df[c] = to_number(df[c])
    return df


def load_results(path: Path | None = None) -> pd.DataFrame:
    """Đọc data/final/results.csv ('N/a' -> NaN để tính toán). Người 8, 9, 10 dùng hàm này."""
    path = Path(path) if path else PATHS.results
    if not path.exists():
        raise FileNotFoundError(f"Không thấy {path}. Hãy chạy `python main.py scrape` (hoặc `demo`) trước.")
    return _read(path, [NA, ""])


def load_extended(path: Path | None = None) -> pd.DataFrame:
    """Đọc bảng mở rộng (có player_id/team_id) ở data/processed."""
    path = Path(path) if path else PATHS.extended
    if not path.exists():
        raise FileNotFoundError(f"Không thấy {path}. Hãy chạy `python main.py scrape` (hoặc `demo`) trước.")
    return _read(path, [NA, ""])


def read_table(name: str) -> pd.DataFrame:
    """Đọc 1 trong 6 bảng chuẩn từ data/processed."""
    path = PATHS.tables[name]
    if not path.exists():
        raise FileNotFoundError(f"Chưa có bảng {name}: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
