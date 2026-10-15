"""Hàm dùng chung cho mọi scraper: tải trang -> đọc bảng -> trích cột đúng tên chuẩn."""
from __future__ import annotations

import pandas as pd

from src.common.fbref_parser import extract_by_spec, read_fbref_table
from src.common.fetcher import Fetcher
from src.common.logging_utils import log
from src.common.sources import log_source
from src.common.table_spec import TableSpec


def scrape_spec(fetcher: Fetcher, spec: TableSpec) -> pd.DataFrame:
    """Thiếu bảng/cột -> giá trị thiếu (NaN), KHÔNG tự điền 0."""
    log(f"[Người {spec.owner}] Thu thập '{spec.key}' (bảng {spec.table_id})")
    html = fetcher.get_html(spec.page)
    raw = read_fbref_table(html, spec.table_id, spec.levels)
    if raw is None:
        log(f"   ! Không tìm thấy bảng {spec.table_id} -> toàn bộ cột sẽ thiếu (N/a ở file nộp)")
        df = pd.DataFrame({c: [] for c in spec.out_columns()})
        missing = [c for c in spec.out_columns() if c not in ("Player", "Squad")]
    else:
        df, missing = extract_by_spec(raw, spec)
    if missing:
        log(f"   ! {len(missing)} cột không có trong nguồn: {', '.join(missing[:6])}{' ...' if len(missing) > 6 else ''}")
    website = "web.archive.org (bản lưu fbref.com)" if fetcher.source == "wayback" else "fbref.com"
    log_source(spec.key, ", ".join(spec.out_columns()[:4]) + " ...", website, fetcher.urls.get(spec.page, ""),
               notes=f"{len(df)} dòng; thiếu {len(missing)} cột")
    return df
