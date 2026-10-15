"""Ghép các bảng thống kê theo (Player, Squad) chuẩn hóa — KHÔNG ghép theo thứ tự dòng (NGƯỜI 1)."""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from config.settings import NA
from src.common.io_utils import KEY_COLS
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.common.sources import log_source
from src.preprocessing.cleaning import player_key, team_key, to_number


def add_keys(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_pk"] = df["Player"].map(player_key)
    df["_sk"] = df["Squad"].map(team_key)
    return df


def merge_modules(master: pd.DataFrame, frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Ghép theo (Player, Squad) chuẩn hóa — KHÔNG ghép theo thứ tự dòng."""
    out = add_keys(master).drop_duplicates(subset=["_pk", "_sk"], keep="first")
    for f in frames:
        if f is None or f.empty:
            continue
        f = add_keys(f)
        dup = f.duplicated(subset=["_pk", "_sk"], keep="first").sum()
        if dup:
            log(f"   ! bỏ {dup} dòng trùng khóa trong một module")
        f = f.drop_duplicates(subset=["_pk", "_sk"], keep="first")
        new_cols = [c for c in f.columns if c not in out.columns]
        out = out.merge(f[["_pk", "_sk"] + new_cols], on=["_pk", "_sk"], how="left")
    return out.drop(columns=["_pk", "_sk"])


def apply_supplements(df: pd.DataFrame) -> pd.DataFrame:
    """Điền các ô còn N/a từ data/raw/supplement_*.csv (nguồn khác, đúng tên cột chuẩn).

    Dùng khi nguồn chính thiếu cột (ví dụ FBref đã gỡ xG). File CSV cần có cột Player,
    Squad và các cột theo tên chuẩn của schema. Ghép theo Player+Squad.
    """
    files = sorted(PATHS.raw.glob("supplement_*.csv"))
    if not files:
        return df
    base = add_keys(df)
    for f in files:
        sup = pd.read_csv(f, na_values=[NA], keep_default_na=False)
        if "Player" not in sup.columns:
            log(f"   ! {f.name}: thiếu cột Player, bỏ qua")
            continue
        if "Squad" not in sup.columns:
            sup["Squad"] = np.nan
        sup = add_keys(sup)
        sup = sup.drop_duplicates(subset=["_pk", "_sk"])
        filled = 0
        for c in [c for c in sup.columns if c in base.columns and c not in KEY_COLS + ["_pk", "_sk"]]:
            m = base[["_pk", "_sk"]].merge(sup[["_pk", "_sk", c]], on=["_pk", "_sk"], how="left")[c]
            m.index = base.index
            mask = base[c].isna() & m.notna()
            if base[c].dtype == object or sup[c].dtype == object:
                m = m if base[c].dtype == object else to_number(m)
            base.loc[mask, c] = m[mask]
            filled += int(mask.sum())
        log(f"   + supplement {f.name}: điền {filled} ô")
        log_source("supplement", f.name, "(nguồn bổ sung)", str(f), notes=f"điền {filled} ô")
    return base.drop(columns=["_pk", "_sk"])
