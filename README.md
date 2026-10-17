# BaiTapLon_Python — Football Data Analysis (Premier League, mùa 2024/2025)

Bài tập lớn Python: thu thập dữ liệu cầu thủ/đội bóng, chuẩn hóa, thống kê, phân cụm K-means + PCA,
radar chart, ước lượng giá trị chuyển nhượng và web dashboard. Làm việc nhóm **10 người**, mỗi người
phụ trách một cụm file (xem [`docs/OWNERSHIP.md`](docs/OWNERSHIP.md)).

## 1. Chạy nhanh

```bash
pip install -r requirements.txt

python main.py demo        # chạy thử TOÀN BỘ bằng dữ liệu GIẢ LẬP -> thư mục data_demo/
pytest                     # 35 test của cả 10 người (chạy offline, không đụng data/)

# Dữ liệu thật
python main.py scrape --source wayback   # Phần I  : 6 bảng chuẩn + data/final/results.csv
python main.py stats                     # Phần II : top/bottom, results2.csv, histogram
python main.py cluster                   # Phần III: K-means + PCA
python main.py transfers                 # Phần IV : chuyển nhượng
python main.py valuation                 # Phần IV : ước lượng giá trị
python main.py web                       # http://127.0.0.1:8000
python main.py validate                  # kiểm tra schema + ID liên kết của 6 bảng

python radarChartPlot.py --p1 "Mohamed Salah" --p2 "Erling Haaland" --Attribute Sh_Gls,Sh_SoT,SCA_SCA90
```

## 2. Cấu trúc project

```text
BaiTapLon_Python/
├── main.py                     # điểm vào CLI                                  (Người 1)
├── radarChartPlot.py           # cú pháp radar theo đề                         (Người 10)
├── config/
│   ├── settings.py             # SEASON, LEAGUE, quy tắc nghiệp vụ             (Người 1)
│   └── team_aliases.py         # tên đội khác nhau giữa các website            (Người 1)
├── src/
│   ├── common/                 # paths, fetcher, parser FBref, schema, ids, io (Người 1)
│   ├── preprocessing/          # cleaning, merge, filters, validation, bảng chuẩn (Người 1)
│   ├── scrapers/
│   │   ├── players/  teams/                      # Người 2
│   │   ├── player_stats/                         # basic(2) shooting(3) passing(4) passing_types+gca(5)
│   │   │                                         # defense+goalkeeper(6) possession+playing_time+misc(7)
│   │   ├── matches/                              # Người 3
│   │   ├── team_stats/                           # Người 4
│   │   └── transfers/                            # Người 10
│   ├── analysis/               # statistics, team_ranking (8) · clustering (9) · valuation (10)
│   ├── visualization/          # histograms (8) · cluster_plots (9) · radar (10) · plot_utils
│   ├── web/app.py              # web dashboard                                 (Người 10)
│   └── pipeline/               # build_dataset, export_results, run_*, demo    (Người 1)
├── tests/                      # mỗi người một file test_pN_*.py
├── data/
│   ├── raw/                    # HTML gốc (cache), KHÔNG ghi đè
│   ├── processed/              # 6 bảng chuẩn + player_stats_extended (thiếu = ô trống/NaN)
│   └── final/                  # SẢN PHẨM NỘP: results.csv, results2.csv, plots/, báo cáo
└── docs/                       # DATA_DICTIONARY, schema, scraper_guide, OWNERSHIP, EXTENDED_STATS
```

## 3. Luồng dữ liệu (3 tầng)

```text
data/raw  ──►  data/processed  ──►  data/final
HTML gốc       6 bảng chuẩn          results.csv  (lọc Min > 90, sắp xếp, thiếu = "N/a")
(cache)        + bảng mở rộng        results2.csv, top3_bottom3.csv, plots/, cluster_*, value_*
               thiếu = NaN
```

* **Tầng processed** tuân thủ đúng `docs/DATA_DICTIONARY.md` và `docs/scraper_guide.md`
  (tên cột, kiểu, season `2024/2025`, thiếu = NULL/NaN, không tự điền 0).
* **Tầng final** là sản phẩm của đề bài. Chỉ ở đây dữ liệu thiếu mới ghi **`N/a`** (đề yêu cầu).
* 5 bảng chuẩn (players, teams, player_stats, team_stats, matches) sinh ra cùng lúc ở `scrape`;
  `transfers` sinh ở bước `transfers`. Chi tiết bảng mở rộng: [`docs/EXTENDED_STATS.md`](docs/EXTENDED_STATS.md).

## 4. Phần việc của đề ↔ module

| Phần của đề | Lệnh | Module chính |
|---|---|---|
| I. Thu thập → `results.csv` | `scrape` | `src/scrapers/*`, `src/pipeline/build_dataset.py` |
| II. Thống kê, `results2.csv`, histogram, đội tốt nhất | `stats` | `src/analysis/statistics.py`, `team_ranking.py`, `src/visualization/histograms.py` |
| III. K-means, PCA, radar | `cluster`, `radarChartPlot.py` | `src/analysis/clustering.py`, `src/visualization/*` |
| IV. Chuyển nhượng, ước lượng giá trị | `transfers`, `valuation` | `src/scrapers/transfers`, `src/analysis/valuation.py` |

## 5. Lưu ý quan trọng

1. **Mùa giải trong đề mâu thuẫn** (Phần I: 2024-2025; Phần II/IV: 2023-2024). Mặc định `2024/2025`.
   Sau khi hỏi giảng viên: `python main.py scrape --season 2023/2024` hoặc sửa `config/settings.py`.
2. **FBref đã gỡ dữ liệu nâng cao (xG, PrgC, SCA/GCA...) từ tháng 1/2026** (Opta chấm dứt hợp đồng).
   Hãy thử `--source wayback` (bản lưu archive.org) trước; nếu thiếu, lưu HTML thủ công vào `data/raw/`
   rồi chạy `--source local`, hoặc thả CSV nguồn khác vào `data/raw/supplement_*.csv`
   (cột `Player`, `Squad` + tên cột chuẩn) để tự điền ô còn thiếu.
3. Website chặn (403/429) → chương trình **dừng và hướng dẫn**, không vượt chặn.
   Giãn cách mặc định 7 giây/request, có cache nên chạy lại không gọi lại website.
4. Dữ liệu `demo` là **ngẫu nhiên**, chỉ để kiểm thử. Không nộp.
5. Địa chỉ trang chuyển nhượng (`TRANSFER_URL` trong `src/scrapers/transfers/scraper.py`) chưa được kiểm tra với
   website thật; nếu không đọc được, dùng `python main.py transfers --transfer-file file.csv`.

## 6. Quy trình làm việc nhóm

Đọc `docs/scraper_guide.md` (schema, ID, season, thiếu dữ liệu, Git workflow, commit message).
Mỗi người một branch (vd. `scraper/matches`, `analysis/clustering`), không push thẳng `main`,
chạy `pytest` + `python main.py validate` trước khi tạo Pull Request.
