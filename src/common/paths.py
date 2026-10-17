"""Đường dẫn thư mục/tệp của project (theo khung: data/raw -> data/processed -> data/final)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Paths:
    def __init__(self, base: Path | None = None):
        self.set(base or ROOT / "data")

    def set(self, base) -> None:
        self.base = Path(base)
        self.raw = self.base / "raw"                 # HTML/CSV gốc, KHÔNG ghi đè
        self.processed = self.base / "processed"     # 6 bảng chuẩn + bảng mở rộng (NaN = thiếu)
        self.final = self.base / "final"             # sản phẩm nộp: results.csv, results2.csv, hình
        self.plots = self.final / "plots"
        self.models = self.final / "models"
        # 6 bảng chuẩn (docs/DATA_DICTIONARY.md)
        self.tables = {t: self.processed / f"{t}.csv" for t in
                       ("players", "teams", "player_stats", "team_stats", "matches", "transfers")}
        self.extended = self.processed / "player_stats_extended.csv"   # xem docs/EXTENDED_STATS.md
        self.sources = self.processed / "sources.csv"
        self.results = self.final / "results.csv"
        self.results2 = self.final / "results2.csv"

    def make(self) -> None:
        for p in (self.raw, self.processed, self.final, self.plots, self.models):
            p.mkdir(parents=True, exist_ok=True)


PATHS = Paths()
