#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: seetop.py
Version: 1.1.0
Objective: Ncurses live dashboard for SeeVar — orchestrator state, weather
           consensus, catalog statistics, tonight's plan, and interleaved
           log tail. Two-column layout. Refreshes every 10 seconds.
           Press q to quit.
"""

import curses
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SEEVAR_ROOT   = Path(__file__).resolve().parent
DATA_DIR      = SEEVAR_ROOT / "data"
CATALOG_DIR   = SEEVAR_ROOT / "catalogs"
LOG_DIR       = SEEVAR_ROOT / "logs"

STATE_FILE    = DATA_DIR    / "system_state.json"
WEATHER_FILE  = DATA_DIR    / "weather_state.json"
PLAN_FILE     = DATA_DIR    / "tonights_plan.json"
VSX_FILE      = DATA_DIR    / "vsx_catalog.json"
CAMPAIGN_FILE = CATALOG_DIR / "campaign_targets.json"
FED_FILE      = CATALOG_DIR / "federation_catalog.json"
CHARTS_DIR    = CATALOG_DIR / "reference_stars"

LOG_FILES = [
    LOG_DIR / "orchestrator.log",
    LOG_DIR / "weather.log",
    LOG_DIR / "dashboard.log",
]

REFRESH_S  = 10
LOG_LINES  = 10
VERSION    = "1.1.0"

# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict | list:
    try:
        raw = json.loads(path.read_text())
        return raw
    except Exception:
        return {}


def read_orchestrator() -> dict:
    s = _read_json(STATE_FILE)
    if not isinstance(s, dict) or not s or s == {}:
        return {"empty": True}
    return {
        "empty":   False,
        "state":   s.get("state",   "UNKNOWN"),
        "sub":     s.get("sub",     ""),
        "msg":     s.get("msg",     ""),
        "updated": s.get("updated", ""),
    }


def read_weather() -> dict:
    w = _read_json(WEATHER_FILE)
    if not isinstance(w, dict) or not w or w == {}:
        return {"empty": True}
    return {
        "empty":        False,
        "status":       w.get("status",               "UNKNOWN"),
        "imaging_go":   w.get("imaging_go",           None),
        "win_start":    w.get("imaging_window_start",  None),
        "win_end":      w.get("imaging_window_end",    None),
        "clear_hours":  w.get("clear_hours",           0),
        "abort_hours":  w.get("abort_hours",           0),
        "clouds_pct":   w.get("clouds_pct",            0),
        "humidity_pct": w.get("humidity_pct",          0),
        "knmi_oktas":   w.get("knmi_oktas",            None),
        "dark_start":   w.get("dark_start",            "?"),
        "dark_end":     w.get("dark_end",              "?"),
        "last_update":  w.get("last_update",           None),
    }


def read_plan() -> dict:
    p = _read_json(PLAN_FILE)
    targets = p if isinstance(p, list) else p.get("targets", [])
    if not targets:
        return {"empty": True, "total": 0, "next": "—"}
    return {
        "empty": False,
        "total": len(targets),
        "next":  targets[0].get("name", "—"),
    }


def read_catalog_stats() -> dict:
    # Campaign targets
    c = _read_json(CAMPAIGN_FILE)
    campaign_list = c if isinstance(c, list) else c.get("targets", [])
    campaign_total = len(campaign_list)

    # VSX enriched
    v = _read_json(VSX_FILE)
    vsx_stars = v.get("stars", {}) if isinstance(v, dict) else {}
    vsx_enriched = len(vsx_stars)
    vsx_pending  = max(0, campaign_total - vsx_enriched)

    # Comparison charts (reference_stars/*.json)
    charts = 0
    if CHARTS_DIR.exists():
        charts = len(list(CHARTS_DIR.glob("*.json")))

    # Federation catalog
    f = _read_json(FED_FILE)
    fed_list = f if isinstance(f, list) else f.get("targets", [])
    fed_total = len(fed_list)

    # Tonight's plan (reuse plan file for deferred count)
    p = _read_json(PLAN_FILE)
    plan_list = p if isinstance(p, list) else p.get("targets", [])
    tonight   = len(plan_list)
    deferred  = max(0, fed_total - tonight)

    return {
        "campaign":  campaign_total,
        "vsx":       vsx_enriched,
        "vsx_pend":  vsx_pending,
        "charts":    charts,
        "fed":       fed_total,
        "tonight":   tonight,
        "deferred":  deferred,
    }


def read_log_tail(n: int) -> list:
    lines = deque(maxlen=n * len(LOG_FILES))
    for lf in LOG_FILES:
        if not lf.exists():
            continue
        try:
            with open(lf, "r") as f:
                for line in f:
                    line = line.rstrip()
                    if line:
                        lines.append((lf.stem, line))
        except OSError:
            continue
    return list(lines)[-n:]


# ---------------------------------------------------------------------------
# Colour pairs
# ---------------------------------------------------------------------------
C_TITLE  = 1
C_GOOD   = 2
C_WARN   = 3
C_ABORT  = 4
C_DIM    = 5
C_BORDER = 6
C_STATE  = 7


def init_colours():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_TITLE,  curses.COLOR_CYAN,    -1)
    curses.init_pair(C_GOOD,   curses.COLOR_GREEN,   -1)
    curses.init_pair(C_WARN,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_ABORT,  curses.COLOR_RED,     -1)
    curses.init_pair(C_DIM,    curses.COLOR_WHITE,   -1)
    curses.init_pair(C_BORDER, curses.COLOR_BLUE,    -1)
    curses.init_pair(C_STATE,  curses.COLOR_MAGENTA, -1)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def safe_addstr(win, y, x, text, attr=0):
    max_y, max_x = win.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x >= max_x:
        return
    max_len = max_x - x - 1
    if max_len <= 0:
        return
    try:
        win.addstr(y, x, str(text)[:max_len], attr)
    except curses.error:
        pass


def draw_border(win, title: str):
    try:
        win.box()
    except curses.error:
        pass
    safe_addstr(win, 0, 2, f" {title} ",
                curses.color_pair(C_TITLE) | curses.A_BOLD)


def waiting(win, row: int = 1):
    safe_addstr(win, row, 2, "waiting for data...",
                curses.color_pair(C_DIM) | curses.A_DIM)


def state_colour(state: str) -> int:
    s = state.upper()
    if s == "FLIGHT":     return curses.color_pair(C_GOOD)  | curses.A_BOLD
    if s == "PREFLIGHT":  return curses.color_pair(C_WARN)  | curses.A_BOLD
    if s == "POSTFLIGHT": return curses.color_pair(C_WARN)
    if s == "PARKED":     return curses.color_pair(C_ABORT) | curses.A_BOLD
    return curses.color_pair(C_DIM)


def weather_colour(status: str, imaging_go) -> int:
    if imaging_go is False:
        return curses.color_pair(C_ABORT) | curses.A_BOLD
    s = status.upper()
    if s == "CLEAR":                    return curses.color_pair(C_GOOD) | curses.A_BOLD
    if s in ("CLOUDY", "HAZY", "HUMID"): return curses.color_pair(C_WARN)
    return curses.color_pair(C_DIM)


def log_colour(source: str) -> int:
    if "orchestrator" in source: return curses.color_pair(C_GOOD)
    if "weather"      in source: return curses.color_pair(C_WARN)
    return curses.color_pair(C_DIM)


# ---------------------------------------------------------------------------
# Panel drawers
# ---------------------------------------------------------------------------

def draw_header(stdscr, cols: int):
    now   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = "seetop — SeeVar Observatory"
    safe_addstr(stdscr, 0, 0, "─" * cols, curses.color_pair(C_BORDER))
    safe_addstr(stdscr, 0, 2, f" {title} ",
                curses.color_pair(C_TITLE) | curses.A_BOLD)
    safe_addstr(stdscr, 0, cols - len(now) - 3, f" {now} ",
                curses.color_pair(C_DIM))


def draw_orchestrator(win, data: dict):
    draw_border(win, "Orchestrator")
    if data.get("empty"):
        waiting(win)
        return
    state = data["state"]
    safe_addstr(win, 1, 2, "State  : ", curses.color_pair(C_DIM))
    safe_addstr(win, 1, 11, f"{state:<12}", state_colour(state))
    if data["sub"]:
        safe_addstr(win, 1, 24, f"({data['sub']})", curses.color_pair(C_DIM))
    safe_addstr(win, 2, 2,  "Message: ", curses.color_pair(C_DIM))
    safe_addstr(win, 2, 11, data["msg"],  curses.color_pair(C_DIM))
    if data["updated"]:
        safe_addstr(win, 3, 2, f"Updated: {data['updated']}",
                    curses.color_pair(C_DIM) | curses.A_DIM)


def draw_weather(win, data: dict):
    draw_border(win, "Weather")
    if data.get("empty"):
        waiting(win)
        safe_addstr(win, 2, 2, "run: .venv/bin/python3 core/preflight/weather.py",
                    curses.color_pair(C_DIM) | curses.A_DIM)
        return

    status     = data["status"]
    imaging_go = data["imaging_go"]
    go_str  = "GO  ✓" if imaging_go else "NO-GO ✗" if imaging_go is False else "?"
    go_attr = (curses.color_pair(C_GOOD)  | curses.A_BOLD) if imaging_go \
         else (curses.color_pair(C_ABORT) | curses.A_BOLD) if imaging_go is False \
         else curses.color_pair(C_DIM)

    safe_addstr(win, 1, 2,  "Status : ", curses.color_pair(C_DIM))
    safe_addstr(win, 1, 11, f"{status:<10}", weather_colour(status, imaging_go))
    safe_addstr(win, 1, 22, "Imaging: ", curses.color_pair(C_DIM))
    safe_addstr(win, 1, 31, go_str, go_attr)

    safe_addstr(win, 2, 2,  "Dark   : ", curses.color_pair(C_DIM))
    safe_addstr(win, 2, 11,
                f"{data['dark_start']} → {data['dark_end']}",
                curses.color_pair(C_DIM))

    if data["win_start"] and data["win_end"]:
        safe_addstr(win, 3, 2,  "Window : ", curses.color_pair(C_DIM))
        safe_addstr(win, 3, 11,
                    f"{data['win_start']} → {data['win_end']}  "
                    f"({data['clear_hours']}h clear / {data['abort_hours']}h abort)",
                    curses.color_pair(C_GOOD))
    else:
        safe_addstr(win, 3, 2, "Window : no clear window tonight",
                    curses.color_pair(C_ABORT))

    oktas = f"{data['knmi_oktas']:.0f}" if data["knmi_oktas"] is not None else "?"
    safe_addstr(win, 4, 2,
                f"Clouds : {data['clouds_pct']}%  "
                f"Humidity: {data['humidity_pct']}%  "
                f"KNMI: {oktas}/9 oktas",
                curses.color_pair(C_DIM) | curses.A_DIM)

    if data["last_update"]:
        age = int(time.time() - data["last_update"])
        safe_addstr(win, 5, 2, f"Updated: {age}s ago",
                    curses.color_pair(C_DIM) | curses.A_DIM)


def draw_catalog(win, data: dict):
    draw_border(win, "Catalog")

    def stat_row(row, label, val, total=None, warn_zero=False):
        safe_addstr(win, row, 2, f"{label:<18}", curses.color_pair(C_DIM))
        if total is not None:
            pct  = int(val / total * 100) if total > 0 else 0
            attr = curses.color_pair(C_GOOD) if pct >= 80 \
                   else curses.color_pair(C_WARN) if pct >= 40 \
                   else curses.color_pair(C_ABORT)
            safe_addstr(win, row, 20, f"{val:>4} / {total:<4} ({pct:>3}%)", attr)
        else:
            attr = curses.color_pair(C_ABORT) if (warn_zero and val == 0) \
                   else curses.color_pair(C_GOOD) if val > 0 \
                   else curses.color_pair(C_DIM)
            safe_addstr(win, row, 20, str(val), attr)

    stat_row(1, "Campaign targets",  data["campaign"])
    stat_row(2, "VSX enriched",      data["vsx"],      data["campaign"])
    stat_row(3, "Comp charts",       data["charts"],   data["campaign"])
    stat_row(4, "Federation catalog",data["fed"])
    stat_row(5, "Tonight's plan",    data["tonight"],  warn_zero=True)
    stat_row(6, "Cadence deferred",  data["deferred"])


def draw_plan(win, data: dict):
    draw_border(win, "Tonight's Plan")
    if data.get("empty") or data["total"] == 0:
        waiting(win)
        return
    attr = curses.color_pair(C_GOOD) | curses.A_BOLD
    safe_addstr(win, 1, 2,  "Targets: ", curses.color_pair(C_DIM))
    safe_addstr(win, 1, 11, str(data["total"]), attr)
    safe_addstr(win, 2, 2,  "Next   : ", curses.color_pair(C_DIM))
    safe_addstr(win, 2, 11, data["next"],
                curses.color_pair(C_WARN) | curses.A_BOLD)


def draw_log_tail(win, lines: list):
    draw_border(win, "Log Tail — orchestrator / weather / dashboard")
    max_y, max_x = win.getmaxyx()
    if not lines:
        waiting(win)
        return
    row = 1
    for source, line in lines:
        if row >= max_y - 1:
            break
        tag  = f"[{source[:4]}] "
        safe_addstr(win, row, 2, tag, log_colour(source))
        safe_addstr(win, row, 2 + len(tag), line, curses.color_pair(C_DIM))
        row += 1


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
# Row 0          : header
# Rows 1–5       : LEFT col — Orchestrator (5 rows)  |  RIGHT col — Catalog (8 rows)
# Rows 6–12      : LEFT col — Weather (7 rows)        |  RIGHT col — Plan (4 rows)
# Rows 13–end-1  : Log tail full width
# Row end        : footer

ORCH_H   = 5
WX_H     = 7
CAT_H    = 8
PLAN_H   = 4
TOP_H    = max(ORCH_H + WX_H, CAT_H + PLAN_H)   # 12
LOG_TOP  = 1 + TOP_H                              # 13


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)
    init_colours()

    last_refresh = 0.0

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break

        now = time.monotonic()
        if now - last_refresh < REFRESH_S:
            continue
        last_refresh = now

        stdscr.erase()
        rows, cols = stdscr.getmaxyx()

        if rows < 28 or cols < 80:
            safe_addstr(stdscr, 0, 0,
                        "Terminal too small — need 80×28 minimum.",
                        curses.A_BOLD)
            stdscr.refresh()
            continue

        # Data
        orch    = read_orchestrator()
        weather = read_weather()
        catalog = read_catalog_stats()
        plan    = read_plan()
        logs    = read_log_tail(LOG_LINES)

        left_w  = cols // 2
        right_w = cols - left_w

        draw_header(stdscr, cols)

        try:
            # Left column — Orchestrator
            orch_win = curses.newwin(ORCH_H, left_w, 1, 0)
            draw_orchestrator(orch_win, orch)
            orch_win.refresh()

            # Left column — Weather
            wx_win = curses.newwin(WX_H, left_w, 1 + ORCH_H, 0)
            draw_weather(wx_win, weather)
            wx_win.refresh()

            # Right column — Catalog
            cat_win = curses.newwin(CAT_H, right_w, 1, left_w)
            draw_catalog(cat_win, catalog)
            cat_win.refresh()

            # Right column — Plan
            plan_win = curses.newwin(PLAN_H, right_w, 1 + CAT_H, left_w)
            draw_plan(plan_win, plan)
            plan_win.refresh()

            # Log tail — full width
            log_h = max(4, rows - LOG_TOP - 1)
            log_win = curses.newwin(log_h, cols, LOG_TOP, 0)
            draw_log_tail(log_win, logs)
            log_win.refresh()

        except curses.error:
            pass

        # Footer
        footer = f" [q] quit  |  refresh: {REFRESH_S}s  |  seetop v{VERSION} "
        safe_addstr(stdscr, rows - 1, 0, "─" * cols,
                    curses.color_pair(C_BORDER))
        safe_addstr(stdscr, rows - 1, 2, footer,
                    curses.color_pair(C_DIM) | curses.A_DIM)

        stdscr.refresh()


def run():
    curses.wrapper(main)


if __name__ == "__main__":
    run()
