# Bảng mở rộng `player_stats_extended` và quan hệ với 6 bảng chuẩn

`docs/scraper_guide.md` cấm tự ý thêm cột vào dataset chính. Nhưng đề bài yêu cầu một bảng **rất rộng**
(~170 thống kê/cầu thủ). Giải pháp: giữ nguyên 6 bảng chuẩn, và thêm **một bảng phụ** để lưu phần mở rộng.

```text
FBref (10 bảng)  ──►  player_stats_extended (processed, mọi cầu thủ, có player_id/team_id, thiếu = NaN)
                          ├──►  players        (1 dòng/cầu thủ)
                          ├──►  player_stats   (cộng dồn theo player_id, 20 cột chuẩn)
                          └──►  results.csv    (final: lọc Min > 90, sắp xếp, thiếu = "N/a", bỏ cột ID)
```

> Đề nghị Người 1 xác nhận hướng này với nhóm trước khi chốt. Nếu nhóm muốn mở rộng schema chính thức,
> hãy cập nhật `DATA_DICTIONARY.md` + `src/common/schema.py` cùng lúc.

## Ánh xạ sang `player_stats` (xem `src/preprocessing/canonical_tables.py`)

| player_stats | Lấy từ bảng mở rộng | Ghi chú |
|---|---|---|
| matches, starts, minutes | `MP`, `Starts`, `Min` | cộng dồn nếu cầu thủ có nhiều dòng (chuyển đội giữa mùa) |
| goals | `Perf_G-PK` + `Perf_PK` | bàn thắng gồm cả phạt đền |
| assists | `Perf_Ast` | |
| shots, shots_on_target | `Sh_Sh`, `Sh_SoT` | |
| passes | `PassTot_Att` | số chuyền **thực hiện** (attempted) |
| key_passes | `PassExp_KP` | |
| pass_accuracy | `PassTot_Cmp%` | trung bình có trọng số theo `PassTot_Att` |
| tackles, interceptions, clearances, blocks | `Tkl_Tkl`, `Blk_Int`, `Blk_Clr`, `Blk_Blocks` | |
| duels_won | `Aerial_Won` | **chỉ không chiến** (FBref không có "duels" tổng) — cần Core duyệt |
| yellow_cards, red_cards | `Perf_CrdY`, `Perf_CrdR` | |

## Các quyết định cần nhóm biết

* **ID**: `team_id = slug(tên đội)`, `player_id = slug(tên)-quốc tịch` (không chứa tên đội → cầu thủ chuyển đội
  giữa mùa vẫn có **một** `player_id`). Hai cầu thủ khác nhau cùng tên + cùng quốc tịch sẽ bị coi là một người.
* **`players.date_of_birth`** để thiếu vì FBref chỉ có năm sinh; **`players.team_id`** = đội có nhiều phút nhất.
* **`team_stats`**: W/D/L, bàn thắng, điểm, clean sheet **tính từ bảng `matches`**; possession/shots lấy từ bảng đội FBref.
* **`transfers`**: `transfer_fee` tính bằng triệu EUR; đội ngoài giải → `from_team_id`/`to_team_id` để thiếu
  (khóa ngoại chỉ trỏ tới `teams`); cầu thủ không khớp bảng `players` bị bỏ.
* **Thiếu dữ liệu**: tầng processed để ô trống; chỉ `data/final/results*.csv` ghi `N/a`.
