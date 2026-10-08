import os
import sys
from pathlib import Path
import unicodedata
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import numpy as np


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parents[3]

FBREF_SHOOTING_URL = "https://fbref.com/en/comps/9/2023-2024/shooting/2023-2024-Premier-League-Stats"
CACHE_HTML_PATH = ROOT_DIR / "data" / "raw" / "fbref_shooting.html"
BACKUP_CSV_URL = "https://raw.githubusercontent.com/hadjdeh/football-data-analysis/main/Scraping_fbref_static_data/data/current_season/2024-03-18/top5_leagues_outfields_2023_2024.csv"
LOCAL_RAW_CSV = ROOT_DIR / "data" / "raw" / "fbref_pl_2023_2024.csv"
OUTPUT_PROCESSED_CSV = ROOT_DIR / "data" / "processed" / "shooting.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def normalize_text(text):
    """Chuẩn hóa chuỗi tên: xóa khoảng trắng thừa, loại bỏ diacritics"""
    if pd.isna(text) or text is None:
        return ""
    text_str = str(text).strip()
    normalized = unicodedata.normalize('NFKD', text_str).encode('ascii', 'ignore').decode('utf-8')
    return " ".join(normalized.split())

def standardize_squad(squad):
    """Chuẩn hóa tên đội bóng"""
    if pd.isna(squad) or squad is None:
        return ""
    squad_map = {
        "Man City": "Manchester City",
        "Man Utd": "Manchester United",
        "Newcastle Utd": "Newcastle United",
        "Tottenham": "Tottenham Hotspur",
        "Spurs": "Tottenham Hotspur",
        "Wolves": "Wolverhampton Wanderers",
        "Brighton": "Brighton & Hove Albion",
        "West Ham": "West Ham United",
        "Nott'm Forest": "Nottingham Forest",
        "Sheffield Utd": "Sheffield United",
    }
    s = str(squad).strip()
    return squad_map.get(s, s)

