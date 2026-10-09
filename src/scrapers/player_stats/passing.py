import pandas as pd

# Đường dẫn nguồn dữ liệu
URL = "https://raw.githubusercontent.com/Gauransh-Singh/Data-Analytics-Football-season-2024-25/main/Data/players_data_light-2024_2025.csv"

def scrape_passing_data(url):
    print("Đang tải dữ liệu từ nguồn...")
    df = pd.read_csv(url)

    # 1. Lọc điều kiện thi đấu > 90 phút theo yêu cầu đề bài
    if "Min" in df.columns:
        df = df[pd.to_numeric(df["Min"], errors="coerce") > 90].copy()
    elif "Playing Time_Min" in df.columns:
        df = df[pd.to_numeric(df["Playing Time_Min"], errors="coerce") > 90].copy()

    # 2. Danh sách các cột Passing cần lấy theo yêu cầu Người 4:
    # - Định danh: Player, Squad
    # - Tổng: Cmp, Att, Cmp%, TotDist, PrgDist
    # - Ngắn: Cmp, Att, Cmp%
    # - Trung bình: Cmp, Att, Cmp%
    # - Dài: Cmp, Att, Cmp%
    # - Dự kiến/Tạo cơ hội: Ast, xAG, xA, A-xAG, KP, 1/3, PPA, CrsPA, PrgP
    
    # Kiểm tra các cột thực tế có trong dataset và chọn ra các cột tương ứng
    # (Tên cột trong file CSV này thường có tiền tố nhóm hoặc viết tắt chuẩn FBref)
    passing_cols = [col for col in df.columns if any(term in col for term in [
        "Player", "Squad", "Total_Cmp", "Total_Att", "TotDist", "PrgDist",
        "Short_Cmp", "Medium_Cmp", "Long_Cmp", "Ast", "xAG", "xA", "KP", "1/3", "PPA", "CrsPA", "PrgP"
    ])]

    # Nếu file dùng tên cột gốc trực tiếp:
    if len(passing_cols) <= 2:
        # Trường hợp lấy theo danh sách cột thông dụng
        desired_cols = [
            "Player", "Squad",
            "Cmp", "Att", "Cmp%", "TotDist", "PrgDist",
            "Ast", "xAG", "xA", "A-xAG", "KP", "1/3", "PPA", "CrsPA", "PrgP"
        ]
        passing_cols = [c for c in desired_cols if c in df.columns]

    df_passing = df[passing_cols].copy()

    # 3. Chuẩn hóa tên cầu thủ
    df_passing["Player"] = df_passing["Player"].astype(str).str.strip()

    # 4. Điền "N/a" cho các ô thiếu dữ liệu theo đúng chuẩn nhóm
    df_passing = df_passing.fillna("N/a")

    return df_passing

if __name__ == "__main__":
    df_result = scrape_passing_data(URL)
    
    # Xuất ra file passing.csv
    output_file = "passing.csv"
    df_result.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Đã tạo thành công {output_file} với {len(df_result)} dòng.")
    print("Các cột đã thu thập:", list(df_result.columns))