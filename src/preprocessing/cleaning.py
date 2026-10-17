"""Chuẩn hóa tên người/đội và chuyển chuỗi -> số (NGƯỜI 1).

Quy tắc: tên giữ DẤU ở cột hiển thị (Player), còn khóa ghép (player_key/team_key) bỏ dấu và chữ hoa.
'N/a' / chuỗi rỗng -> NaN, TUYỆT ĐỐI không đổi thành 0.
"""
from __future__ import annotations

import math
import re
import unicodedata

import numpy as np
import pandas as pd


_SPECIAL = str.maketrans({"ø": "o", "Ø": "O", "đ": "d", "Đ": "D", "ł": "l", "Ł": "L",
                          "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ı": "i"})


def strip_accents(text: str) -> str:
    text = str(text).translate(_SPECIAL)
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize_player_name(name) -> str:
    """Player_raw -> Player_standard (bỏ khoảng trắng thừa, chuẩn Unicode, GIỮ dấu)."""
    if name is None or (isinstance(name, float) and math.isnan(name)):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(name))).strip()


def _key(text) -> str:
    text = strip_accents(normalize_player_name(text)).lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def player_key(name) -> str:
    """Khóa so khớp tên: không dấu, không ký tự đặc biệt, chữ thường."""
    return _key(name)


def team_key(name) -> str:
    return _key(name)


def to_number(series: pd.Series) -> pd.Series:
    """'1,234' -> 1234 ; '45.2%' -> 45.2 ; 'N/a' / '' -> NaN (KHÔNG thành 0)."""
    s = series.astype(str).str.strip()
    s = s.str.replace(",", "", regex=False).str.replace("%", "", regex=False)
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "<NA>": np.nan,
                   "N/a": np.nan, "NA": np.nan, "-": np.nan})
    return pd.to_numeric(s, errors="coerce")


def clean_age(value):
    """FBref ghi tuổi dạng '24-123' (24 tuổi 123 ngày) -> 24."""
    m = re.match(r"\s*(\d+)", str(value))
    return int(m.group(1)) if m else np.nan


def clean_nation(value) -> str:
    """'eng ENG' -> 'ENG'."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    parts = str(value).split()
    return parts[-1].upper() if parts else ""
