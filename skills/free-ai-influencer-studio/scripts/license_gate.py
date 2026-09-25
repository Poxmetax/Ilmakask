#!/usr/bin/env python3
"""License gate: block publishing of anything with a non-commercial, watermarked,
unknown or untraceable source.

Usage:
    python license_gate.py --project studio/ilma.kask [--queue publish/queue] [--max-tool-age 45] [--out gate.json]

Ledger rules (ledger.csv in the project):
  - Every media file under the queue must match a ledger row by its `file` path
    (relative to the project) or, failing that, by file name.
  - Each row lists upstream asset_ids in `derived_from` (separated by ';').
    Tool rows (stage == 'tool') describe a tool/plan; asset rows point to them.
  - Every row in a file's lineage must have commercial_ok == yes and watermark == no.
  - Tool rows must have verified_on within --max-tool-age days (terms change).
  - Asset rows must have a verified_on date (the terms that applied when made).
Exit code 0 = pass, 1 = fail, 2 = usage error. Prints and optionally writes a JSON report.
"""
import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

MEDIA = {".mp4", ".mov", ".m4v", ".webm", ".jpg", ".jpeg", ".png", ".webp",
         ".wav", ".mp3", ".m4a", ".aac", ".flac", ".pdf"}


def parse_date(s: str):
    try:
        return dt.date.fromisoformat(s.strip())
    except Exception:
        return None


def load_ledger(path: Path):
    rows = {}
    by_file = {}
    by_name = {}
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            aid = (r.get("asset_id") or "").strip()
            if not aid:
                continue
            rows[aid] = r
            fp = (r.get("file") or "").strip()
            if fp:
                by_file[Path(fp).as_posix()] = aid
                by_name.setdefault(Path(fp).name, []).append(aid)
    return rows, by_file, by_name


def check_row(r: dict, today: dt.date, max_age: int):
    problems = []
    if (r.get("commercial_ok") or "").strip().lower() != "yes":
        problems.append(f"commercial_ok is '{r.get('commercial_ok') or 'blank'}' (must be yes)")
    if (r.get("watermark") or "").strip().lower() != "no":
        problems.append(f"watermark is '{r.get('watermark') or 'blank'}' (must be no)")
    d = parse_date(r.get("verified_on") or "")
    if d is None:
        problems.append("verified_on missing or not YYYY-MM-DD")
    elif (r.get("stage") or "").strip().lower() == "tool" and (today - d).days > max_age:
        problems.append(f"tool terms verified {(today - d).days} days ago (max {max_age}); re-verify")
    return problems


def lineage(aid: str, rows: dict, seen=None):
    seen = set() if seen is None else seen
    if aid in seen:
        return seen
    seen.add(aid)
    r = rows.get(aid)
    if r:
        for up in (r.get("derived_from") or "").split(";"):
            up = up.strip()
            if up:
                lineage(up, rows, seen)
    return seen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--queue", default="publish/queue")
    ap.add_argument("--max-tool-age", type=int, default=45)
    ap.add_argument("--out")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = ap.parse_args()

    proj = Path(args.project)
    ledger = proj / "ledger.csv"
    queue = proj / args.queue
    if not ledger.exists() or not queue.exists():
        print(json.dumps({"ok": False, "error": "ledger.csv or queue folder not found",
                          "ledger": str(ledger), "queue": str(queue)}))
        return 2

    today = parse_date(args.today) if args.today else dt.date.today()
    rows, by_file, by_name = load_ledger(ledger)
    report = {"ok": True, "checked_on": today.isoformat(), "files": []}

    media = sorted(p for p in queue.rglob("*") if p.is_file() and p.suffix.lower() in MEDIA)
    if not media:
        report["note"] = "no media files in queue"
    for p in media:
        rel = p.relative_to(proj).as_posix()
        entry = {"file": rel, "ok": True, "problems": []}
        aid = by_file.get(rel)
        if aid is None:
            cands = by_name.get(p.name, [])
            if len(cands) == 1:
                aid = cands[0]
            elif len(cands) > 1:
                entry["problems"].append(f"ambiguous: {len(cands)} ledger rows share the name {p.name}; use full paths")
        if aid is None and not entry["problems"]:
            entry["problems"].append("untracked: no ledger row for this file")
        if aid:
            entry["asset_id"] = aid
            chain = lineage(aid, rows)
            entry["lineage"] = sorted(chain)
            for node in sorted(chain):
                r = rows.get(node)
                if r is None:
                    entry["problems"].append(f"{node}: referenced in derived_from but missing from ledger")
                    continue
                for prob in check_row(r, today, args.max_tool_age):
                    entry["problems"].append(f"{node} ({r.get('tool') or '?'}): {prob}")
        if entry["problems"]:
            entry["ok"] = False
            report["ok"] = False
        report["files"].append(entry)

    out = json.dumps(report, indent=2, ensure_ascii=False)
    print(out)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
