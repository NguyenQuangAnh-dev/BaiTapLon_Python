"""NGƯỜI 10 — bảng `transfers` (transfer_id, player_id, transfer_date, from_team_id, to_team_id, transfer_fee).

Nguồn mặc định: footballtransfers.com (danh sách có phân trang). Website có thể đổi cấu trúc hoặc dựng bảng bằng
JavaScript: khi đó lưu HTML thủ công vào data/raw/transfers_page_N.html hoặc dùng --transfer-file (CSV).

* transfer_fee tính bằng TRIỆU EURO (số thực). 'Free'/'Loan'/không rõ -> thiếu (không điền 0).
* Đội ở NGOÀI giải (không có trong bảng teams) -> from_team_id/to_team_id để thiếu (khóa ngoại phải hợp lệ).
* Cầu thủ không khớp được với bảng players bị bỏ (khóa ngoại) — số lượng được in ra để kiểm tra.
"""
from __future__ import annotations

import hashlib
from typing import Optional

import numpy as np
import pandas as pd

from config import settings
from src.common.fetcher import Fetcher, ScrapeBlocked
from src.common.ids import match_player_id, match_team_id
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.common.schema import enforce_schema, validate_table
from src.common.sources import log_source
from src.preprocessing.cleaning import normalize_player_name
from src.scrapers.transfers.parsing import parse_money, parse_transfer_html

TRANSFER_SITE = "https://www.footballtransfers.com"
TRANSFER_URL = TRANSFER_SITE + "/en/players/uk-premier-league/{page}"     # sửa nếu website đổi cấu trúc
TRANSFER_MAX_PAGES = 40


def _raw_from_csv(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    low = {c.lower(): c for c in raw.columns}
    pick = lambda *keys: next((low[k] for k in low if any(w in k for w in keys)), None)
    pcol, vcol = pick("player"), pick("value", "fee", "price")
    if not (pcol and vcol):
        raise ValueError("CSV cần có cột Player và một cột Value/Fee/Price")
    scol, dcol, fcol, tcol = pick("squad", "team", "club"), pick("date"), pick("from"), low.get("to")
    return pd.DataFrame({"Player": raw[pcol].map(normalize_player_name),
                         "Date": raw[dcol].astype(str) if dcol else np.nan,
                         "From": raw[fcol] if fcol else np.nan,
                         "To": raw[tcol] if tcol else (raw[scol] if scol else np.nan),
                         "Raw_Fee": raw[vcol].astype(str), "Fee_M": raw[vcol].map(parse_money)})


def collect_raw(source: str = "fbref", delay: float = settings.REQUEST_DELAY,
                transfer_file: Optional[str] = None, max_pages: int = TRANSFER_MAX_PAGES) -> pd.DataFrame:
    """Thu thập thô (có cache ở data/raw/transfers_page_N.html). Bị chặn -> dừng, không vượt chặn."""
    if transfer_file:
        return _raw_from_csv(transfer_file)
    fetcher = Fetcher("local" if source == "local" else "fbref", delay=delay)
    pages, seen = [], set()
    for page in range(1, max_pages + 1):
        cache = PATHS.raw / f"transfers_page_{page}.html"
        if cache.exists():
            html = cache.read_text(encoding="utf-8", errors="ignore")
        elif source == "local":
            break
        else:
            try:
                html = fetcher.download(TRANSFER_URL.format(page=page))
            except ScrapeBlocked as exc:
                log(f"   !! {str(exc).splitlines()[0]}\n   KHÔNG vượt chặn. Lưu trang bằng trình duyệt vào "
                    f"{cache} hoặc dùng --transfer-file.")
                break
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(html, encoding="utf-8")
        part = parse_transfer_html(html)
        key = part["Player"] + "|" + part["To"].astype(str) if not part.empty else part
        new = part[~key.isin(seen)] if not part.empty else part
        if new.empty:
            break
        seen.update(key.loc[new.index])
        pages.append(new)
    return pd.concat(pages, ignore_index=True) if pages else pd.DataFrame(
        columns=["Player", "Date", "From", "To", "Raw_Fee", "Fee_M"])


def build_transfers(raw: pd.DataFrame, players: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa -> đúng schema `transfers`, ID khớp với players/teams."""
    rows, dropped = [], 0
    for r in raw.to_dict("records"):
        to_id, from_id = match_team_id(r.get("To"), teams), match_team_id(r.get("From"), teams)
        pid = match_player_id(r.get("Player"), players, team_id=to_id)
        if pid is None:
            dropped += 1
            continue
        date = pd.to_datetime(r.get("Date"), errors="coerce")
        fee = r.get("Fee_M")
        fee = np.nan if fee is None else fee
        key = f"{pid}|{date}|{from_id}|{to_id}|{fee}"
        rows.append({"transfer_id": "T" + hashlib.sha1(key.encode()).hexdigest()[:10], "player_id": pid,
                     "transfer_date": date, "from_team_id": from_id, "to_team_id": to_id, "transfer_fee": fee})
    if dropped:
        log(f"   ! {dropped} dòng chuyển nhượng không khớp cầu thủ trong bảng players (đã bỏ)")
    out = enforce_schema(pd.DataFrame(rows), "transfers").drop_duplicates("transfer_id").reset_index(drop=True)
    return out


def scrape_transfers(players: pd.DataFrame, teams: pd.DataFrame, source: str = "fbref",
                     delay: float = settings.REQUEST_DELAY, transfer_file: Optional[str] = None) -> pd.DataFrame:
    raw = collect_raw(source, delay, transfer_file)
    out = build_transfers(raw, players, teams)
    for issue in validate_table(out, "transfers"):
        log(f"   ⚠ {issue}")
    origin = str(transfer_file) if transfer_file else TRANSFER_URL
    log_source("transfers", "transfer_fee", "footballtransfers.com", origin, notes=f"{len(out)} dòng")
    log(f"[Người 10] transfers: {len(out)} dòng ({int(out['transfer_fee'].notna().sum())} có phí)")
    return out
