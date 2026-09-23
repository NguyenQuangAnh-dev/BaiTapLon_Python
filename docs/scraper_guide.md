# Hướng dẫn xây dựng Scraper

## 1. Mục đích

Tài liệu này quy định cách xây dựng, tổ chức và bàn giao các scraper trong project:

**Football Data Analysis – Season 2024/2025**

Mục tiêu là đảm bảo scraper của các thành viên tạo ra dữ liệu có cùng cấu trúc và có thể tích hợp trực tiếp vào pipeline chung.

---

## 2. Tài liệu bắt buộc phải đọc

Trước khi bắt đầu code, mỗi thành viên phải đọc:

1. `docs/DATA_DICTIONARY.md`
2. `docs/SCHEMA.md`

Không tự ý thiết kế lại cấu trúc dữ liệu.

---

## 3. Nhiệm vụ của Scraper

Mỗi scraper có nhiệm vụ:

```text
Nguồn dữ liệu
     ↓
Thu thập dữ liệu
     ↓
Parse dữ liệu
     ↓
Chuẩn hóa dữ liệu
     ↓
Kiểm tra dữ liệu cơ bản
     ↓
Lưu dữ liệu
```

Scraper **không chịu trách nhiệm** cho các bước phân tích dữ liệu như:

* K-Means
* PCA
* Visualization
* Machine Learning
* Phân tích thống kê chuyên sâu

Các bước này thuộc các module phía sau của pipeline.

---

## 4. Quy tắc Schema

### 4.1. Không tự ý đổi tên cột

Tên cột phải khớp chính xác với `DATA_DICTIONARY.md`.

Ví dụ:

```text
ĐÚNG:
player_id
player_name
team_id

KHÔNG dùng:
playerId
player_name_full
id_player
team
```

---

### 4.2. Không tự ý thêm hoặc xóa cột

Nếu nguồn dữ liệu có thêm thông tin không nằm trong schema hiện tại:

```text
Không tự ý thêm vào dataset chính.
```

Nếu thông tin đó cần thiết cho project, báo cho người phụ trách Core/Schema để xem xét.

---

### 4.3. Kiểu dữ liệu

Dữ liệu phải được chuyển về đúng kiểu được quy định trong `DATA_DICTIONARY.md`.

Ví dụ:

```text
player_id      → string
player_name    → string
date_of_birth  → date
matches        → int
goals          → int
pass_accuracy  → float
```

Không để số nguyên hoặc số thực dưới dạng chuỗi nếu schema yêu cầu kiểu số.

---

## 5. Quy tắc ID

ID là thành phần quan trọng để liên kết các bảng.

### Player ID

Cùng một cầu thủ phải có cùng `player_id` trong:

```text
players
player_stats
transfers
```

### Team ID

Cùng một đội bóng phải có cùng `team_id` trong:

```text
teams
players
team_stats
matches
transfers
```

Không được tự tạo một ID khác cho cùng một player/team nếu ID đó đã tồn tại trong project.

---

## 6. Quy tắc Season

Season hiện tại của project:

```text
2024/2025
```

Tất cả scraper phải sử dụng cùng một format.

Ví dụ:

```text
ĐÚNG:
2024/2025

KHÔNG dùng:
2024-25
24/25
2024_2025
2025
```

---

## 7. Quy tắc League

Tên giải đấu phải sử dụng cùng một cách viết trong toàn project.

Ví dụ:

```text
Premier League
La Liga
Serie A
Bundesliga
Ligue 1
```

Không tự ý sử dụng nhiều cách viết khác nhau cho cùng một giải đấu.

---

## 8. Xử lý dữ liệu thiếu

Đối với các trường `Required = NO`:

Nếu nguồn không có dữ liệu:

```text
→ để giá trị thiếu
```

Không tự ý:

```text
0
Unknown
N/A
None
```

nếu việc thay thế đó làm thay đổi ý nghĩa dữ liệu.

Các quy tắc xử lý missing data cụ thể sẽ được thống nhất ở bước preprocessing.

---

## 9. Cấu trúc code

Mỗi scraper nên được tổ chức theo cấu trúc:

```text
src/
└── scrapers/
    ├── players/
    │   └── scraper.py
    │
    ├── teams/
    │   └── scraper.py
    │
    ├── player_stats/
    │   └── scraper.py
    │
    ├── team_stats/
    │   └── scraper.py
    │
    ├── matches/
    │   └── scraper.py
    │
    └── transfers/
        └── scraper.py
```

Tùy theo nguồn dữ liệu và cách phân công, cấu trúc có thể được mở rộng nhưng không được làm ảnh hưởng đến cấu trúc chung của project.

