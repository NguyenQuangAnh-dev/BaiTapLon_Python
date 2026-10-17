"""Nhật ký nguồn dữ liệu -> data/processed/sources.csv (mục 3 của kế hoạch phân công)."""
import datetime as dt

import pandas as pd

from config import settings
from src.common.paths import PATHS

_SOURCES: list[dict] = []


def log_source(module: str, attribute: str, website: str, url: str, notes: str = "") -> None:
    _SOURCES.append({"Module": module, "Attribute": attribute, "Website": website, "URL": url,
                     "Season": settings.SEASON,
                     "CollectedAt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "Notes": notes})


def write_sources() -> None:
    if _SOURCES:
        PATHS.processed.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_SOURCES).to_csv(PATHS.sources, index=False, encoding="utf-8-sig")
