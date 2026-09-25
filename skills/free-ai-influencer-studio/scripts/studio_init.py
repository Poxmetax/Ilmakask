#!/usr/bin/env python3
"""Create the on-disk state for one AI influencer project.

Usage:
    python studio_init.py --name "Ilma Kask" --handle ilma.kask [--root ./studio] [--force]

Creates studio/<handle>/ with influencer.json, ledger.csv, calendar.csv and the
working folders. Never overwrites existing files unless --force is given.
Prints a JSON report.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

LEDGER_FIELDS = [
    "asset_id", "file", "stage", "tool", "plan", "commercial_ok", "watermark",
    "terms_url", "verified_on", "derived_from", "notes",
]
CALENDAR_FIELDS = [
    "date", "time", "timezone", "platform", "format", "series", "idea_id",
    "title", "status", "pack_path", "post_url",
]
FOLDERS = [
    "identity/golden", "identity/sheets", "voice", "world/plates", "world/scouting",
    "content/ideas", "content/scripts", "production/stills", "production/clips",
    "production/audio", "production/renders", "publish/queue", "publish/posted",
    "product", "analytics",
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", text.lower()).strip("-") or "persona"


def bible(name: str, handle: str) -> dict:
    today = dt.date.today().isoformat()
    return {
        "schema": 1,
        "created": today,
        "persona": {
            "name": name, "handle": handle, "age": None, "niche": None,
            "niche_sentence": None, "backstory": None, "voice_style": None,
            "catchphrase": None, "audience_language": None, "home_region": None,
            "disclosure_line": "AI-generated character · real places",
        },
        "identity": {
            "anchor_image": None, "golden_set": [], "anchors": [],
            "anchor_paragraph": None, "sheet_images": [], "locked": False,
        },
        "voice": {
            "tool": None, "model": None, "voice_id": None, "settings": {},
            "seed_line": None, "pronunciations": {}, "locked": False,
        },
        "world": {"locations": []},
        "stack": {"hardware_tier": None, "tools": {}},
        "product": {"title": None, "format": None, "price": None, "platform": None,
                    "spec_path": "product/spec.json", "sample_approved": False},
        "publishing": {"tier": 0, "ig_user_id": None, "token_expires": None,
                       "cadence": None},
        "gates": {"G1_identity": False, "G2_voice_world": False,
                  "G3_product_sample": False, "G4_first_nine_posts": 0},
        "mode": "guided",
        "phase": 0,
        "learnings": [],
        "sources": [],
    }


def write_csv(path: Path, fields, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(fields)
    return "created"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--handle", required=True)
    ap.add_argument("--root", default="./studio")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    base = Path(args.root) / slugify(args.handle)
    report = {"project": str(base), "files": {}, "folders": []}
    for rel in FOLDERS:
        p = base / rel
        p.mkdir(parents=True, exist_ok=True)
        report["folders"].append(rel)

    bpath = base / "influencer.json"
    if bpath.exists() and not args.force:
        report["files"]["influencer.json"] = "kept"
    else:
        bpath.write_text(json.dumps(bible(args.name, args.handle), indent=2, ensure_ascii=False), encoding="utf-8")
        report["files"]["influencer.json"] = "created"

    report["files"]["ledger.csv"] = write_csv(base / "ledger.csv", LEDGER_FIELDS, args.force)
    report["files"]["calendar.csv"] = write_csv(base / "calendar.csv", CALENDAR_FIELDS, args.force)

    readme = base / "README.md"
    if not readme.exists() or args.force:
        readme.write_text(
            f"# {args.name} studio\n\n"
            "- influencer.json: the bible. Read at session start, update at session end.\n"
            "- ledger.csv: one row per tool and per asset. commercial_ok must be yes, watermark no,\n"
            "  verified_on recent, and derived_from lists upstream asset_ids (separated by ;).\n"
            "- publish/queue: one folder per post; run license_gate.py before publishing.\n",
            encoding="utf-8")
        report["files"]["README.md"] = "created"
    else:
        report["files"]["README.md"] = "kept"

    report["ok"] = True
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
