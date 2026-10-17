"""Dữ liệu GIẢ LẬP (ngẫu nhiên) chỉ để chạy thử/kiểm thử pipeline.

CẢNH BÁO: tên đội, tên cầu thủ, số liệu đều do máy tạo. KHÔNG dùng làm kết quả nộp.
"""
from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

from config import settings
from config.settings import RANDOM_STATE
from src.common.paths import PATHS
from src.common.table_spec import TableSpec


_FIRST = ["Alex", "Ben", "Carlos", "Daniel", "Ethan", "Felix", "Gabriel", "Hugo", "Ivan", "Jack",
          "Kevin", "Liam", "Marco", "Noah", "Oscar", "Pablo", "Quinn", "Rafael", "Samuel", "Tom",
          "Victor", "William", "Xavier", "Yusuf", "Zack", "Adam", "Bruno", "Cesar", "David", "Eric"]


_LAST = ["Anderson", "Brown", "Clark", "Davies", "Evans", "Foster", "Green", "Hughes", "Jones",
         "Kelly", "Lewis", "Morgan", "Nelson", "Owen", "Parker", "Reed", "Smith", "Taylor",
         "Walker", "Young", "Silva", "Costa", "Rossi", "Muller", "Dubois", "Kovac", "Nielsen",
         "Santos", "Moreno", "Ibrahim", "Okafor", "Tanaka", "Haddad", "Petrov", "Larsen", "Ortiz"]


_TEAMS = ["Ashford", "Brookvale", "Crestmoor", "Dunmere", "Eastbrook", "Fairhaven", "Glenwick",
          "Harrowgate", "Ironbridge", "Kingsmere", "Lakeshire", "Millbrook", "Northvale", "Oakhurst",
          "Pinecrest", "Queensford", "Redcliffe", "Stonebridge", "Thornbury", "Westmere"]


_NATIONS = ["ENG", "ENG", "ENG", "FRA", "ESP", "BRA", "POR", "NED", "GER", "ARG", "SCO", "IRL", "NGA", "SEN"]


_ATTACK_PREFIX = {"Perf", "Exp", "P90", "Sh", "ShExp", "SCA", "SCAType", "GCA", "GCAType"}


_DEFEND_PREFIX = {"Tkl", "Chall", "Blk", "Aerial"}


_POS_MULT = {  # (tấn công, phòng ngự, kiểm soát)
    "GK": (0.03, 0.05, 0.25), "DF": (0.4, 1.8, 1.0), "MF": (1.0, 1.0, 1.4), "FW": (2.0, 0.5, 0.8)}


def demo_players(n_teams: int = 20, per_team: int = 24, seed: int = RANDOM_STATE) -> list[dict]:
    rng = np.random.default_rng(seed)
    pattern = ["GK"] * 3 + ["DF"] * 8 + ["MF"] * 8 + ["FW"] * 5
    players, used = [], set()
    for t in range(n_teams):
        team = f"{_TEAMS[t % len(_TEAMS)]} Town"
        strength = float(rng.normal(1.0, 0.18))
        for i in range(per_team):
            base = pattern[i % len(pattern)]
            while True:
                name = f"{rng.choice(_FIRST)} {rng.choice(_LAST)}"
                if (name, team) not in used:
                    used.add((name, team))
                    break
            if base == "GK":
                minutes = int(rng.integers(3000, 3421)) if i % 3 == 0 else int(rng.integers(0, 120))
            else:
                minutes = int(rng.integers(0, 91)) if rng.random() < 0.1 else int(3420 * rng.beta(1.4, 1.6))
            pos = base if base == "GK" or rng.random() > 0.2 else {"DF": "DF,MF", "MF": "MF,FW", "FW": "FW,MF"}[base]
            players.append({"Player": name, "Squad": team, "Pos": pos, "base": base,
                            "Nation": f"{str(rng.choice(_NATIONS)).lower()} {rng.choice(_NATIONS)}",
                            "Age": int(rng.integers(18, 37)), "Min": minutes,
                            "ab": strength * float(rng.lognormal(0, 0.35))})
    return players


