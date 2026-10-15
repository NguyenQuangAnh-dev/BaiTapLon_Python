"""Tiện ích vẽ biểu đồ dùng chung."""
from __future__ import annotations

import re


def get_plt(show: bool = False):
    import matplotlib
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def safe_name(col: str) -> str:
    """Tên file ổn định cho biểu đồ: 'Sh/90' -> 'Shper90'."""
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", col.replace("/", "per").replace("%", "pct").replace(":", "_"))
