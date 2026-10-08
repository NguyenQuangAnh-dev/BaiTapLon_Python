import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "data" / "processed" / "shooting.csv"

def test_file_exists():
    """Kiểm tra sự tồn tại của file kết quả shooting.csv trong data/processed/"""
    assert os.path.exists(CSV_PATH), f"Lỗi: Không tìm thấy file {CSV_PATH}. Hãy chạy scraper trước!"
    df = pd.read_csv(CSV_PATH)
    assert len(df) > 0, "Lỗi: File shooting.csv bị rỗng!"

def test_required_columns():
    """Kiểm tra có đầy đủ toàn bộ các cột chỉ số sút bóng theo đề bài"""
    df = pd.read_csv(CSV_PATH)
    required_cols = [
        "Player", "Nation", "Pos", "Squad", "Gls", "Sh", "SoT", "SoT%",
        "Sh/90", "SoT/90", "G/Sh", "G/SoT", "Dist", "FK", "PK", "PKatt",
        "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"
    ]
    for col in required_cols:
        assert col in df.columns, f"Lỗi: Thiếu cột '{col}' trong shooting.csv!"

def test_no_percent_symbols():
    """Kiểm tra không còn ký tự '%' trong các cột tỷ lệ (phải là số thực float)"""
    df = pd.read_csv(CSV_PATH)
    assert not df["SoT%"].astype(str).str.contains("%").any(), "Lỗi: Cột SoT% vẫn còn ký tự '%'!"

def test_logical_stat_constraints():
    """Kiểm tra tính hợp lý logic của dữ liệu sút bóng"""
    df = pd.read_csv(CSV_PATH)
    calc_df = df.replace("N/a", np.nan)
    
    # 1. Số cú sút trúng đích (SoT) không thể lớn hơn tổng số cú sút (Sh)
    sh = pd.to_numeric(calc_df["Sh"], errors="coerce").fillna(0)
    sot = pd.to_numeric(calc_df["SoT"], errors="coerce").fillna(0)
    invalid_shots = calc_df[sot > sh]
    assert len(invalid_shots) == 0, f"Lỗi logic: Có {len(invalid_shots)} cầu thủ có SoT > Sh!"

    # 2. Số bàn thắng (Gls) phải >= 0
    gls = pd.to_numeric(calc_df["Gls"], errors="coerce").fillna(0)
    assert (gls >= 0).all(), "Lỗi: Phát hiện số bàn thắng âm!"

    # 3. Penalty thành công (PK) không thể lớn hơn số lần sút Penalty (PKatt)
    pk = pd.to_numeric(calc_df["PK"], errors="coerce").fillna(0)
    pkatt = pd.to_numeric(calc_df["PKatt"], errors="coerce").fillna(0)
    assert (pk <= pkatt).all(), "Lỗi logic: Số lần ghi bàn PK lớn hơn số lần sút PKatt!"

def test_star_players():
    """Kiểm tra tính xác thực dữ liệu của các ngôi sao hàng đầu Ngoại hạng Anh"""
    df = pd.read_csv(CSV_PATH)
    
    # Kiểm tra Erling Haaland
    haaland = df[df["Player"].str.contains("Haaland", case=False, na=False)]
    assert not haaland.empty, "Lỗi: Không tìm thấy Erling Haaland trong danh sách!"
    haaland_gls = int(haaland.iloc[0]["Gls"])
    assert haaland_gls >= 15, f"Dữ liệu bàn thắng của Haaland bất thường ({haaland_gls})!"
    
    # Kiểm tra Mohamed Salah
    salah = df[df["Player"].str.contains("Salah", case=False, na=False)]
    assert not salah.empty, "Lỗi: Không tìm thấy Mohamed Salah!"
    salah_gls = int(salah.iloc[0]["Gls"])
    assert salah_gls >= 10, f"Dữ liệu bàn thắng của Salah bất thường ({salah_gls})!"

def test_min_playing_time_filter():
    """Kiểm tra điều kiện bắt buộc của đề bài: Lọc cầu thủ thi đấu > 90 phút"""
    df = pd.read_csv(CSV_PATH)
    if "Min" in df.columns:
        mins = pd.to_numeric(df["Min"].astype(str).str.replace(",", "").str.replace("N/a", "0"), errors="coerce")
        assert (mins > 90).all(), "Lỗi: Vẫn còn cầu thủ thi đấu <= 90 phút chưa bị loại bỏ!"

if __name__ == "__main__":
    test_file_exists()
    test_required_columns()
    test_no_percent_symbols()
    test_logical_stat_constraints()
    test_star_players()
    test_min_playing_time_filter()
