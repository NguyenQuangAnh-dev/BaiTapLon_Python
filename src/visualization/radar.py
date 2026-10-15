"""NGƯỜI 10 — Radar chart so sánh hai cầu thủ.

python radarChartPlot.py --p1 <tên 1> --p2 <tên 2> --Attribute <a1,a2,...,an>
"""
from __future__ import annotations

import argparse
import re
import sys
from difflib import get_close_matches
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.common.io_utils import load_results, stat_columns
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.preprocessing.cleaning import player_key
from src.visualization.plot_utils import get_plt, safe_name


def find_player(df: pd.DataFrame, query: str) -> pd.Series:
    """Tìm cầu thủ theo tên (không phân biệt dấu/hoa-thường; chấp nhận gõ một phần; gần đúng)."""
    keys = df["Player"].map(player_key)
    k = player_key(query)
    hit = df[keys == k]
    if hit.empty:
        hit = df[keys.str.contains(re.escape(k), na=False)]
    if hit.empty:
        near = get_close_matches(k, keys.unique().tolist(), n=3, cutoff=0.75)
        hit = df[keys.isin(near)]
        if near:
            log(f"  (không có '{query}', dùng tên gần đúng nhất)")
    if hit.empty:
        raise ValueError(f"Không tìm thấy cầu thủ '{query}' trong results.csv")
    if len(hit) > 1:
        names = ", ".join(f"{r.Player} ({r.Squad})" for r in hit.head(5).itertuples())
        log(f"  ! '{query}' khớp nhiều người: {names} -> chọn người có nhiều phút nhất")
        hit = hit.sort_values("Min", ascending=False)
    return hit.iloc[0]


def resolve_attribute(name: str, columns: list[str]) -> str:
    """Chấp nhận tên đầy đủ (Sh_Gls) hoặc tên ngắn nếu không mơ hồ (Gls)."""
    name = name.strip()
    low = {c.lower(): c for c in columns}
    if name.lower() in low:
        return low[name.lower()]
    suffix = [c for c in columns if c.lower().endswith("_" + name.lower())]
    if len(suffix) == 1:
        return suffix[0]
    hints = suffix or get_close_matches(name, columns, n=5, cutoff=0.5)
    raise ValueError(f"Thuộc tính '{name}' không hợp lệ/mơ hồ. Gợi ý: {hints}")


def radar_chart(p1: str, p2: str, attributes: list[str], df: Optional[pd.DataFrame] = None,
                out: Optional[Path] = None, show: bool = False) -> Path:
    """Radar so sánh 2 cầu thủ. Mỗi thuộc tính được chuẩn hóa min–max trên TOÀN BỘ cầu thủ
    (0 = thấp nhất giải, 1 = cao nhất giải) để các trục khác đơn vị so sánh được."""
    df = load_results() if df is None else df
    attrs = [resolve_attribute(a, stat_columns(df)) for a in attributes]
    if len(attrs) < 3:
        raise ValueError("Radar cần ít nhất 3 thuộc tính (--Attribute a,b,c,...)")
    a, b = find_player(df, p1), find_player(df, p2)
    vals = df[attrs].apply(pd.to_numeric, errors="coerce")
    lo, hi = vals.min(), vals.max()
    span = (hi - lo).replace(0, np.nan)
    norm = lambda row: ((pd.to_numeric(row[attrs], errors="coerce") - lo) / span).fillna(0).clip(0, 1)
    na_, nb_ = norm(a), norm(b)
    for who, row in ((a, "p1"), (b, "p2")):
        miss = [c for c in attrs if pd.isna(pd.to_numeric(who[c], errors="coerce"))]
        if miss:
            log(f"  ! {who['Player']} không có dữ liệu (N/a) cho {miss} -> vẽ ở mức 0")

    plt = get_plt(show)
    angles = np.linspace(0, 2 * np.pi, len(attrs), endpoint=False).tolist()
    ang = angles + angles[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for row, nv, color in ((a, na_, "#2a6fbb"), (b, nb_, "#d9822b")):
        data = nv.tolist() + nv.tolist()[:1]
        ax.plot(ang, data, color=color, lw=2, label=f"{row['Player']} ({row['Squad']})")
        ax.fill(ang, data, color=color, alpha=0.2)
    labels = []
    for c in attrs:
        va, vb = pd.to_numeric(a[c], errors="coerce"), pd.to_numeric(b[c], errors="coerce")
        f = lambda v: "N/a" if pd.isna(v) else f"{v:g}"
        labels.append(f"{c}\n{f(va)} | {f(vb)}")
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=7, color="gray")
    ax.set_title(f"{a['Player']}  vs  {b['Player']}\n(giá trị chuẩn hóa min–max toàn giải; nhãn = thực tế p1 | p2)",
                 fontsize=11, pad=24)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    fig.tight_layout()
    if out is None:
        d = PATHS.plots / "radar"
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"radar_{safe_name(a['Player'])}_vs_{safe_name(b['Player'])}.png"
    out = Path(out)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out


def radar_cli(argv: Optional[list[str]] = None) -> int:
    """python radarChartPlot.py --p1 <tên 1> --p2 <tên 2> --Attribute <a1,a2,...,an>"""
    ap = argparse.ArgumentParser(prog="radarChartPlot.py",
                                 description="Vẽ biểu đồ radar so sánh hai cầu thủ")
    ap.add_argument("--p1", nargs="+", required=True, help="tên cầu thủ thứ nhất")
    ap.add_argument("--p2", nargs="+", required=True, help="tên cầu thủ thứ hai")
    ap.add_argument("--Attribute", nargs="+", required=True,
                    help="danh sách thống kê, cách nhau bằng dấu phẩy. Ví dụ: Sh_Gls,Sh_SoT,SCA_SCA90")
    ap.add_argument("--data", help="đường dẫn results.csv (mặc định data/processed/results.csv)")
    ap.add_argument("--out", help="file PNG xuất ra")
    ap.add_argument("--show", action="store_true", help="mở cửa sổ hiển thị")
    args = ap.parse_args(argv)
    attrs = [a for a in re.split(r"\s*,\s*", " ".join(args.Attribute).strip()) if a]
    try:
        df = load_results(Path(args.data)) if args.data else None
        path = radar_chart(" ".join(args.p1), " ".join(args.p2), attrs, df=df,
                           out=Path(args.out) if args.out else None, show=args.show)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2
    print(f"Đã lưu biểu đồ radar: {path}")
    return 0
