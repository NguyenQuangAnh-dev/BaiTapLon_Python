# Lược đồ dữ liệu

## Thông tin dự án

**Football Data Analysis – Mùa giải 2024/2025**

## Mục đích

Tài liệu này định nghĩa cấu trúc dữ liệu, khóa chính, khóa ngoại và mối quan hệ giữa các bảng dữ liệu cốt lõi được sử dụng trong project.

---

## 1. Các bảng dữ liệu chính

Project gồm 6 bảng dữ liệu chính:

* `players` – Thông tin cầu thủ
* `teams` – Thông tin đội bóng
* `player_stats` – Thống kê cầu thủ
* `team_stats` – Thống kê đội bóng
* `matches` – Thông tin trận đấu
* `transfers` – Thông tin chuyển nhượng

Chi tiết về các cột, kiểu dữ liệu, ý nghĩa và trường bắt buộc được mô tả trong [`DATA_DICTIONARY.md`](./DATA_DICTIONARY.md).

---

## 2. Khóa chính (Primary Key)

| Bảng           | Khóa chính                    |
| -------------- | ----------------------------- |
| `players`      | `player_id`                   |
| `teams`        | `team_id`                     |
| `player_stats` | `(player_id, season, league)` |
| `team_stats`   | `(team_id, season, league)`   |
| `matches`      | `match_id`                    |
| `transfers`    | `transfer_id`                 |

### Giải thích

Đối với `player_stats`, một cầu thủ có thể có nhiều bản ghi thống kê theo các mùa giải hoặc giải đấu khác nhau.

Do đó sử dụng tổ hợp:

```text
(player_id, season, league)
```

để xác định duy nhất một bản ghi thống kê.

Tương tự, `team_stats` sử dụng:

```text
(team_id, season, league)
```

---

## 3. Khóa ngoại (Foreign Key)

| Bảng           | Cột            | Tham chiếu đến      |
| -------------- | -------------- | ------------------- |
| `players`      | `team_id`      | `teams.team_id`     |
| `player_stats` | `player_id`    | `players.player_id` |
| `team_stats`   | `team_id`      | `teams.team_id`     |
| `matches`      | `home_team_id` | `teams.team_id`     |
| `matches`      | `away_team_id` | `teams.team_id`     |
| `transfers`    | `player_id`    | `players.player_id` |
| `transfers`    | `from_team_id` | `teams.team_id`     |
| `transfers`    | `to_team_id`   | `teams.team_id`     |

---

## 4. Mối quan hệ giữa các bảng

### 4.1. `teams` → `players`

Một đội bóng có thể có nhiều cầu thủ.

```text
teams.team_id
      │
      └──────< players.team_id
```

Quan hệ:

```text
teams 1 ──── N players
```

Trong đó:

* `teams.team_id`: khóa chính
* `players.team_id`: khóa ngoại

---

### 4.2. `players` → `player_stats`

Một cầu thủ có thể có nhiều bản ghi thống kê theo mùa giải và giải đấu.

```text
players.player_id
       │
       └──────< player_stats.player_id
```

Quan hệ:

```text
players 1 ──── N player_stats
```

Một bản ghi trong `player_stats` được xác định duy nhất bởi:

```text
(player_id, season, league)
```

---

### 4.3. `teams` → `team_stats`

Một đội bóng có thể có nhiều bản ghi thống kê theo mùa giải và giải đấu.

```text
teams.team_id
     │
     └──────< team_stats.team_id
```

Quan hệ:

```text
teams 1 ──── N team_stats
```

Một bản ghi trong `team_stats` được xác định duy nhất bởi:

```text
(team_id, season, league)
```

---

### 4.4. `teams` → `matches`

Mỗi trận đấu có hai đội:

* `home_team_id`: đội chủ nhà
* `away_team_id`: đội khách

Cả hai đều tham chiếu đến `teams.team_id`.

```text
                    ┌── home_team_id
teams.team_id ──────┤
                    └── away_team_id
```

Quan hệ:

```text
teams 1 ──── N matches (đội chủ nhà)
teams 1 ──── N matches (đội khách)
```

Một đội có thể xuất hiện trong nhiều trận đấu với tư cách đội chủ nhà hoặc đội khách.

---

### 4.5. `players` → `transfers`

Một cầu thủ có thể có nhiều lần chuyển nhượng.

```text
players.player_id
       │
       └──────< transfers.player_id
```

Quan hệ:

```text
players 1 ──── N transfers
```

Trong đó:

* `players.player_id`: khóa chính
* `transfers.player_id`: khóa ngoại

---

### 4.6. `teams` → `transfers`

Một bản ghi chuyển nhượng liên quan đến tối đa hai đội:

* `from_team_id`: đội bóng cũ
* `to_team_id`: đội bóng mới

Cả hai đều tham chiếu đến `teams.team_id`.

```text
                    ┌── from_team_id
teams.team_id ──────┤
                    └── to_team_id
```

Quan hệ:

```text
teams 1 ──── N transfers (đội cũ)
teams 1 ──── N transfers (đội mới)
```

---

## 5. Sơ đồ quan hệ tổng thể

```text
                         ┌─────────────┐
                         │    teams    │
                         │─────────────│
                         │ PK team_id  │
                         └──────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ↓                 ↓                 ↓
        ┌──────────┐      ┌────────────┐    ┌──────────┐
        │ players  │      │ team_stats │    │ matches  │
        └────┬─────┘      └────────────┘    └────┬─────┘
             │                                    │
             ↓                                    │
       ┌─────────────┐                            │
       │player_stats │                            │
       └─────────────┘                            │
                                                  │
                         ┌────────────────────────┘
                         ↓
                  ┌─────────────┐
                  │  transfers  │
                  └─────────────┘
```

---

## 6. Quy tắc đảm bảo tính nhất quán dữ liệu

Tất cả scraper và module xử lý dữ liệu phải tuân thủ các quy tắc sau:

1. Tên các cột phải **giống chính xác** với `DATA_DICTIONARY.md`.
2. Giá trị khóa chính phải duy nhất trong phạm vi được định nghĩa.
3. Giá trị khóa ngoại phải tham chiếu đến bản ghi tồn tại trong bảng tương ứng.
4. `player_id` phải luôn xác định cùng một cầu thủ trong toàn bộ project.
5. `team_id` phải luôn xác định cùng một đội bóng trong toàn bộ project.
6. `season` phải sử dụng cùng một định dạng trong tất cả dataset.
7. Tên `league` phải sử dụng cùng một quy ước trong tất cả dataset.
8. Các trường ngày tháng phải sử dụng cùng một định dạng.
9. Scraper **không được tự ý đổi tên hoặc xóa** các cột đã được quy định trong schema.
10. Các giá trị bị thiếu ở những trường không bắt buộc phải được biểu diễn thống nhất theo format dữ liệu đang sử dụng (`NULL`/`NaN`).

---

## 7. Tài liệu tham khảo

Chi tiết về từng cột, kiểu dữ liệu, trường bắt buộc và ý nghĩa của từng trường được trình bày trong:

