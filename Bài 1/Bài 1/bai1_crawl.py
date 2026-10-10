import time
import io
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

CATEGORIES = [
    ("stats", "stats_standard"),
    ("keepers", "stats_keeper"),
    ("shooting", "stats_shooting"),
    ("passing", "stats_passing"),
    ("passing_types", "stats_passing_types"),
    ("gca", "stats_gca"),
    ("defense", "stats_defense"),
    ("possession", "stats_possession"),
    ("playingtime", "stats_playing_time"),
    ("misc", "stats_misc")
]

def parse_html_table(html_content, table_id):
    """Bóc tách bảng dữ liệu HTML ngay cả khi nằm trong comment."""
    html_cleaned = html_content.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html_cleaned, "html.parser")
    
    # 1. Thử tìm theo table_id chính xác
    table = soup.find("table", {"id": table_id})
    
    # 2. Nếu không thấy, tìm bảng chứa class 'stats_table' mà có cột 'Player'
    if table is None:
        all_tables = soup.find_all("table", class_="stats_table")
        for t in all_tables:
            if "Player" in t.get_text():
                table = t
                break
                
    if table is None:
        return None

    try:
        df = pd.read_html(io.StringIO(str(table)))[0]
    except Exception:
        return None

    # Xử lý MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            f"{c[0].strip()}_{c[1].strip()}" if "Unnamed" not in str(c[0]) and str(c[0]) != "" else str(c[1]).strip()
            for c in df.columns
        ]
    else:
        df.columns = [str(c).strip() for c in df.columns]

    # Loại bỏ dòng lặp header
    if "Player" in df.columns:
        df = df[df["Player"] != "Player"].copy()

    return df

def main():
    print("[*] Đang khởi chạy trình duyệt Chrome tự động...")
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    driver = uc.Chrome(options=options)

    merged_df = None

    try:
        for cat_slug, table_id in CATEGORIES:
            url = f"https://fbref.com/en/comps/9/2024-2025/{cat_slug}/2024-2025-Premier-League-Stats"
            print(f"[*] Đang tải dữ liệu từ: {cat_slug}...")
            
            driver.get(url)
            # Chờ trang tải đầy đủ DOM
            time.sleep(6)
            
            df = parse_html_table(driver.page_source, table_id)
            if df is None:
                # Đợi thêm 3s nếu mạng chậm rồi thử lại lần 2
                time.sleep(3)
                df = parse_html_table(driver.page_source, table_id)

            if df is not None and "Player" in df.columns:
                print(f"  -> Lấy thành công {len(df)} dòng dữ liệu từ {cat_slug}.")
                if merged_df is None:
                    merged_df = df
                else:
                    # Các cột nhận diện cầu thủ dùng để merge
                    common_cols = [c for c in ["Player", "Nation", "Pos", "Squad", "Age"] if c in df.columns and c in merged_df.columns]
                    # Loại bỏ các cột trùng khác trước khi gộp để tránh cột _x, _y
                    new_cols = [c for c in df.columns if c not in merged_df.columns]
                    merged_df = pd.merge(merged_df, df[common_cols + new_cols], on=common_cols, how="outer")
            else:
                print(f"  [!] Cảnh báo: Không thể bóc tách bảng từ {cat_slug}")
            
            time.sleep(4)

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    if merged_df is None:
        print("Không có dữ liệu thu thập được.")
        return

    # 1. Lọc điều kiện: Đã thi đấu hơn 90 phút
    # Thống kê phút thường là 'Min' hoặc có tiền tố 'Playing Time_Min'
    min_col = None
    for candidate in ["Min", "Playing Time_Min", "Playing Time_Mn"]:
        if candidate in merged_df.columns:
            min_col = candidate
            break

    if min_col:
        merged_df[min_col] = merged_df[min_col].astype(str).str.replace(",", "")
        merged_df[min_col] = pd.to_numeric(merged_df[min_col], errors="coerce").fillna(0)
        merged_df = merged_df[merged_df[min_col] > 90].copy()
        print(f"[*] Số cầu thủ sau khi lọc (> 90 phút): {len(merged_df)}")

    # 2. Xử lý giá trị trống/không áp dụng thành 'N/a'
    merged_df = merged_df.fillna("N/a")
    merged_df = merged_df.replace({"": "N/a", None: "N/a"})

    # 3. Sắp xếp theo First Name A-Z, nếu trùng xếp theo Tuổi giảm dần
    def get_first_name(full_name):
        parts = str(full_name).strip().split()
        return parts[0] if parts else ""

    def parse_age(age_val):
        try:
            return float(str(age_val).split("-")[0])
        except Exception:
            return -1.0

    merged_df["_first_name"] = merged_df["Player"].apply(get_first_name)
    merged_df["_age_num"] = merged_df["Age"].apply(parse_age)

    merged_df = merged_df.sort_values(
        by=["_first_name", "_age_num"],
        ascending=[True, False]
    )

    merged_df = merged_df.drop(columns=["_first_name", "_age_num"])

    # 4. Xuất file results.csv
    # Xóa cột Rk nếu có
    if "Rk" in merged_df.columns:
        merged_df = merged_df.drop(columns=["Rk"])
    output_filename = "results.csv"
    # Đặt driver về None để bộ dọn rác không gọi quit() lần 2
    del driver
    merged_df.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"[+] Hoàn thành! Đã lưu kết quả vào '{output_filename}'.")

if __name__ == "__main__":
    main()