"""Đọc bảng HTML của FBref và trích cột theo TableSpec."""
from __future__ import annotations

import io
from typing import Optional

import numpy as np
import pandas as pd

from src.common.table_spec import TableSpec
from src.preprocessing.cleaning import clean_age, clean_nation, normalize_player_name, to_number


def read_fbref_table(html: str, table_id: str, levels: int = 2) -> Optional[pd.DataFrame]:
    """Đọc bảng theo id (kể cả khi FBref giấu bảng trong chú thích <!-- -->).
    Trả DataFrame có cột MultiIndex (nhóm, thống kê); bảng 1 dòng tiêu đề -> nhóm = ''."""
    html = html.replace("<!--", "").replace("-->", "")
    try:
        tables = pd.read_html(io.StringIO(html), attrs={"id": table_id}, header=[0, 1] if levels == 2 else 0)
    except (ValueError, IndexError):
        return None
    if not tables:
        return None
    df = tables[0]
    if isinstance(df.columns, pd.MultiIndex):
        newcols = [("" if str(g).startswith("Unnamed") else str(g).strip(), str(s).strip()) for g, s in df.columns]
    else:
        newcols = [("", str(c).strip()) for c in df.columns]
    df.columns = pd.MultiIndex.from_tuples(newcols)
    return df


def find_col(columns, group: Optional[str], stat: str) -> Optional[int]:
    """Vị trí cột theo (nhóm, thống kê): ưu tiên khớp chính xác, sau đó khớp tiền tố."""
    if group is None:
        for i, (_, s) in enumerate(columns):
            if s == stat:
                return i
        return None
    want = group.lower()
    for i, (g, s) in enumerate(columns):
        if s == stat and g.lower() == want:
            return i
    for i, (g, s) in enumerate(columns):
        if s == stat and g and (g.lower().startswith(want) or want.startswith(g.lower())):
            return i
    return None


def extract_by_spec(raw: pd.DataFrame, spec: TableSpec) -> tuple[pd.DataFrame, list[str]]:
    """Bảng thô FBref -> DataFrame đúng tên cột chuẩn. Trả thêm danh sách cột THIẾU (sẽ là NaN)."""
    columns = list(raw.columns)
    anchor = spec.anchor_name
    aidx = find_col(columns, None, anchor)
    if aidx is None:
        raise ValueError(f"Bảng {spec.table_id} không có cột {anchor}")
    s = raw.iloc[:, aidx].astype(str)
    keep = ~s.isin([anchor, "nan", ""]) & ~s.str.contains("Total", na=False)
    raw = raw.loc[keep.values].reset_index(drop=True)

    out, missing = {}, []
    for group, stat, name in spec.full_columns():
        idx = find_col(columns, group, stat)
        if idx is None:
            out[name] = pd.Series([np.nan] * len(raw), dtype=float)
            missing.append(name)
            continue
        col = raw.iloc[:, idx]
        if name == "Player":
            out[name] = col.map(normalize_player_name)
        elif name == "Nation":
            out[name] = col.map(clean_nation).replace("", np.nan)
        elif name in ("Squad", "Pos"):
            out[name] = col.astype(str).str.strip().replace({"nan": np.nan, "": np.nan})
        elif name in spec.text_cols:
            out[name] = col.astype(str).str.strip().replace({"nan": np.nan, "": np.nan})
        elif name == "Age":
            out[name] = col.map(clean_age)
        else:
            out[name] = to_number(col)
    return pd.DataFrame(out), missing
