import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    csv_file = "results.csv"
    if not os.path.exists(csv_file):
        print(f"Không tìm thấy file {csv_file}. Vui lòng chạy bài 1 trước!")
        return

    print("[*] Đang đọc dữ liệu từ results.csv...")
    df = pd.read_csv(csv_file)

    # 1. Xác định các cột định danh (chuỗi chữ) và các cột thống kê định lượng (số)
    id_cols = ["Player", "Nation", "Pos", "Squad", "Matches"]
    # Bỏ qua các cột định danh để lấy danh sách thuộc tính thống kê
    stat_cols = [c for c in df.columns if c not in id_cols]

    # Chuyển đổi các giá trị số (thay "N/a" thành NaN để tính toán chính xác)
    for col in stat_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # Chỉ giữ lại các cột có dữ liệu số
    stat_cols = [c for c in stat_cols if df[c].notna().sum() > 0]
    print(f"[*] Tổng số thuộc tính thống kê cần phân tích: {len(stat_cols)}")

    # -------------------------------------------------------------
    # NHIỆM VỤ 1: Xác định 3 cầu thủ cao nhất và thấp nhất cho mỗi chỉ số
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print("TOP 3 VÀ BOTTOM 3 CẦU THỦ CHO MỖI THỐNG KÊ")
    print("="*50)
    
    top_bottom_records = []
    for col in stat_cols:
        sub_df = df[["Player", "Squad", col]].dropna()
        if len(sub_df) >= 3:
            top3 = sub_df.sort_values(by=col, ascending=False).head(3)
            bottom3 = sub_df.sort_values(by=col, ascending=True).head(3)
            
            top_str = ", ".join([f"{r['Player']} ({r[col]})" for _, r in top3.iterrows()])
            bottom_str = ", ".join([f"{r['Player']} ({r[col]})" for _, r in bottom3.iterrows()])
            
            top_bottom_records.append({
                "Thống kê": col,
                "Top 3 cao nhất": top_str,
                "Top 3 thấp nhất": bottom_str
            })

    top_bottom_df = pd.DataFrame(top_bottom_records)
    top_bottom_df.to_csv("top_bottom_players.csv", index=False, encoding="utf-8-sig")
    print("[+] Đã lưu danh sách Top 3 / Bottom 3 vào file 'top_bottom_players.csv'")

    # -------------------------------------------------------------
    # NHIỆM VỤ 2: Tính Median, Mean, Std và xuất 'results2.csv'
    # Định dạng yêu cầu:
    #             Median của Thuộc tính 1 | Mean của Thuộc tính 1 | Std của Thuộc tính 1 | ...
    # 0 all
    # 1 Team 1
    # ...
    # -------------------------------------------------------------
    print("\n[*] Đang tính toán Median, Mean, Std cho từng thuộc tính...")

    teams = sorted(df["Squad"].dropna().unique())
    groups = ["all"] + list(teams)
    
    result_rows = []
    for group in groups:
        row_data = {}
        if group == "all":
            group_df = df
        else:
            group_df = df[df["Squad"] == group]

        for col in stat_cols:
            valid_vals = group_df[col].dropna()
            
            med = valid_vals.median() if len(valid_vals) > 0 else np.nan
            mean_val = valid_vals.mean() if len(valid_vals) > 0 else np.nan
            std_val = valid_vals.std() if len(valid_vals) > 1 else 0.0

            row_data[f"Median của {col}"] = f"{med:.2f}" if pd.notna(med) else "N/a"
            row_data[f"Mean của {col}"] = f"{mean_val:.2f}" if pd.notna(mean_val) else "N/a"
            row_data[f"Std của {col}"] = f"{std_val:.2f}" if pd.notna(std_val) else "N/a"

        result_rows.append(row_data)

    results2_df = pd.DataFrame(result_rows, index=groups)
    results2_df.index.name = "Team"
    
    # Xuất ra kết quả results2.csv
    results2_df.to_csv("results2.csv", encoding="utf-8-sig")
    print("[+] Đã xuất thành công file 'results2.csv'!")

    # -------------------------------------------------------------
    # NHIỆM VỤ 3: Xác định đội có điểm số trung bình cao nhất mỗi thuộc tính
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print("ĐỘI BÓNG ĐỨNG ĐẦU MỖI THỐNG KÊ (THEO GIÁ TRỊ TRUNG BÌNH)")
    print("="*50)
    
    team_best_stats = {}
    team_scores = {team: 0 for team in teams}

    for col in stat_cols:
        team_means = df.groupby("Squad")[col].mean().dropna()
        if not team_means.empty:
            best_team = team_means.idxmax()
            best_val = team_means.max()
            team_best_stats[col] = (best_team, best_val)
            team_scores[best_team] += 1

    # Đội dẫn đầu nhiều chỉ số nhất
    top_performing_team = max(team_scores, key=team_scores.get)
    print(f"[+] Đội dẫn đầu nhiều chỉ số tích cực nhất giải đấu: {top_performing_team} ({team_scores[top_performing_team]} chỉ số đứng đầu).")

    # -------------------------------------------------------------
    # NHIỆM VỤ 4: Vẽ biểu đồ Histogram phân bố
    # -------------------------------------------------------------
    os.makedirs("histograms", exist_ok=True)
    print("\n[*] Đang vẽ biểu đồ Histogram cho một số chỉ số quan trọng (lưu tại thư mục 'histograms/')...")

    # Chọn lọc các thuộc tính quan trọng để minh họa vẽ biểu đồ
    key_features = [c for c in stat_cols if any(k in c.lower() for k in ["gls", "ast", "xg", "prgc", "touches", "tkl"])]
    sample_features = key_features[:8] if key_features else stat_cols[:8]

    for col in sample_features:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            plt.figure(figsize=(8, 5))
            plt.hist(valid_data, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            plt.title(f"Histogram: Phân bố của {col} (Toàn bộ giải đấu)")
            plt.xlabel("Giá trị")
            plt.ylabel("Số lượng cầu thủ")
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            clean_col_name = col.replace("/", "_").replace(" ", "_")
            plt.savefig(f"histograms/hist_{clean_col_name}.png", bbox_inches='tight')
            plt.close()

    print("[+] Hoàn thành vẽ biểu đồ Histogram!")

if __name__ == "__main__":
    main()