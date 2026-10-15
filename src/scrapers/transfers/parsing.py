"""NGƯỜI 10 — Tiện ích đọc tiền chuyển nhượng và bảng chuyển nhượng HTML."""
from __future__ import annotations

import io
import re
import math

import numpy as np
import pandas as pd

from src.preprocessing.cleaning import normalize_player_name


def parse_money(text) -> float:
    """'€45.2M' -> 45.2 ; '€800K' -> 0.8 ; '£1.2B' -> 1200 ; 'Free'/'-' -> NaN   (đơn vị: triệu)."""
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return np.nan
    if isinstance(text, (int, float)):
        return float(text)
    m = re.search(r"([\d.,]+)\s*([KkMmBb]?)", str(text).replace(" ", ""))
    if not m or not re.search(r"\d", m.group(1)):
        return np.nan
    num = float(m.group(1).replace(",", ""))
    return num * {"": 1e-6, "k": 1e-3, "m": 1.0, "b": 1e3}[m.group(2).lower()]


def _flat(columns) -> list[str]:
    return [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in columns]


def parse_transfer_html(html: str) -> pd.DataFrame:
    """Tìm bảng có cột cầu thủ + cột phí/giá trị. Trả về: Player, Date, From, To, Raw_Fee, Fee_M.

    Chấp nhận 2 dạng bảng: (1) danh sách chuyển nhượng (Player, Date, From, To, Fee);
    (2) danh sách cầu thủ kèm giá trị (Player, Team, Value) -> Team được coi là đội mới (To).
    """
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        return pd.DataFrame()
    for t in tables:
        t = t.copy()
        t.columns = _flat(t.columns)
        low = {c.lower().strip(): c for c in t.columns}
        pick = lambda pred: next((low[c] for c in low if pred(c)), None)
        pcol = pick(lambda c: "player" in c or c == "name")
        fcol = pick(lambda c: any(w in c for w in ("fee", "value", "price", "etv")))
        if not (pcol and fcol):
            continue
        dcol = pick(lambda c: "date" in c)
        from_col = pick(lambda c: c.startswith("from") or "previous" in c or "left" in c)
        to_col = pick(lambda c: c in ("to", "to club", "new club", "team", "club", "squad") or c.startswith("to "))
        out = pd.DataFrame({
            "Player": t[pcol].astype(str).str.split("\n").str[0].map(normalize_player_name),
            "Date": t[dcol].astype(str) if dcol else np.nan,
            "From": t[from_col].astype(str).str.strip() if from_col else np.nan,
            "To": t[to_col].astype(str).str.strip() if to_col else np.nan,
            "Raw_Fee": t[fcol].astype(str)})
        out["Fee_M"] = out["Raw_Fee"].map(parse_money)
        return out[out["Player"].ne("") & out["Player"].ne("nan")].reset_index(drop=True)
    return pd.DataFrame()
