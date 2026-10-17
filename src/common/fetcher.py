"""Tải HTML lịch sự (giãn cách, cache vào data/raw) — KHÔNG vượt cơ chế chặn của website."""
from __future__ import annotations

import time

from config import settings
from src.common.logging_utils import log
from src.common.paths import PATHS


class ScrapeBlocked(RuntimeError):
    """Website chặn truy cập tự động -> dừng, KHÔNG vượt cơ chế bảo vệ."""


# Hậu tố URL của từng "page" trên FBref (mặc định là 'Stats')
_PAGE_SUFFIX = {"schedule": "Scores-and-Fixtures"}


class Fetcher:
    """source = 'fbref' (tải trực tiếp) | 'wayback' (bản lưu archive.org) | 'local' (HTML đã lưu ở data/raw)."""

    def __init__(self, source: str = "fbref", delay: float = settings.REQUEST_DELAY, refresh: bool = False):
        assert source in ("fbref", "wayback", "local"), source
        self.source, self.delay, self.refresh = source, delay, refresh
        self.urls: dict[str, str] = {}
        self._last_request = 0.0

    def fbref_url(self, page: str) -> str:
        slug = settings.season_slug()
        suffix = _PAGE_SUFFIX.get(page, "Stats")
        return (f"https://fbref.com/en/comps/{settings.FBREF_COMP_ID}/{slug}/{page}/"
                f"{slug}-{settings.FBREF_COMP_SLUG}-{suffix}")

    def url_for(self, page: str) -> str:
        url = self.fbref_url(page)
        if self.source == "wayback":
            return f"https://web.archive.org/web/{settings.WAYBACK_TIMESTAMP}id_/{url}"
        return url

    def get_html(self, page: str) -> str:
        """Trả HTML của một trang; ưu tiên cache data/raw/<page>.html để không gọi lại website."""
        cache = PATHS.raw / f"{page}.html"
        self.urls[page] = self.url_for(page)
        if cache.exists() and not self.refresh:
            return cache.read_text(encoding="utf-8", errors="ignore")
        if self.source == "local":
            raise FileNotFoundError(
                f"Thiếu file {cache}.\nMở {self.fbref_url(page)} trên trình duyệt -> Save page as -> "
                f"'Webpage, HTML only' -> lưu thành {cache}")
        html = self.download(self.urls[page])
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(html, encoding="utf-8")
        return html

    def download(self, url: str) -> str:
        import requests
        wait = self.delay - (time.time() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(3):
            try:
                log(f"   GET {url}")
                r = requests.get(url, headers={"User-Agent": settings.USER_AGENT}, timeout=30)
                self._last_request = time.time()
            except requests.RequestException as exc:
                log(f"   ! lỗi mạng ({exc}); thử lại {attempt + 1}/3")
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code == 200:
                return r.text
            if r.status_code == 429 and attempt < 2:      # quá tải -> chờ đúng yêu cầu của server
                ra = str(r.headers.get("Retry-After", "60"))
                time.sleep(int(ra) if ra.isdigit() else 60)
                continue
            if r.status_code in (403, 429, 503):
                raise ScrapeBlocked(
                    f"{url} trả về HTTP {r.status_code} (bị chặn truy cập tự động).\n"
                    "KHÔNG cố vượt chặn. Hãy: (1) thử --source wayback, hoặc (2) mở trang bằng trình duyệt, "
                    "Save page as HTML vào data/raw/<page>.html rồi chạy --source local, hoặc (3) báo Người 1 đổi nguồn.")
            r.raise_for_status()
        raise ScrapeBlocked(f"Không tải được {url} sau 3 lần thử.")
