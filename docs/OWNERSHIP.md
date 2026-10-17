# Phân công theo file (10 người)

Dựa trên "Kế hoạch phân công BTL Python 10 người v2". Mỗi người **chỉ sửa file của mình**; cần sửa file
chung (`src/common`, `config`, `src/preprocessing`) → báo Người 1. Mỗi người có file test riêng trong `tests/`.

| # | Vai trò | File phụ trách | Test | Bàn giao |
|---|---|---|---|---|
| 1 | Core / Schema / Tích hợp | `config/*`, `src/common/*`, `src/preprocessing/*`, `src/scrapers/base.py`, `src/scrapers/player_stats/scraper.py`, `src/pipeline/*`, `main.py`, `docs/*` | `test_p1_core.py` | schema + ID + merge + `results.csv` + `sources.csv` + 6 bảng hợp lệ |
| 2 | Cơ bản, danh sách cầu thủ, đội | `scrapers/player_stats/basic.py`, `scrapers/players/scraper.py`, `scrapers/teams/scraper.py` | `test_p2_basic_players_teams.py` | `players`, `teams`, cột cơ bản (Nation, Pos, Age, MP, Starts, Min, Perf, Exp, Prog, P90) |
| 3 | Shooting + Matches | `scrapers/player_stats/shooting.py`, `scrapers/matches/scraper.py` | `test_p3_shooting_matches.py` | cột Sh_*, ShExp_*; bảng `matches` (380 trận) |
| 4 | Passing + Team stats | `scrapers/player_stats/passing.py`, `scrapers/team_stats/scraper.py` | `test_p4_passing_team_stats.py` | cột PassTot/Short/Med/Long/Exp; bảng `team_stats` |
| 5 | Pass types + SCA/GCA | `scrapers/player_stats/passing_types.py`, `scrapers/player_stats/gca.py` | `test_p5_passing_types_gca.py` | cột PTyp_, Corner_, POut_, SCA_, SCAType_, GCA_, GCAType_ |
| 6 | Defense + Goalkeeping* | `scrapers/player_stats/defense.py`, `scrapers/player_stats/goalkeeper.py` | `test_p6_defense_goalkeeper.py` | cột Tkl_, Chall_, Blk_, GK_, GKPK_ |
| 7 | Possession + Playing time + Misc | `scrapers/player_stats/possession.py`, `playing_time.py`, `misc.py` | `test_p7_possession_playing_time_misc.py` | cột Touch_, TakeOn_, Carry_, Recv_, Start_, Sub_, Team_, TeamxG_, Misc_, Aerial_ |
| 8 | Statistics + Histogram (Phần II) | `analysis/statistics.py`, `analysis/team_ranking.py`, `visualization/histograms.py`, `visualization/plot_utils.py`, `pipeline/run_statistics.py` | `test_p8_statistics.py` | `results2.csv`, `top3_bottom3.csv`, histogram, `team_analysis.txt` |
| 9 | K-means + PCA (Phần III) | `analysis/clustering.py`, `visualization/cluster_plots.py`, `pipeline/run_clustering.py` | `test_p9_clustering.py` | hình Elbow/Silhouette/PCA, `cluster_result.csv`, `cluster_report.txt` |
| 10 | Radar + Transfers + Web (Phần III, IV) | `visualization/radar.py`, `radarChartPlot.py`, `scrapers/transfers/*`, `analysis/valuation.py`, `web/app.py`, `pipeline/run_transfers.py` | `test_p10_radar_transfers_web.py` | radar, bảng `transfers`, `value_estimates.csv`, `valuation_method.md`, web |

\* Kế hoạch v2 chưa giao phần thủ môn → tạm gán Người 6 (nhóm có thể điều chỉnh).

## Thứ tự phụ thuộc (ai cần chờ ai)

```text
Người 1 (schema, ID, fetcher, parser)
   └─► Người 2–7 (scraper theo bảng FBref)  ──►  Người 1 (merge → 6 bảng + results.csv)
                                                    └─► Người 8, 9, 10 (đọc results.csv / bảng chuẩn)
```

Người 8–10 có thể làm ngay từ đầu bằng `python main.py demo` (dữ liệu giả lập) rồi đổi sang dữ liệu thật.

## Thêm một thống kê mới vào scraper của bạn

1. Thêm `(nhóm_FBref, tên_cột_FBref, tên_cột_chuẩn)` vào `SPEC_...` trong file của bạn (dùng `cols(...)`).
2. Tên cột chuẩn theo mẫu `Nhóm_Thống kê` (vd. `Sh_SoT`, `Tkl_TklW`) và **không trùng** cột đã có.
3. Cập nhật `must_numeric` trong test của bạn. Chạy `pytest tests/test_pN_*.py`.
4. Cột mới chỉ nằm ở bảng mở rộng/`results.csv`; **không** thêm vào 6 bảng chuẩn khi chưa được Người 1 duyệt.