def _demo_value(p: dict, name: str, blank_rate: float) -> str:
    """Sinh 1 ô dữ liệu giả lập theo kiểu dữ liệu của FBref."""
    rng = np.random.default_rng(zlib.crc32(f"{p['Player']}|{p['Squad']}|{name}".encode()))
    if name == "Player":
        return p["Player"]
    if name == "Squad":
        return p["Squad"]
    if name == "Nation":
        return p["Nation"]
    if name == "Pos":
        return p["Pos"]
    if name == "Age":
        return f"{p['Age']}-{int(rng.integers(0, 365))}"
    n90 = max(p["Min"], 1) / 90
    if name == "Min":
        return f"{p['Min']:,}"
    if name == "MP":
        return str(max(1, min(38, int(round(p["Min"] / 75)))))
    if name in ("Starts", "Start_Starts"):
        return str(max(0, min(38, int(round(p["Min"] / 90)))))
    if blank_rate and rng.random() < blank_rate:
        return ""
    prefix, _, stat = name.partition("_")
    if not stat:
        prefix, stat = "", name
    if "%" in stat:
        return f"{float(np.clip(rng.normal(55 + 12 * (p['ab'] - 1), 14), 0, 100)):.1f}"
    if stat.startswith("Mn/"):
        return f"{float(np.clip(rng.normal(72, 14), 1, 95)):.0f}"
    if stat == "PPM":
        return f"{float(np.clip(rng.normal(1.5 * p['ab'], 0.35), 0, 3)):.2f}"
    if prefix == "Sh" and stat == "Dist":
        return f"{float(np.clip(rng.normal(17, 4), 5, 35)):.1f}"
    a, d, c = _POS_MULT[p["base"]]
    mult = a if prefix in _ATTACK_PREFIX else d if prefix in _DEFEND_PREFIX else c
    if prefix.startswith("GK"):
        mult = 1.0
    r0 = 0.05 + (zlib.crc32(stat.encode()) % 1000) / 1000 * 1.5
    rate = r0 * mult * p["ab"] * float(rng.lognormal(0, 0.3))
    per90 = stat.endswith("90") or prefix == "P90"
    value = rate if per90 else rate * n90
    if "Dist" in stat:
        value *= 25
    if stat in ("PK", "PKatt", "PKA", "PKsv", "PKm"):
        value *= 0.08                      # phạt đền hiếm hơn nhiều
    if per90 or stat.startswith(("x", "npx")) or "xG" in stat or "xA" in stat:
        return f"{value:.2f}"
    return str(int(round(value)))


def make_fake_html(spec: TableSpec, players: list[dict], blank_rate: float = 0.0,
                   wrap_comment: bool = False) -> str:
    """Tạo HTML giống FBref (2 dòng tiêu đề, dòng tiêu đề lặp, chuỗi '1,234', tuổi '24-123')."""
    fc = spec.full_columns()
    head1 = "<th></th>" + "".join(f"<th>{g or ''}</th>" for g, _, _ in fc) + "<th></th>"
    head2 = "<th>Rk</th>" + "".join(f"<th>{s}</th>" for _, s, _ in fc) + "<th>Matches</th>"
    body = []
    rows = [p for p in players if not (spec.key == "goalkeeper" and p["base"] != "GK")]
    for i, p in enumerate(rows, 1):
        tds = "".join(f"<td>{_demo_value(p, n, blank_rate)}</td>" for _, _, n in fc)
        body.append(f"<tr><th>{i}</th>{tds}<td>Matches</td></tr>")
        if i == len(rows) // 2:                      # dòng tiêu đề lặp giữa bảng như FBref
            body.append(f"<tr class='thead'>{head2}</tr>")
    html = (f"<table id='{spec.table_id}'><thead><tr>{head1}</tr><tr>{head2}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody></table>")
    return f"<div><!--{html}--></div>" if wrap_comment else f"<div>{html}</div>"


# ---------------------------------------------------------------------------------------
# Bảng cấp ĐỘI, lịch thi đấu và chuyển nhượng giả lập
# ---------------------------------------------------------------------------------------
def _wrap(html: str, comment: bool) -> str:
    return f"<div><!--{html}--></div>" if comment else f"<div>{html}</div>"


def make_fake_squad_html(table_id: str, squads: list[str], stats: list[tuple[str, str]], seed: int,
                         comment: bool = False) -> str:
    """Bảng theo đội kiểu FBref. stats = [(nhóm, tên cột)]; cột đầu luôn là Squad."""
    rng = np.random.default_rng(seed)
    head1 = "<th></th>" + "".join(f"<th>{g}</th>" for g, _ in stats)
    head2 = "<th>Squad</th>" + "".join(f"<th>{s}</th>" for _, s in stats)
    rows = []
    for sq in squads:
        cells = ""
        for _, s_ in stats:
            if s_ == "Poss":
                cells += f"<td>{rng.uniform(38, 62):.1f}</td>"
            elif s_ == "Sh":
                cells += f"<td>{int(rng.integers(380, 620))}</td>"
            else:
                cells += f"<td>{int(rng.integers(130, 230))}</td>"
        rows.append(f"<tr><th>{sq}</th>{cells}</tr>")
    html = (f"<table id='{table_id}'><thead><tr>{head1}</tr><tr>{head2}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")
    return _wrap(html, comment)


