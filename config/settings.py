"""Cấu hình chung của project (NGƯỜI 1 — Core/Schema phụ trách).

Mọi module đọc cấu hình từ đây. Với giá trị có thể đổi lúc chạy (SEASON) hãy luôn dùng
``from config import settings`` rồi ``settings.SEASON`` (KHÔNG ``from config.settings import SEASON``).
"""
from __future__ import annotations

# ---- Mùa giải / giải đấu (theo docs/scraper_guide.md: format "2024/2025") ----------
# LƯU Ý: đề gốc mâu thuẫn (Phần I: 2024-2025; Phần II/IV: 2023-2024) -> hỏi giảng viên,
# rồi đổi bằng `python main.py scrape --season 2023/2024`.
SEASON = "2024/2025"
TRANSFER_SEASON = "2023/2024"
LEAGUE = "Premier League"
COUNTRY = "England"

# ---- FBref -------------------------------------------------------------------------
FBREF_COMP_ID = 9
FBREF_COMP_SLUG = "Premier-League"

# ---- Quy tắc nghiệp vụ -------------------------------------------------------------
MIN_MINUTES = 90        # "hơn 90 phút" -> lọc Min > 90 (nghiêm ngặt) khi xuất results.csv
NA = "N/a"              # CHỈ dùng ở file xuất cuối data/final/results*.csv (yêu cầu của đề)
RANDOM_STATE = 42
STD_DDOF = 1            # độ lệch chuẩn mẫu; đổi 0 nếu muốn tổng thể

# ---- Truy cập web (lịch sự, không vượt chặn) ----------------------------------------
REQUEST_DELAY = 7.0     # giây giữa 2 request (FBref giới hạn ~10 request/phút)
WAYBACK_TIMESTAMP = "20251201000000"
USER_AGENT = "Mozilla/5.0 (BaiTapLon-Python student project; polite, rate-limited)"


def normalize_season(value: str) -> str:
    """'2024-2025' / '2024_2025' / '2024/2025' -> '2024/2025'."""
    import re
    m = re.fullmatch(r"\s*(\d{4})\s*[-_/]\s*(\d{4})\s*", str(value))
    if not m:
        raise ValueError(f"Mùa giải không hợp lệ: {value!r} (dùng dạng 2024/2025)")
    return f"{m.group(1)}/{m.group(2)}"


def set_season(value: str) -> None:
    global SEASON
    SEASON = normalize_season(value)


def season_slug(season: str | None = None) -> str:
    """Dạng dùng trong URL của FBref: 2024/2025 -> 2024-2025."""
    return (season or SEASON).replace("/", "-")
