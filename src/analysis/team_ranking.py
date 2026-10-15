"""NGƯỜI 8 — Đội có điểm cao nhất cho từng thống kê và đánh giá phong độ đội."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import settings


LOWER_IS_BETTER = {
    "GK_GA", "GK_GA90", "GK_SoTA", "GK_L", "GKPK_PKA", "Perf_CrdY", "Perf_CrdR", "Chall_Lost",
    "Blk_Err", "Carry_Mis", "Carry_Dis", "TakeOn_Tkld", "TakeOn_Tkld%", "Misc_Fls", "Misc_OG",
    "Aerial_Lost", "Team_onGA", "TeamxG_onxGA",
}


NON_PERFORMANCE = {"Age", "MP", "Starts", "Min", "Start_Starts", "Start_Mn/Start", "Start_Compl",
                   "Sub_Subs", "Sub_Mn/Sub", "Sub_unSub"}


def best_team_per_stat(df: pd.DataFrame, stats: list[str]) -> pd.DataFrame:
    """Đội có điểm cao nhất cho mỗi thống kê (điểm đội = TRUNG BÌNH của các cầu thủ trong đội;
    với thống kê 'càng thấp càng tốt' thì chọn đội có trung bình thấp nhất)."""
    means = df.groupby("Squad")[stats].mean(numeric_only=True)
    rows = []
    for s in stats:
        col = means[s].dropna()
        if col.empty:
            continue
        low = s in LOWER_IS_BETTER
        team = col.idxmin() if low else col.idxmax()
        rows.append({"Statistic": s, "Best team": team, "Team mean": round(col[team], 3),
                     "Rule": "thấp nhất" if low else "cao nhất"})
    return pd.DataFrame(rows)


def assess_team_form(df: pd.DataFrame, stats: list[str], best: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Xếp hạng phong độ: điểm = trung bình z-score của (trung bình đội) trên các thống kê
    hiệu suất (đảo dấu với thống kê 'càng thấp càng tốt'), kèm số thống kê đứng nhất."""
    perf = [s for s in stats if s not in NON_PERFORMANCE]
    means = df.groupby("Squad")[perf].mean(numeric_only=True)
    means = means.loc[:, means.notna().sum() >= max(5, int(0.75 * len(means)))]   # đủ phủ cho các đội
    z = (means - means.mean()) / means.std(ddof=0).replace(0, np.nan)
    for s in z.columns:
        if s in LOWER_IS_BETTER:
            z[s] = -z[s]
    score = z.mean(axis=1, skipna=True)
    firsts = best[best["Statistic"].isin(perf)]["Best team"].value_counts()
    table = pd.DataFrame({"Team": score.index, "ZScore": score.values.round(3)})
    table["#Best"] = table["Team"].map(firsts).fillna(0).astype(int)
    table = table.sort_values("ZScore", ascending=False).reset_index(drop=True)
    table.insert(0, "Rank", range(1, len(table) + 1))
    if table.empty:
        return table, "Không đủ dữ liệu để đánh giá phong độ đội."
    top = table.iloc[0]
    text = (
        f"NHẬN ĐỊNH PHONG ĐỘ ĐỘI (mùa {settings.SEASON})\n"
        f"- Phương pháp: với {len(z.columns)} thống kê hiệu suất, tính trung bình từng đội, chuẩn hóa z-score "
        f"giữa các đội (đảo dấu thống kê 'càng thấp càng tốt'), rồi lấy trung bình z-score.\n"
        f"- Đội có phong độ tốt nhất theo phân tích: {top['Team']} (z = {top['ZScore']:.3f}, đứng nhất ở "
        f"{int(top['#Best'])} thống kê).\n"
        f"- Top 5: " + "; ".join(f"{r.Team} ({r.ZScore:.2f})" for r in table.head(5).itertuples()) + "\n"
        "- Hạn chế: điểm đội là trung bình theo cầu thủ (không trọng số theo số phút); thống kê thủ môn chỉ dựa trên "
        "vài thủ môn; kết quả thực tế của đội (điểm, hiệu số) nên được đối chiếu thêm (ví dụ Team_PPM).\n")
    return table, text
