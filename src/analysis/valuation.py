"""NGƯỜI 10 — Phần IV: ước lượng giá trị cầu thủ từ thống kê (log-target, 3 mô hình, 5-fold CV)."""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from config import settings
from config.settings import RANDOM_STATE
from src.analysis.clustering import prepare_features
from src.common.io_utils import load_extended, read_table, save_with_na
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.preprocessing.filters import filter_min_minutes


def estimate_player_value(results: Optional[pd.DataFrame] = None, tf: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Mô hình ước lượng giá trị cầu thủ.
       Target : log(1 + giá trị, triệu €)      (giá lệch phải -> lấy log)
       Feature: thống kê /90 phút + Min + Age + vị trí (one-hot)
       Mô hình: Ridge (cơ sở), RandomForest, GradientBoosting -> chọn theo R² qua 5-fold CV."""
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    PATHS.make()
    results = (filter_min_minutes(load_extended()) if results is None else results).reset_index(drop=True)
    if tf is None:
        tf = read_table("transfers")
    results = results.copy()
    fees = (tf.assign(transfer_fee=pd.to_numeric(tf["transfer_fee"], errors="coerce"))
              .dropna(subset=["transfer_fee"]).sort_values("transfer_date", na_position="first")
              .groupby("player_id")["transfer_fee"].last())
    results["Value_M"] = results["player_id"].map(fees)      # target = phí chuyển nhượng (triệu EUR) theo player_id
    X, info = prepare_features(results, per90=True)
    X = X.copy()
    X["Min"] = pd.to_numeric(results["Min"], errors="coerce")
    X["Age"] = pd.to_numeric(results["Age"], errors="coerce")
    X["Age_sq"] = (X["Age"] - 26) ** 2
    main_pos = results["Pos"].astype(str).str.split(",").str[0].str.strip()
    X = pd.concat([X, pd.get_dummies(main_pos, prefix="Pos").astype(float)], axis=1)
    X = X.fillna(X.median(numeric_only=True))
    known = results["Value_M"].notna().values
    log(f"== PHẦN IV: Ước lượng giá trị — {int(known.sum())}/{len(results)} cầu thủ có giá để huấn luyện ==")
    if known.sum() < 30:
        log("  ! Quá ít cầu thủ khớp được giá (<30): kiểm tra lại cách ghép tên/mùa giải trong transfers.csv")
        return pd.DataFrame()
    y = np.log1p(results.loc[known, "Value_M"].values)
    models = {
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "RandomForest": RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }
    kf = KFold(5, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    for name, model in models.items():
        pred = cross_val_predict(model, X[known], y, cv=kf)
        rows.append({"Model": name, "R2_log": r2_score(y, pred),
                     "MAE_M_EUR": mean_absolute_error(np.expm1(y), np.expm1(pred))})
    cv = pd.DataFrame(rows).sort_values("R2_log", ascending=False).reset_index(drop=True)
    best = cv.loc[0, "Model"]
    log("  Kết quả 5-fold CV:\n" + cv.round(3).to_string(index=False) + f"\n  -> chọn: {best}")
    model = models[best].fit(X[known], y)
    results["Predicted_M"] = np.expm1(model.predict(X)).round(2)
    out = results[["Player", "Squad", "Value_M", "Predicted_M"]].rename(columns={"Value_M": "Actual_M"})
    out["Error_M"] = (out["Predicted_M"] - out["Actual_M"]).round(2)
    save_with_na(out, PATHS.final / "value_estimates.csv")
    cv.round(4).to_csv(PATHS.final / "valuation_cv.csv", index=False)

    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1).fit(X[known], y)
    imp = pd.Series(rf.feature_importances_, X.columns).sort_values(ascending=False).head(15)
    method = (
        f"# Phương pháp ước lượng giá trị cầu thủ\n\n"
        f"* **Dữ liệu**: player_stats_extended (mùa {settings.SEASON}) + phí từ bảng transfers (mùa {settings.TRANSFER_SEASON}); ghép theo player_id.\n"
        f"* **Target**: log(1 + giá trị, triệu €). **Feature**: {X.shape[1]} đặc trưng (thống kê /90 phút, Min, Age, Age², vị trí one-hot).\n"
        f"* **Mô hình**: Ridge, RandomForest, GradientBoosting; đánh giá 5-fold CV; chọn **{best}**.\n\n"
        f"{cv.round(3).to_markdown(index=False) if hasattr(cv, 'to_markdown') and _has_tabulate() else cv.round(3).to_string(index=False)}\n\n"
        f"**Top đặc trưng quan trọng (RandomForest):** " + ", ".join(f"{k} ({v:.3f})" for k, v in imp.items()) + "\n\n"
        "**Hạn chế**: giá phụ thuộc yếu tố ngoài sân (hợp đồng, thương hiệu, tiềm năng); thống kê một mùa có nhiễu; "
        "cầu thủ ít phút khó dự đoán; chênh lệch mùa giải giữa thống kê và giá làm giảm độ chính xác.\n")
    (PATHS.final / "valuation_method.md").write_text(method, encoding="utf-8")
    log(f"  -> {PATHS.final / 'value_estimates.csv'}, valuation_method.md")
    return out


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False
