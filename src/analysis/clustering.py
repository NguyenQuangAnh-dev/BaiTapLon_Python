"""NGƯỜI 9 — Phần III: chuẩn bị feature, chọn k, mô tả cụm (K-means + PCA).

Quy tắc: không dùng tên cầu thủ làm feature; luôn chuẩn hóa trước K-means; seed cố định;
lưu danh sách feature để báo cáo tái lập được.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import RANDOM_STATE
from src.analysis.statistics import numeric_stats


NON_FEATURE = {"Age", "MP", "Starts", "Min", "Start_Starts", "Start_Mn/Start", "Start_Compl",
               "Sub_Subs", "Sub_Mn/Sub", "Sub_unSub"}


NON_FEATURE_PREFIX = ("Team_", "TeamxG_")


def _is_count_feature(col: str) -> bool:
    """Cột dạng TỔNG (đếm) -> sẽ chia cho số trận 90 phút để so sánh công bằng."""
    prefix, _, stat = col.partition("_")
    if col.startswith("P90_"):
        return False
    return not ("%" in stat or "90" in stat or "/" in stat or stat.startswith("Mn")
                or col in ("Sh_Dist",))


def prepare_features(df: pd.DataFrame, per90: bool = True, max_missing: float = 0.5):
    """Tạo ma trận đặc trưng: bỏ cột quá thiếu (vd. thủ môn), quy về /90 phút, điền median."""
    cols_ = [c for c in numeric_stats(df)
             if c not in NON_FEATURE and not c.startswith(NON_FEATURE_PREFIX)]
    X = df[cols_].apply(pd.to_numeric, errors="coerce")
    info = {"ban_dau": len(cols_)}
    miss = X.isna().mean()
    dropped_missing = list(miss[miss > max_missing].index)       # vd. GK_*: chỉ thủ môn mới có
    X = X.drop(columns=dropped_missing)
    if per90:
        n90 = (pd.to_numeric(df["Min"], errors="coerce") / 90).clip(lower=1 / 90)
        for c in X.columns:
            if _is_count_feature(c):
                X[c] = X[c] / n90
    dup = X.T.duplicated()                                       # cột trùng hệt nhau
    dropped_dup = list(X.columns[dup.values])
    X = X.loc[:, ~dup.values]
    X = X.fillna(X.median(numeric_only=True))                    # quy tắc thiếu: điền trung vị cột
    const = [c for c in X.columns if X[c].std(ddof=0) == 0 or X[c].isna().all()]
    X = X.drop(columns=const)
    info.update(bo_vi_thieu=dropped_missing, bo_vi_trung=dropped_dup, bo_hang_so=const,
                con_lai=list(X.columns))
    return X, info


def evaluate_k(Xs: np.ndarray, kmin: int = 2, kmax: int = 10) -> pd.DataFrame:
    from sklearn.cluster import KMeans
    from sklearn.metrics import davies_bouldin_score, silhouette_score
    rows = []
    for k in range(kmin, min(kmax, len(Xs) - 1) + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(Xs)
        rows.append({"k": k, "inertia": km.inertia_,
                     "silhouette": silhouette_score(Xs, km.labels_),
                     "davies_bouldin": davies_bouldin_score(Xs, km.labels_)})
    return pd.DataFrame(rows)


def choose_k(scores: pd.DataFrame, k_floor: int = 3) -> int:
    """Chọn k có silhouette cao nhất trong k >= 3. (k=2 thường chỉ tách thủ môn/cầu thủ ngoài
    sân hoặc 'ít phút/nhiều phút' nên ít ý nghĩa mô tả phong cách; vẫn in kèm để so sánh.)"""
    cand = scores[scores["k"] >= k_floor]
    cand = cand if not cand.empty else scores
    return int(cand.loc[cand["silhouette"].idxmax(), "k"])


def describe_clusters(df, X, km, scores, k_best, k_used, evr, info, Xs) -> str:
    """Giải thích số nhóm + nhận xét từng cụm (thành phần vị trí, đặc trưng nổi bật, ví dụ)."""
    row_best = scores[scores["k"] == k_best].iloc[0]
    lines = [
        "GIẢI THÍCH SỐ NHÓM VÀ NHẬN XÉT KẾT QUẢ K-MEANS",
        f"- Dữ liệu: {len(df)} cầu thủ; {X.shape[1]} đặc trưng đã chuẩn hóa (StandardScaler); các thống kê dạng "
        "tổng được quy về /90 phút để không phụ thuộc số phút thi đấu; ô thiếu điền bằng trung vị cột; "
        "cột thiếu >50% (thủ môn) bị loại; seed cố định = " + str(RANDOM_STATE) + ".",
        f"- Tiêu chí chọn k: silhouette cao nhất với k>=3 (k={k_best}: silhouette={row_best['silhouette']:.3f}, "
        f"Davies-Bouldin={row_best['davies_bouldin']:.3f}), đối chiếu với điểm gấp khúc của Elbow. "
        f"Số cụm đang dùng: k={k_used}.",
        f"- PCA 2 chiều giữ {evr.sum():.1%} phương sai (PC1 {evr[0]:.1%}, PC2 {evr[1]:.1%}); phần còn lại bị "
        "mất khi vẽ 2D nên các cụm có thể chồng lấn trên hình dù tách tốt trong không gian đầy đủ.",
        "",
    ]
    pos_main = df["Pos"].astype(str).str.split(",").str[0].str.strip()
    Z = pd.DataFrame(km.cluster_centers_, columns=X.columns)
    for c in range(k_used):
        idx = np.where(km.labels_ == c)[0]
        comp = pos_main.iloc[idx].value_counts(normalize=True).head(3)
        comp_txt = ", ".join(f"{p} {v:.0%}" for p, v in comp.items())
        top = Z.loc[c].sort_values(ascending=False).head(5)
        low = Z.loc[c].sort_values().head(3)
        d = np.linalg.norm(Xs[idx] - km.cluster_centers_[c], axis=1)
        examples = ", ".join(df["Player"].iloc[idx[np.argsort(d)[:3]]])
        lines += [f"Cụm {c}: {len(idx)} cầu thủ | vị trí chính: {comp_txt}",
                  "   nổi bật cao: " + ", ".join(f"{n} ({v:+.2f})" for n, v in top.items()),
                  "   nổi bật thấp: " + ", ".join(f"{n} ({v:+.2f})" for n, v in low.items()),
                  f"   cầu thủ tiêu biểu (gần tâm cụm): {examples}"]
    lines += ["", "Nhận xét: nếu thành phần vị trí của mỗi cụm khá thuần (ví dụ cụm toàn tiền đạo/ tiền vệ/ hậu vệ), "
              "K-means đã phát hiện được vai trò thi đấu từ thống kê mà không cần biết vị trí. Cụm lẫn nhiều vị trí "
              "thường là cầu thủ đa năng hoặc cầu thủ có ít phút (thống kê /90 phút nhiễu)."]
    return "\n".join(lines)
