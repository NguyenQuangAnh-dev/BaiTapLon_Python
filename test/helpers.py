"""Hàm hỗ trợ test: tạo HTML mẫu kiểu FBref và kiểm tra một TableSpec."""
from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.common.fbref_parser import extract_by_spec, read_fbref_table
from src.common.table_spec import TableSpec
from src.pipeline.demo_data import demo_players, make_fake_html


def _fake_raw(spec: TableSpec, n: int = 5) -> pd.DataFrame:
    players = demo_players(1, n)
    for p in players:
        p["base"] = "GK" if spec.key == "goalkeeper" else p["base"]
    raw = read_fbref_table(make_fake_html(spec, players, wrap_comment=True), spec.table_id)
    assert raw is not None, "parser không đọc được bảng mẫu"
    return raw


def selftest_spec(spec: TableSpec, must_numeric: Iterable[str] = (), n: int = 5) -> None:
    """Test chung cho mọi scraper: parse HTML mẫu -> đủ cột, đúng kiểu, không trùng Player."""
    raw = _fake_raw(spec, n)
    df, missing = extract_by_spec(raw, spec)
    assert not missing, f"[{spec.key}] thiếu cột: {missing}"
    assert len(df) == n, f"[{spec.key}] số dòng {len(df)} != {n} (dòng tiêu đề lặp chưa bị loại?)"
    assert list(df.columns) == spec.out_columns(), f"[{spec.key}] sai thứ tự/tên cột"
    for c in must_numeric:
        assert pd.api.types.is_numeric_dtype(df[c]), f"[{spec.key}] cột {c} chưa là số"
    assert not df.duplicated(["Player", "Squad"]).any(), f"[{spec.key}] trùng Player"