def fetch_shooting_data():
    """
    Thu thập dữ liệu Shooting:
    1. Thử cào trực tiếp từ FBref (kèm cache cục bộ vào data/raw/)
    2. Nếu FBref kích hoạt Cloudflare (403), tự động đọc từ bộ dữ liệu FBref 2023-2024 chuẩn
    """
    os.makedirs(ROOT_DIR / "data" / "raw", exist_ok=True)

    html_content = None
    if os.path.exists(CACHE_HTML_PATH) and os.path.getsize(CACHE_HTML_PATH) > 1000:
        with open(CACHE_HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        try:
            r = requests.get(FBREF_SHOOTING_URL, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                html_content = r.text
                with open(CACHE_HTML_PATH, "w", encoding="utf-8") as f:
                    f.write(html_content)
        except Exception:
            pass

    rows = []
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", id="stats_shooting")
        if table is None:
            comments = soup.find_all(string=lambda t: isinstance(t, Comment))
            for c in comments:
                if 'id="stats_shooting"' in c:
                    table = BeautifulSoup(c, "html.parser").find("table", id="stats_shooting")
                    break

        if table:
            tbody = table.find("tbody")
            for tr in tbody.find_all("tr"):
                if tr.get("class") and "thead" in tr.get("class"):
                    continue
                th = tr.find("th", {"data-stat": "player"})
                if not th or not th.text.strip():
                    continue
                def g(stat):
                    td = tr.find("td", {"data-stat": stat})
                    return td.text.strip().replace("%", "").replace(",", "") if td and td.text.strip() else np.nan

                nation_raw = g("nationality")
                nation = nation_raw.split()[-1] if pd.notna(nation_raw) else np.nan

                rows.append({
                    "Player": normalize_text(th.text.strip()),
                    "Nation": nation,
                    "Pos": g("position"),
                    "Squad": standardize_squad(g("team")),
                    "Age": g("age"),
                    "Min": g("minutes"),
                    "90s": g("minutes_90s"),
                    "Gls": g("goals"),
                    "Sh": g("shots"),
                    "SoT": g("shots_on_target"),
                    "SoT%": g("shots_on_target_pct"),
                    "Sh/90": g("shots_per90"),
                    "SoT/90": g("shots_on_target_per90"),
                    "G/Sh": g("goals_per_shot"),
                    "G/SoT": g("goals_per_shot_on_target"),
                    "Dist": g("average_shot_distance"),
                    "FK": g("shots_free_kicks"),
                    "PK": g("pens_made"),
                    "PKatt": g("pens_att"),
                    "xG": g("xg"),
                    "npxG": g("npxg"),
                    "npxG/Sh": g("npxg_per_shot"),
                    "G-xG": g("xg_net"),
                    "np:G-xG": g("npxg_net"),
                })

    if not rows:
        if not os.path.exists(LOCAL_RAW_CSV):
            raw_full = pd.read_csv(BACKUP_CSV_URL)
            pl_only = raw_full[raw_full["league_name"] == "Premier-League"].copy()
            pl_only.to_csv(LOCAL_RAW_CSV, index=False, encoding="utf-8-sig")
            raw_df = pl_only
        else:
            raw_df = pd.read_csv(LOCAL_RAW_CSV)

        for _, r in raw_df.iterrows():
            nation_raw = str(r.get("nationality", ""))
            nation = nation_raw.split()[-1] if nation_raw and nation_raw != "nan" else np.nan
            rows.append({
                "Player": normalize_text(r.get("player")),
                "Nation": nation,
                "Pos": r.get("position"),
                "Squad": standardize_squad(r.get("team")),
                "Age": r.get("age"),
                "Min": r.get("minutes"),
                "90s": r.get("minutes_90s"),
                "Gls": r.get("goals"),
                "Sh": r.get("shots"),
                "SoT": r.get("shots_on_target"),
                "SoT%": r.get("shots_on_target_pct"),
                "Sh/90": r.get("shots_per90"),
                "SoT/90": r.get("shots_on_target_per90"),
                "G/Sh": r.get("goals_per_shot"),
                "G/SoT": r.get("goals_per_shot_on_target"),
                "Dist": r.get("average_shot_distance"),
                "FK": r.get("shots_free_kicks"),
                "PK": r.get("pens_made"),
                "PKatt": r.get("pens_att"),
                "xG": r.get("xg"),
                "npxG": r.get("npxg"),
                "npxG/Sh": r.get("npxg_per_shot"),
                "G-xG": r.get("xg_net"),
                "np:G-xG": r.get("npxg_net"),
            })

    return pd.DataFrame(rows)

def clean_and_validate_shooting(df):
    """
    Làm sạch dữ liệu, lọc Min > 90 và khử trùng lặp
    """
    df = df.copy()

    # Lọc cầu thủ thi đấu > 90 phút
    if "Min" in df.columns:
        df["Min_num"] = pd.to_numeric(df["Min"].astype(str).str.replace(",", "").str.replace("N/a", ""), errors="coerce").fillna(0)
        df = df[df["Min_num"] > 90].copy()
        df.drop(columns=["Min_num"], inplace=True)

    df.drop_duplicates(subset=["Player", "Squad"], keep="first", inplace=True)

    int_cols = ["Gls", "Sh", "SoT", "FK", "PK", "PKatt"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    float_cols = ["SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT", "Dist", "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    df.sort_values(by="Gls", ascending=False, inplace=True)
    return df

def save_and_report(df):
    """
    Lưu dữ liệu ra file CSV tại data/processed/shooting.csv
    """
    export_df = df.astype(object).fillna("N/a")

    os.makedirs(OUTPUT_PROCESSED_CSV.parent, exist_ok=True)
    export_df.to_csv(OUTPUT_PROCESSED_CSV, index=False, encoding="utf-8-sig")
    return export_df

def run_scraper():
    raw_df = fetch_shooting_data()
    cleaned_df = clean_and_validate_shooting(raw_df)
    save_and_report(cleaned_df)
    return cleaned_df

if __name__ == "__main__":
    run_scraper()
