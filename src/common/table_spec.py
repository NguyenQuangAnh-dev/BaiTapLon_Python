"""Mô tả một bảng FBref và ánh xạ cột FBref -> tên cột chuẩn của nhóm."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TableSpec:
    """key       : tên nội bộ (tên file trung gian)
    page      : đoạn URL của FBref (stats, shooting, passing, ...)
    table_id  : id thẻ <table>
    owner     : số thứ tự người phụ trách (1..10)
    columns   : list (nhóm_gốc, tên_thống_kê_gốc, tên_cột_chuẩn). nhóm = None -> lấy cột đầu tiên có tên đó.
    with_player: True nếu bảng theo cầu thủ (Player, Squad); False nếu bảng theo đội (chỉ Squad).
    levels    : số dòng tiêu đề của bảng (FBref: 2; bảng lịch thi đấu: 1)
    """
    key: str
    page: str
    table_id: str
    owner: int
    columns: list = field(default_factory=list)
    with_player: bool = True
    levels: int = 2
    anchor: Optional[str] = None            # cột dùng để nhận diện dòng dữ liệu thật (mặc định Player/Squad)
    text_cols: tuple = ()                   # tên cột chuẩn cần giữ dạng CHỮ (không ép sang số)

    @property
    def anchor_name(self) -> str:
        return self.anchor or ("Player" if self.with_player else "Squad")

    def full_columns(self) -> list:
        have = {c[2] for c in self.columns}
        base = []
        if self.anchor is None:
            base = ([(None, "Player", "Player")] if self.with_player else []) + [(None, "Squad", "Squad")]
        return [c for c in base if c[2] not in have] + list(self.columns)

    def out_columns(self) -> list[str]:
        return [c[2] for c in self.full_columns()]


def cols(group: Optional[str], prefix: str, *stats) -> list:
    """Tạo danh sách cột. stat có thể là 'xG' hoặc ('PrgDist', 'ProDist') = (tên gốc, tên chuẩn)."""
    out = []
    for s in stats:
        src, name = (s if isinstance(s, tuple) else (s, s))
        out.append((group, src, f"{prefix}_{name}" if prefix else name))
    return out
