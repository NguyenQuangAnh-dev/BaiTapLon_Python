"""Chạy trọn PHẦN III (Người 9): chuẩn hóa -> chọn k -> K-means -> PCA -> hình + báo cáo."""
from __future__ import annotations

import pickle
from typing import Optional

import pandas as pd

from config.settings import RANDOM_STATE
from src.analysis.clustering import choose_k, describe_clusters, evaluate_k, prepare_features
from src.common.io_utils import load_results, save_with_na
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.visualization.cluster_plots import plot_elbow_silhouette, plot_pca_clusters


def run_clustering(df: Optional[pd.DataFrame] = None, k: Optional[int] = None,
                   kmin: int = 2, kmax: int = 10, per90: bool = True) -> pd.DataFrame:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    PATHS.make()
    df = load_results() if df is None else df.reset_index(drop=True)
    log(f"== PHẦN III: K-means + PCA ({len(df)} cầu thủ) ==")
    X, info = prepare_features(df, per90=per90)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.values)
    log(f"  Feature: {X.shape[1]} (ban đầu {info['ban_dau']}; bỏ {len(info['bo_vi_thieu'])} cột thiếu >50%, "
        f"{len(info['bo_vi_trung'])} cột trùng, {len(info['bo_hang_so'])} cột hằng số)")

    scores = evaluate_k(Xs, kmin, kmax)
    k_best = choose_k(scores)
    k_used = k or k_best
    log("  Đánh giá số nhóm:\n" + scores.round(3).to_string(index=False))
    log(f"  -> k đề xuất = {k_best}" + (f"; đang dùng k = {k_used} (người dùng chỉ định)" if k else ""))

    km = KMeans(n_clusters=k_used, n_init=10, random_state=RANDOM_STATE).fit(Xs)
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    P = pca.fit_transform(Xs)
    evr = pca.explained_variance_ratio_

    result = df[["Player", "Squad", "Pos"]].copy()
    result["Cluster"] = km.labels_
    result["PC1"], result["PC2"] = P[:, 0].round(4), P[:, 1].round(4)
    save_with_na(result, PATHS.final / "cluster_result.csv")
    scores.round(4).to_csv(PATHS.final / "kmeans_scores.csv", index=False)
    pd.Series(list(X.columns), name="feature").to_csv(PATHS.final / "cluster_features.csv", index=False)
    with open(PATHS.models / "kmeans_pca.pkl", "wb") as fh:
        pickle.dump({"scaler": scaler, "kmeans": km, "pca": pca, "features": list(X.columns),
                     "per90": per90, "random_state": RANDOM_STATE}, fh)

    plot_elbow_silhouette(scores, k_best, PATHS.plots / "kmeans_elbow_silhouette.png")
    plot_pca_clusters(P, km.labels_, pca.transform(km.cluster_centers_), evr, k_used, PATHS.plots / "pca_clusters.png")

    report = describe_clusters(df, X, km, scores, k_best, k_used, evr, info, Xs)
    (PATHS.final / "cluster_report.txt").write_text(report, encoding="utf-8")
    log("\n" + report)
    return result
