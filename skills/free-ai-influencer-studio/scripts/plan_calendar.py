#!/usr/bin/env python3
"""Turn chosen ideas into calendar rows.

Usage:
    python plan_calendar.py --ideas ideas.json --start 2026-10-05 \
        --slots "mon@18:00,wed@18:00,fri@12:30" --tz Europe/Tallinn \
        [--pin "Dark Season=tue@08:30"] [--platform instagram] --out calendar.csv [--append]

ideas.json: a list of {"id": "...", "title": "...", "format": "reel|carousel|story",
            "series": "optional series name", "repeat": optional int (series episodes)}
Rules: pinned series get their own weekday slot every week; everything else fills the
regular slots in list order; a series with "repeat": N is scheduled N times.
Output columns match studio calendar.csv. Prints a JSON summary.
"""
import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
FIELDS = ["date", "time", "timezone", "platform", "format", "series", "idea_id",
          "title", "status", "pack_path", "post_url"]


def parse_slot(s: str):
    day, _, tm = s.strip().lower().partition("@")
    if day not in DAYS or not tm:
        raise ValueError(f"bad slot '{s}', expected like mon@18:00")
    dt.time.fromisoformat(tm)
    return DAYS[day], tm


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--slots", required=True)
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--pin", action="append", default=[], help='"Series name=day@HH:MM"')
    ap.add_argument("--platform", default="instagram")
    ap.add_argument("--out", required=True)
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()

    ideas = json.loads(Path(args.ideas).read_text(encoding="utf-8"))
    slots = sorted(parse_slot(s) for s in args.slots.split(",") if s.strip())
    pins = {}
    for p in args.pin:
        name, _, slot = p.partition("=")
        pins[name.strip()] = parse_slot(slot)

    pinned_queue = {name: [] for name in pins}
    regular = []
    for idea in ideas:
        n = int(idea.get("repeat", 1) or 1)
        for k in range(n):
            item = dict(idea)
            if n > 1:
                item["title"] = f"{idea['title']} #{k + 1}"
            s = idea.get("series")
            (pinned_queue[s] if s in pins else regular).append(item)

    start = dt.date.fromisoformat(args.start)
    rows, day = [], start
    guard = 0
    while (regular or any(pinned_queue.values())) and guard < 3660:
        wd = day.weekday()
        for name, (pday, ptime) in pins.items():
            if wd == pday and pinned_queue[name]:
                it = pinned_queue[name].pop(0)
                rows.append([day.isoformat(), ptime, args.tz, args.platform, it.get("format", "reel"),
                             name, it.get("id", ""), it["title"], "planned", "", ""])
        for sday, stime in slots:
            if wd == sday and regular:
                it = regular.pop(0)
                rows.append([day.isoformat(), stime, args.tz, args.platform, it.get("format", "reel"),
                             it.get("series", ""), it.get("id", ""), it["title"], "planned", "", ""])
        day += dt.timedelta(days=1)
        guard += 1

    out = Path(args.out)
    mode = "a" if args.append and out.exists() else "w"
    with out.open(mode, newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if mode == "w":
            w.writerow(FIELDS)
        w.writerows(rows)
    print(json.dumps({"ok": True, "rows": len(rows), "first": rows[0][:2] if rows else None,
                      "last": rows[-1][:2] if rows else None, "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