---

## 10. Output của Scraper

Scraper phải tạo ra dữ liệu có cấu trúc đúng với bảng tương ứng.

Ví dụ `players`:

```python
[
    "player_id",
    "player_name",
    "date_of_birth",
    "nationality",
    "position",
    "team_id"
]
```

Ví dụ `matches`:

```python
[
    "match_id",
    "date",
    "league",
    "season",
    "home_team_id",
    "away_team_id",
    "home_score",
    "away_score",
    "result"
]
```

---

## 11. Kiểm tra trước khi bàn giao

Trước khi tạo Pull Request, scraper phải kiểm tra tối thiểu:

### Schema

```text
[ ] Đúng tên cột
[ ] Đúng số lượng cột
[ ] Đúng kiểu dữ liệu
```

### ID

```text
[ ] ID không bị thiếu ở trường bắt buộc
[ ] ID không bị trùng ngoài phạm vi cho phép
[ ] ID có thể liên kết với các bảng khác
```

### Dữ liệu

```text
[ ] Không lấy nhầm mùa giải
[ ] Không lấy nhầm giải đấu
[ ] Không có dữ liệu rác rõ ràng
[ ] Không bị duplicate bất thường
```

### Output

```text
[ ] File output đúng vị trí
[ ] Tên file đúng quy ước
[ ] Có thể đọc lại bằng pandas
```

---

## 12. Raw Data và Processed Data

Không ghi đè dữ liệu raw.

Luồng dữ liệu:

```text
Source
  ↓
Raw Data
  ↓
Processing
  ↓
Processed Data
```

### Raw Data

Lưu dữ liệu gần với dữ liệu thu thập ban đầu nhất có thể.

### Processed Data

Lưu dữ liệu sau khi đã:

* chuẩn hóa tên cột
* chuẩn hóa kiểu dữ liệu
* xử lý format
* loại bỏ dữ liệu lỗi rõ ràng

---

## 13. Không commit dữ liệu quá lớn

Không commit các file dữ liệu quá lớn vào repository nếu chưa được thống nhất.

Đặc biệt không commit:

```text
cache
temporary files
debug files
browser data
large raw datasets
```

Các file lớn sẽ được xử lý theo quy định chung của project.

---

## 14. Git Workflow

Mỗi thành viên làm việc trên branch riêng.

Ví dụ:

```text
main
 │
 ├── scraper/player-stats
 ├── scraper/team-stats
 ├── scraper/matches
 └── scraper/transfers
```

Không push trực tiếp lên `main`.

Quy trình:

```text
main
 ↓
Tạo branch
 ↓
Code
 ↓
Test
 ↓
Commit
 ↓
Push
 ↓
Pull Request
 ↓
Review
 ↓
Merge
```

---

## 15. Commit Message

Sử dụng commit message ngắn gọn và rõ ràng.

Ví dụ:

```text
feat: add player scraper
feat: add match scraper
fix: handle missing player nationality
fix: remove duplicate matches
refactor: normalize team ids
```

---

## 16. Pull Request

Khi tạo Pull Request, cần ghi rõ:

### Công việc đã làm

```text
- Implement player scraper
- Normalize player IDs
- Add basic validation
```

### Dataset

```text
Table:
players
```

### Nguồn dữ liệu

Ghi rõ nguồn dữ liệu mà scraper sử dụng.

### Kiểm tra

```text
- [x] Schema validated
- [x] Duplicate checked
- [x] Missing values checked
- [x] Output tested
```

---

## 17. Nguyên tắc quan trọng

> **Scraper phải tuân thủ Schema, không được tự ý thay đổi Schema.**

Nếu gặp vấn đề như:

* nguồn không có một column bắt buộc
* nguồn sử dụng ID khác
* dữ liệu không khớp schema
* cần thêm column mới
* cần thay đổi kiểu dữ liệu

thì **không tự sửa schema**.

Hãy báo cho người phụ trách Core/Schema trước khi thay đổi.

---

## 18. Definition of Done

Một scraper được xem là hoàn thành khi:

```text
[ ] Thu thập đúng dữ liệu
[ ] Đúng mùa giải 2024/2025
[ ] Đúng giải đấu được phân công
[ ] Đúng schema
[ ] Đúng tên column
[ ] Đúng kiểu dữ liệu
[ ] ID nhất quán
[ ] Đã kiểm tra duplicate
[ ] Đã kiểm tra missing data
[ ] Có output hợp lệ
[ ] Code có thể chạy lại
[ ] Đã test
[ ] Đã tạo Pull Request
```

Sau khi đáp ứng các yêu cầu trên, scraper mới được xem xét để merge vào `main`.
