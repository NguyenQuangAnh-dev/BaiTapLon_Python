"""NGƯỜI 10 — Web dashboard (chỉ dùng thư viện chuẩn Python, không cần cài thêm)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from config import settings
from config.settings import NA
from src.common.io_utils import load_results
from src.common.logging_utils import log
from src.common.paths import PATHS
from src.preprocessing.cleaning import player_key
from src.visualization.radar import radar_chart


_CSS = ("body{font-family:system-ui,Arial;margin:24px;max-width:1100px}table{border-collapse:collapse;font-size:14px}"
        "td,th{border:1px solid #ccc;padding:4px 8px}th{background:#f2f2f2}nav a{margin-right:14px}"
        "img{max-width:100%}input,select{padding:4px;margin:2px}pre{background:#f6f6f6;padding:10px;white-space:pre-wrap}")


def _page(title: str, body: str) -> bytes:
    import html as H
    nav = ("<nav><a href='/'>Cầu thủ</a><a href='/stats'>Thống kê đội</a>"
           "<a href='/clusters'>K-means/PCA</a><a href='/radar'>Radar</a></nav><hr>")
    return (f"<!doctype html><meta charset='utf-8'><title>{H.escape(title)}</title><style>{_CSS}</style>"
            f"<h2>BTL Python — {H.escape(title)} (mùa {settings.SEASON})</h2>{nav}{body}").encode("utf-8")


def _table(df: pd.DataFrame, links: Optional[Callable] = None) -> str:
    import html as H
    head = "".join(f"<th>{H.escape(str(c))}</th>" for c in df.columns)
    rows = []
    for i, r in df.iterrows():
        cells = []
        for c in df.columns:
            v = r[c]
            txt = NA if pd.isna(v) else (f"{v:.3g}" if isinstance(v, float) else str(v))
            txt = H.escape(txt)
            cells.append(f"<td>{links(c, i, txt) if links else txt}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><tr>{head}</tr>{''.join(rows)}</table>"


def serve_web(host: str = "127.0.0.1", port: int = 8000) -> None:
    import html as H
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, quote, urlparse
    df = load_results()
    default_attrs = [c for c in ("Perf_G-PK", "Perf_Ast", "Exp_xG", "SCA_SCA90", "Tkl_Tkl", "Carry_Carries") if c in df.columns]

    def read_txt(p: Path) -> str:
        return H.escape(p.read_text(encoding="utf-8")) if p.exists() else "(chưa có — hãy chạy bước tương ứng)"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):   # im lặng
            pass

        def send(self, body: bytes, ctype="text/html; charset=utf-8", code=200):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            try:
                if u.path == "/":
                    sub = df
                    if q.get("q"):
                        sub = sub[sub["Player"].map(player_key).str.contains(re.escape(player_key(q["q"])), na=False)]
                    if q.get("team"):
                        sub = sub[sub["Squad"] == q["team"]]
                    teams = "".join(f"<option{' selected' if q.get('team') == t else ''}>{H.escape(t)}</option>"
                                    for t in [""] + sorted(df["Squad"].dropna().unique()))
                    show = sub[[c for c in ("Player", "Squad", "Pos", "Age", "Min", "Perf_G-PK", "Perf_Ast") if c in sub]].head(200)
                    tbl = _table(show, lambda c, i, t: f"<a href='/player?i={i}'>{t}</a>" if c == "Player" else t)
                    body = (f"<form>Tên: <input name='q' value='{H.escape(q.get('q', ''))}'> Đội: <select name='team'>{teams}</select>"
                            f"<button>Tìm</button></form><p>{len(sub)} cầu thủ (hiển thị tối đa 200)</p>{tbl}")
                    self.send(_page("Cầu thủ", body))
                elif u.path == "/player":
                    r = df.iloc[int(q["i"])]
                    info = pd.DataFrame({"Thống kê": r.index, "Giá trị": r.values})
                    self.send(_page(str(r["Player"]), f"<p>{H.escape(str(r['Squad']))} — {H.escape(str(r['Pos']))}</p>"
                                    f"<a href='/radar?p1={quote(str(r['Player']))}'>So sánh bằng radar</a>" + _table(info)))
                elif u.path == "/stats":
                    rk = PATHS.final / "team_ranking.csv"
                    body = f"<pre>{read_txt(PATHS.final / 'team_analysis.txt')}</pre>"
                    if rk.exists():
                        body += "<h3>Xếp hạng phong độ</h3>" + _table(pd.read_csv(rk, na_values=[NA], keep_default_na=False))
                    bt = PATHS.final / "best_team_per_stat.csv"
                    if bt.exists():
                        body += "<h3>Đội tốt nhất cho từng thống kê</h3>" + _table(pd.read_csv(bt))
                    self.send(_page("Thống kê đội", body))
                elif u.path == "/clusters":
                    img = "<img src='/plots/pca_clusters.png'>" if (PATHS.plots / "pca_clusters.png").exists() else ""
                    self.send(_page("K-means / PCA", img + f"<pre>{read_txt(PATHS.final / 'cluster_report.txt')}</pre>"))
                elif u.path == "/radar":
                    p1, p2 = q.get("p1", ""), q.get("p2", "")
                    attrs = q.get("attrs") or ",".join(default_attrs)
                    form = (f"<form>Cầu thủ 1: <input name='p1' value='{H.escape(p1)}'> Cầu thủ 2: <input name='p2' value='{H.escape(p2)}'>"
                            f"<br>Thuộc tính (dấu phẩy): <input name='attrs' size='70' value='{H.escape(attrs)}'><button>Vẽ</button></form>")
                    img = (f"<img src='/radar.png?p1={quote(p1)}&p2={quote(p2)}&attrs={quote(attrs)}'>" if p1 and p2 else "")
                    self.send(_page("Radar", form + img))
                elif u.path == "/radar.png":
                    path = radar_chart(q["p1"], q["p2"], [a for a in q["attrs"].split(",") if a.strip()], df=df)
                    self.send(path.read_bytes(), "image/png")
                elif u.path.startswith("/plots/"):
                    f = (PATHS.plots / u.path[len("/plots/"):]).resolve()
                    if PATHS.plots.resolve() not in f.parents or not f.is_file():
                        self.send(b"Not found", "text/plain", 404)
                    else:
                        self.send(f.read_bytes(), "image/png")
                else:
                    self.send(b"Not found", "text/plain", 404)
            except Exception as exc:                       # hiển thị lỗi thân thiện thay vì sập server
                self.send(_page("Lỗi", f"<pre>{H.escape(str(exc))}</pre>"), code=400)

    srv = ThreadingHTTPServer((host, port), Handler)
    log(f"Web dashboard: http://{host}:{port}   (Ctrl+C để dừng)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log("Đã dừng web.")