def make_fake_schedule_html(teams: list[str], seed: int = RANDOM_STATE) -> str:
    """380 trận (vòng tròn 2 lượt) + dòng ngăn cách trống + dòng tiêu đề lặp, giống FBref."""
    rng = np.random.default_rng(seed)
    n = len(teams)
    arr = list(range(n))
    rounds = []
    for r in range(n - 1):                                    # phương pháp vòng tròn
        pairs = [(arr[i], arr[n - 1 - i]) for i in range(n // 2)]
        rounds.append(pairs if r % 2 == 0 else [(b, a) for a, b in pairs])
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    rounds += [[(b, a) for a, b in rd] for rd in rounds]       # lượt về
    head = "<tr><th>Wk</th><th>Day</th><th>Date</th><th>Time</th><th>Home</th><th>xG</th><th>Score</th><th>xG</th><th>Away</th><th>Attendance</th></tr>"
    body = []
    start = pd.Timestamp("2024-08-16")
    for wk, rd in enumerate(rounds, 1):
        date = (start + pd.Timedelta(days=7 * (wk - 1))).strftime("%Y-%m-%d")
        for h, a in rd:
            hs, as_ = int(rng.poisson(1.5)), int(rng.poisson(1.2))
            body.append(f"<tr><th>{wk}</th><td>Sat</td><td>{date}</td><td>15:00</td><td>{teams[h]}</td><td>1.4</td>"
                        f"<td>{hs}–{as_}</td><td>1.1</td><td>{teams[a]}</td><td>40,000</td></tr>")
        body.append("<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>")
        if wk % 10 == 0:
            body.append(f"<tr class='thead'>{head.replace('<th>Wk', '<th>Wk')}</tr>")
    return (f"<table id='sched_{settings.season_slug()}_{settings.FBREF_COMP_ID}_1'><thead>{head}</thead>"
            f"<tbody>{''.join(body)}</tbody></table>")


def demo_fee(p: dict, rng) -> float:
    """Phí chuyển nhượng giả lập phụ thuộc năng lực, số phút, tuổi (để mô hình có thứ để học)."""
    lv = 1.0 + 1.5 * np.log(max(p["ab"], 0.2)) + 0.8 * p["Min"] / 3420 - 0.05 * abs(p["Age"] - 26) + rng.normal(0, 0.35)
    return float(np.clip(np.exp(lv), 0.5, 120))


def make_fake_transfers_html(players: list[dict], seed: int = RANDOM_STATE, n: int = 160) -> str:
    rng = np.random.default_rng(seed + 7)
    pool = [p for p in players if p["Min"] > 200]
    teams = sorted({p["Squad"] for p in players})
    idx = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
    rows = []
    for i in idx:
        p = pool[i]
        frm = rng.choice([t for t in teams if t != p["Squad"]]) if rng.random() < 0.6 else "Foreign FC"
        date = (pd.Timestamp("2023-06-15") + pd.Timedelta(days=int(rng.integers(0, 200)))).strftime("%Y-%m-%d")
        r = rng.random()
        fee = "Free" if r < 0.1 else "Loan" if r < 0.15 else f"€{demo_fee(p, rng):.1f}M"
        rows.append(f"<tr><td>{p['Player']}</td><td>{date}</td><td>{frm}</td><td>{p['Squad']}</td><td>{fee}</td></tr>")
    return ("<table id='transfers'><thead><tr><th>Player</th><th>Date</th><th>From</th><th>To</th><th>Fee</th></tr>"
            f"</thead><tbody>{''.join(rows)}</tbody></table>")


def make_demo_raw(specs: list, blank_rate: float = 0.01) -> None:
    """Ghi các file HTML giả lập vào data/raw (dùng với --source local)."""
    PATHS.raw.mkdir(parents=True, exist_ok=True)
    players = demo_players()
    squads = sorted({p["Squad"] for p in players})
    extra = {
        "stats": make_fake_squad_html("stats_squads_standard_for", squads, [("", "Poss")], 11, comment=True),
        "shooting": make_fake_squad_html("stats_squads_shooting_for", squads,
                                         [("Standard", "Sh"), ("Standard", "SoT")], 12),
    }
    for i, spec in enumerate(specs):
        html = make_fake_html(spec, players, blank_rate=blank_rate, wrap_comment=(i % 2 == 1))
        (PATHS.raw / f"{spec.page}.html").write_text(html + extra.get(spec.page, ""), encoding="utf-8")
    (PATHS.raw / "schedule.html").write_text(make_fake_schedule_html(squads), encoding="utf-8")
    (PATHS.raw / "transfers_page_1.html").write_text(make_fake_transfers_html(players), encoding="utf-8")
