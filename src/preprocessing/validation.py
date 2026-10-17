"""Kiểm tra dữ liệu theo checklist integration của Người 1."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from config.settings import MIN_MINUTES
from src.common.io_utils import KEY_COLS


def validate_dataset(df: pd.DataFrame, expected_cols: Optional[list[str]] = None,
                     check_min: bool = True) -> list[str]:
    """Kiểm tra theo checklist integration của người 1. Trả về danh sách vấn đề."""
    issues = []
    if df.empty:
        return ["Dataset rỗng"]
    if df.duplicated(subset=KEY_COLS).any():
        issues.append(f"Có {int(df.duplicated(subset=KEY_COLS).sum())} cầu thủ trùng (Player, Squad)")
    if expected_cols:
        miss = [c for c in expected_cols if c not in df.columns]
        if miss:
            issues.append(f"Thiếu {len(miss)} cột so với schema: {miss[:5]}")
    if check_min and "Min" in df.columns and (pd.to_numeric(df["Min"], errors="coerce") <= MIN_MINUTES).any():
        issues.append(f"Có cầu thủ Min <= {MIN_MINUTES} (vi phạm điều kiện lọc)")
    for c in ("Player", "Squad"):
        if c in df.columns and df[c].isna().any():
            issues.append(f"Cột {c} có giá trị trống")
    allna = [c for c in df.columns if df[c].isna().all()]
    if allna:
        issues.append(f"{len(allna)} cột toàn N/a (nguồn không có): {allna[:6]}{' ...' if len(allna) > 6 else ''}")
    return issues
