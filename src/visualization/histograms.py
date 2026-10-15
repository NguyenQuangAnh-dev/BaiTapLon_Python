"""NGƯỜI 8 — Histogram toàn giải và theo từng đội cho mỗi thống kê."""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

from src.common.paths import PATHS
from src.visualization.plot_utils import get_plt, safe_name


def plot_histograms(df: pd.DataFrame, stats: list[str], bins: int = 15,
                    limit: Optional[int] = None) -> int:
    """Với mỗi thống kê: 1 histogram toàn giải + 1 lưới histogram cho từng đội.

    plots/hist_all/<stat>.png   và   plots/hist_teams/<stat>.png
    """
    plt = get_plt()
    out_all, out_team = PATHS.plots / "hist_all", PATHS.plots / "hist_teams"
    out_all.mkdir(parents=True, exist_ok=True)
    out_team.mkdir(parents=True, exist_ok=True)
    teams = sorted(df["Squad"].dropna().unique())
    ncol = 5
    nrow = max(1, math.ceil(len(teams) / ncol))
    done = 0
    for s in stats[: limit if limit else None]:
        vals = pd.to_numeric(df[s], errors="coerce").dropna()
        if vals.empty:
            continue
        lo, hi = float(vals.min()), float(vals.max())
        hi = hi if hi > lo else lo + 1.0
        edges = np.linspace(lo, hi, bins + 1)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(vals, bins=edges, color="#2a6fbb", edgecolor="white")
        ax.set(title=f"{s} — toàn bộ cầu thủ (n={len(vals)})", xlabel=s, ylabel="Số cầu thủ")
        fig.tight_layout()
        fig.savefig(out_all / f"{safe_name(s)}.png", dpi=110)
        plt.close(fig)

        fig, axes = plt.subplots(nrow, ncol, figsize=(3.1 * ncol, 2.3 * nrow), sharex=True)
        for ax, team in zip(np.ravel(axes), teams):
            tv = pd.to_numeric(df.loc[df["Squad"] == team, s], errors="coerce").dropna()
            ax.hist(tv, bins=edges, color="#d9822b", edgecolor="white")
            ax.set_title(team, fontsize=8)
            ax.tick_params(labelsize=7)
        for ax in np.ravel(axes)[len(teams):]:
            ax.axis("off")
        fig.suptitle(f"{s} — theo từng đội", fontsize=11)
        fig.tight_layout()
        fig.savefig(out_team / f"{safe_name(s)}.png", dpi=90)
        plt.close(fig)
        done += 1
    return done
