"""NGƯỜI 9 — Hình Elbow/Silhouette và PCA 2D tô màu theo cụm."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.visualization.plot_utils import get_plt


def plot_elbow_silhouette(scores: pd.DataFrame, k_best: int, path: Path) -> None:
    plt = get_plt()
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(scores["k"], scores["inertia"], "o-")
    ax[0].set(title="Elbow (inertia)", xlabel="k", ylabel="Inertia")
    ax[1].plot(scores["k"], scores["silhouette"], "o-", color="#d9822b")
    ax[1].axvline(k_best, ls="--", color="gray")
    ax[1].set(title="Silhouette", xlabel="k", ylabel="Silhouette")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_pca_clusters(P: np.ndarray, labels: np.ndarray, centers_2d: np.ndarray, evr, k: int, path: Path) -> None:
    plt = get_plt()
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(P[:, 0], P[:, 1], c=labels, cmap="tab10", s=22, alpha=0.8)
    for i, (x, y) in enumerate(centers_2d):
        ax.text(x, y, str(i), fontsize=14, weight="bold", ha="center", va="center",
                bbox=dict(boxstyle="circle", fc="white", ec="black", alpha=0.85))
    ax.legend(*sc.legend_elements(), title="Cụm", loc="best")
    ax.set(xlabel=f"PC1 ({evr[0]:.1%} phương sai)", ylabel=f"PC2 ({evr[1]:.1%} phương sai)",
           title=f"K-means (k={k}) trên không gian PCA 2 chiều")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
