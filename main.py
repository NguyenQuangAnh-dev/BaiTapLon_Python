#!/usr/bin/env python3
"""Điểm vào của project (NGƯỜI 1). Xem `python main.py --help`.

    python main.py demo                    # chạy thử TOÀN BỘ bằng dữ liệu GIẢ LẬP (data_demo/)
    python main.py scrape --source wayback # PHẦN I : 6 bảng chuẩn + results.csv
    python main.py stats                   # PHẦN II: top/bottom, results2.csv, histogram
    python main.py cluster                 # PHẦN III: K-means + PCA
    python main.py transfers               # PHẦN IV: chuyển nhượng
    python main.py valuation               # PHẦN IV: ước lượng giá trị cầu thủ
    python main.py web                     # web dashboard
    python main.py validate                # kiểm tra schema/ID của 6 bảng
    python main.py all                     # chạy lần lượt tất cả
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import settings
from src.common.fetcher import Fetcher, ScrapeBlocked
from src.common.logging_utils import log
from src.common.paths import PATHS


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Football Data Analysis — pipeline BTL Python")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, helptext in [("scrape", "PHẦN I: thu thập -> 6 bảng chuẩn + results.csv"),
                           ("stats", "PHẦN II: thống kê, results2.csv, histogram"),
                           ("cluster", "PHẦN III: K-means + PCA"),
                           ("transfers", "PHẦN IV: thu thập chuyển nhượng"),
                           ("valuation", "PHẦN IV: ước lượng giá trị cầu thủ"),
                           ("all", "chạy tất cả theo thứ tự"), ("web", "mở web dashboard"),
                           ("validate", "kiểm tra schema/ID 6 bảng"), ("demo", "chạy thử bằng dữ liệu giả lập")]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--data-dir", help="thư mục dữ liệu (mặc định ./data)")
        if name in ("scrape", "transfers", "all"):
            p.add_argument("--source", choices=["fbref", "wayback", "local"], default="fbref",
                           help="fbref: tải trực tiếp | wayback: bản lưu archive.org | local: HTML đã lưu ở data/raw")
            p.add_argument("--season", default=settings.SEASON, help="vd 2024/2025 hoặc 2023/2024")
            p.add_argument("--delay", type=float, default=settings.REQUEST_DELAY, help="giây giữa 2 request")
            p.add_argument("--refresh", action="store_true", help="tải lại, bỏ qua cache data/raw")
        if name in ("transfers", "all"):
            p.add_argument("--transfer-file", help="CSV (Player, Team/Squad, Value/Fee) nếu không scrape được")
        if name in ("stats", "all", "demo"):
            p.add_argument("--no-hist", action="store_true", help="bỏ qua histogram (nhanh hơn)")
            p.add_argument("--hist-limit", type=int, help="chỉ vẽ N thống kê đầu tiên")
        if name in ("cluster", "all"):
            p.add_argument("--k", type=int, help="ép số nhóm k (mặc định: tự chọn theo silhouette)")
            p.add_argument("--no-per90", action="store_true", help="không quy đổi thống kê tổng về /90 phút")
        if name == "web":
            p.add_argument("--host", default="127.0.0.1")
            p.add_argument("--port", type=int, default=8000)
    return ap


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].startswith("--p1"):                  # cú pháp radar của đề, gọi thẳng main.py
        from src.visualization.radar import radar_cli
        return radar_cli(argv)
    args = build_parser().parse_args(argv)
    if getattr(args, "data_dir", None):
        PATHS.set(Path(args.data_dir))
    if hasattr(args, "season"):
        settings.set_season(args.season)
    try:
        if args.cmd == "demo":
            from src.pipeline.run_demo import run_demo
            run_demo(hist_limit=0 if args.no_hist else (args.hist_limit or 6))
        if args.cmd in ("scrape", "all"):
            from src.pipeline.build_dataset import run_scrape
            run_scrape(Fetcher(args.source, args.delay, args.refresh))
        if args.cmd in ("stats", "all"):
            from src.pipeline.run_statistics import run_stats
            run_stats(hist=not args.no_hist, hist_limit=args.hist_limit)
        if args.cmd in ("cluster", "all"):
            from src.pipeline.run_clustering import run_clustering
            run_clustering(k=args.k, per90=not args.no_per90)
        if args.cmd in ("transfers", "all"):
            from src.pipeline.run_transfers import run_transfers
            run_transfers(args.source, args.delay, args.transfer_file)
        if args.cmd in ("valuation", "all"):
            from src.pipeline.run_transfers import run_valuation
            run_valuation()
        if args.cmd == "validate":
            from src.pipeline.build_dataset import load_tables, validate_all
            issues = validate_all(load_tables())
            log("\n".join(f"⚠ {i}" for i in issues) if issues else "✔ 6 bảng đúng schema và ID liên kết hợp lệ")
            return 1 if issues else 0
        if args.cmd == "web":
            from src.web.app import serve_web
            serve_web(args.host, args.port)
    except (ScrapeBlocked, FileNotFoundError) as exc:
        print(f"\nDỪNG: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
