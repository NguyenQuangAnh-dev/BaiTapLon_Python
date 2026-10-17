"""NGƯỜI 8 — Phần II: top/bottom 3 và bảng results2 (median/mean/std)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import STD_DDOF
from src.common.io_utils import stat_columns


def numeric_stats(df: pd.DataFrame) -> list[str]:
    """Tự động xác định cột thống kê số có ít nhất 1 giá trị."""
    out = []
    for c in stat_columns(df):
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().any():
            out.append(c)
    return out


def top_bottom(df: pd.DataFrame, stats: list[str], n: int = 3) -> pd.DataFrame:
    """3 cầu thủ cao nhất và thấp nhất cho MỖI thống kê (bỏ qua N/a)."""
    rows = []
    for s in stats:
        sub = df[["Player", "Squad", s]].dropna(subset=[s])
        if sub.empty:
            continue
        for kind, part in (("Top", sub.nlargest(n, s)), ("Bottom", sub.nsmallest(n, s))):
            for rank, (_, r) in enumerate(part.iterrows(), 1):
                rows.append({"Statistic": s, "Type": kind, "Rank": rank,
                             "Player": r["Player"], "Squad": r["Squad"], "Value": r[s]})
    return pd.DataFrame(rows)


def build_results2(df: pd.DataFrame, stats: list[str]) -> pd.DataFrame:
    """Median/Mean/Std của mỗi thống kê: dòng 0 = 'all', các dòng sau = từng đội."""
    labels = ["all"] + sorted(df["Squad"].dropna().unique())
    records = []
    for label in labels:
        sub = df if label == "all" else df[df["Squad"] == label]
        row = {"Team": label}
        for s in stats:
            v = pd.to_numeric(sub[s], errors="coerce").dropna()
            row[f"Median of {s}"] = v.median() if len(v) else np.nan
            row[f"Mean of {s}"] = v.mean() if len(v) else np.nan
            row[f"Std of {s}"] = v.std(ddof=STD_DDOF) if len(v) > STD_DDOF else np.nan
        records.append(row)
    out = pd.DataFrame(records).round(3)
    out.insert(0, "", range(len(out)))              # cột chỉ số 0, 1, ..., n như mẫu của đề
    return out
