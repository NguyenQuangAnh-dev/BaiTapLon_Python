"""Chạy thử TOÀN BỘ pipeline bằng dữ liệu GIẢ LẬP trong thư mục data_demo/ (không đụng data/)."""
from __future__ import annotations

from src.common.fetcher import Fetcher
from src.common.io_utils import load_results
from src.common.logging_utils import log
from src.common.paths import PATHS, ROOT
from src.pipeline.build_dataset import run_scrape
from src.pipeline.demo_data import make_demo_raw
from src.pipeline.run_clustering import run_clustering
from src.pipeline.run_statistics import run_stats
from src.pipeline.run_transfers import run_transfers, run_valuation
from src.scrapers.player_stats.scraper import ALL_SPECS
from src.visualization.radar import radar_chart


def run_demo(hist_limit: int = 6) -> None:
    PATHS.set(ROOT / "data_demo")
    PATHS.make()
    log("#" * 78)
    log("# CHẾ ĐỘ DEMO: dữ liệu NGẪU NHIÊN do máy tạo, chỉ để kiểm tra chương trình chạy được.")
    log("# KHÔNG dùng kết quả này để nộp. Kết quả thật: python main.py scrape --source wayback")
    log("#" * 78)
    make_demo_raw(ALL_SPECS)
    run_scrape(Fetcher("local"))
    run_stats(load_results(), hist=hist_limit != 0, hist_limit=hist_limit or None)
    run_clustering()
    run_transfers(source="local")
    run_valuation()
    res = load_results()
    out = radar_chart(res.iloc[0]["Player"], res.iloc[1]["Player"],
                      ["Sh_Gls", "Sh_SoT", "SCA_SCA90", "Tkl_Tkl", "PassTot_Cmp%"])
    log(f"Radar mẫu: {out}")
    log(f"\nXong demo. Mọi kết quả nằm trong: {PATHS.base}")
