"""NGƯỜI 9 — K-means + PCA."""
import numpy as np
import pandas as pd

from src.pipeline.run_clustering import run_clustering


def test_three_clear_clusters(isolated_paths):
    rng = np.random.default_rng(1)
    n = 40
    data = {"Player": [f"P{i}" for i in range(3 * n)], "Squad": ["T"] * (3 * n),
            "Pos": ["FW"] * n + ["MF"] * n + ["DF"] * n, "Min": [900] * (3 * n)}
    for j in range(6):
        centers = rng.normal(0, 6, 3)
        data[f"P90_f{j}"] = np.concatenate([rng.normal(centers[i], 0.5, n) for i in range(3)])
    res = run_clustering(pd.DataFrame(data), kmin=2, kmax=6)
    assert res["Cluster"].nunique() == 3
    assert (isolated_paths.plots / "pca_clusters.png").exists()
    assert (isolated_paths.final / "cluster_report.txt").exists()
