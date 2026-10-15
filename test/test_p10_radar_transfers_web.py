"""NGƯỜI 10 — radar, transfers, ước lượng giá trị, web."""
import math
from pathlib import Path

import pandas as pd
import pytest

from src.analysis.valuation import estimate_player_value
from src.common.io_utils import load_results, stat_columns
from src.scrapers.transfers.parsing import parse_money, parse_transfer_html
from src.scrapers.transfers.scraper import build_transfers
from src.visualization.radar import find_player, radar_chart, resolve_attribute
from src.web.app import _table


def test_parse_money():
    assert abs(parse_money("€45.2M") - 45.2) < 1e-9 and abs(parse_money("€800K") - 0.8) < 1e-9
    assert math.isnan(parse_money("Free")) and math.isnan(parse_money(None))


def test_parse_transfer_html_both_shapes():
    ev = "<table><tr><th>Player</th><th>Date</th><th>From</th><th>To</th><th>Fee</th></tr><tr><td>A B</td><td>2023-07-01</td><td>X</td><td>Y</td><td>€10M</td></tr></table>"
    r = parse_transfer_html(ev).iloc[0]
    assert r["Fee_M"] == 10 and r["From"] == "X" and r["To"] == "Y"
    lst = "<table><tr><th>Player</th><th>Team</th><th>Value</th></tr><tr><td>C D</td><td>Z</td><td>€2.5M</td></tr></table>"
    assert parse_transfer_html(lst).iloc[0]["To"] == "Z"


def test_build_transfers_drops_unknown_and_keeps_fk():
    players = pd.DataFrame({"player_id": ["a-b-eng"], "player_name": ["A B"], "team_id": ["y"]})
    teams = pd.DataFrame({"team_id": ["y"], "team_name": ["Y"]})
    raw = pd.DataFrame({"Player": ["A B", "Nobody"], "Date": ["2023-07-01"] * 2, "From": ["Foreign FC", "Y"],
                        "To": ["Y", "Y"], "Fee_M": [10.0, 5.0]})
    t = build_transfers(raw, players, teams)
    assert len(t) == 1 and pd.isna(t.loc[0, "from_team_id"]) and t.loc[0, "to_team_id"] == "y"


def test_radar_on_demo(demo_env, isolated_paths):
    df = load_results()
    attr = resolve_attribute("SCA90", stat_columns(df))
    assert attr == "SCA_SCA90"
    with pytest.raises(ValueError):
        resolve_attribute("Gls", stat_columns(df))           # mơ hồ (nhiều cột kết thúc _Gls)
    p1, p2 = df.iloc[0]["Player"], df.iloc[5]["Player"]
    out = radar_chart(p1, p2, ["Sh_Gls", "Sh_SoT", attr, "Tkl_Tkl"], df=df)
    assert Path(out).exists() and Path(out).stat().st_size > 5000
    assert find_player(df, p1.lower())["Player"] == p1


def test_transfers_and_valuation_on_demo(demo_env, isolated_paths):
    from src.pipeline.run_transfers import run_transfers
    t = run_transfers(source="local")
    assert len(t) > 100 and t["transfer_fee"].notna().sum() > 30
    est = estimate_player_value()
    assert not est.empty and (isolated_paths.final / "valuation_method.md").exists()


def test_web_table_renders_na():
    html = _table(pd.DataFrame({"a": [1.5, float("nan")]}))
    assert "N/a" in html and "<table>" in html
