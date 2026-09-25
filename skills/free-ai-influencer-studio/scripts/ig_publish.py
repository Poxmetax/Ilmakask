#!/usr/bin/env python3
"""Publish a local MP4 as an Instagram Reel through the Graph API resumable upload.
No public server is needed. Dry run by default.

Usage:
    export IG_ACCESS_TOKEN=...            # never pass the token on the command line
    python ig_publish.py --ig-user-id 1784... --video pack/video.mp4 --caption-file pack/caption.txt \
        --gate-report gate.json [--thumb-offset-ms 1500] [--api-version v25.0] [--live]

Steps (Meta Instagram Platform docs, content publishing + resumable uploads):
  1. GET  /{ig-user-id}/content_publishing_limit?fields=config,quota_usage
  2. POST /{ig-user-id}/media  media_type=REELS, upload_type=resumable, caption, share_to_feed
  3. POST https://rupload.facebook.com/ig-api-upload/{version}/{container-id}  (file bytes)
  4. GET  /{container-id}?fields=status_code  until FINISHED or ERROR
  5. POST /{ig-user-id}/media_publish  creation_id={container-id}
Requires an app using Facebook Login for Business with the content publishing permission.
Refuses --live unless the license gate report exists and says ok.
Check the current API version in Meta's changelog before first use.
Prints a JSON report; exit 0 on success (or a clean dry run).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

GRAPH = "https://graph.facebook.com"
RUPLOAD = "https://rupload.facebook.com/ig-api-upload"


def fail(msg, **extra):
    print(json.dumps({"ok": False, "error": msg, **extra}, indent=2))
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ig-user-id", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--caption-file", required=True)
    ap.add_argument("--gate-report", help="JSON written by license_gate.py --out")
    ap.add_argument("--thumb-offset-ms", type=int)
    ap.add_argument("--api-version", default="v25.0")
    ap.add_argument("--timeout-s", type=int, default=600)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.is_file():
        return fail(f"video not found: {video}")
    caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    if len(caption) > 2200:
        return fail(f"caption is {len(caption)} characters; Instagram's limit is 2200")
    size = video.stat().st_size

    gate_ok, gate_note = False, "no gate report given"
    if args.gate_report:
        try:
            gate = json.loads(Path(args.gate_report).read_text(encoding="utf-8"))
            files = [f.get("file", "") for f in gate.get("files", [])]
            gate_ok = bool(gate.get("ok")) and any(Path(f).name == video.name for f in files)
            gate_note = "pass" if gate_ok else "gate failed or this video is not in the report"
        except Exception as e:
            gate_note = f"could not read gate report: {e}"

    plan = {
        "ig_user_id": args.ig_user_id, "video": str(video), "bytes": size,
        "caption_chars": len(caption), "api_version": args.api_version,
        "license_gate": gate_note,
        "steps": ["read publishing quota", "create resumable REELS container",
                  "upload bytes to rupload.facebook.com", "poll status_code", "media_publish"],
    }
    if not args.live:
        print(json.dumps({"ok": True, "mode": "dry-run", "plan": plan,
                          "note": "add --live to publish; the license gate must pass"}, indent=2))
        return 0
    if not gate_ok:
        return fail("refusing to publish: license gate did not pass for this file", plan=plan)

    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token:
        return fail("IG_ACCESS_TOKEN is not set")
    try:
        import requests
    except ImportError:
        return fail("the requests package is required: pip install requests")

    v = args.api_version
    s = requests.Session()
    auth = {"Authorization": f"Bearer {token}"}
    report = {"ok": False, "mode": "live", "plan": plan}

    r = s.get(f"{GRAPH}/{v}/{args.ig_user_id}/content_publishing_limit",
              params={"fields": "config,quota_usage"}, headers=auth, timeout=30)
    report["quota"] = r.json() if r.ok else {"http": r.status_code, "body": r.text[:500]}
    try:
        data = r.json().get("data", [{}])[0]
        used = int(data.get("quota_usage", 0))
        total = int(data.get("config", {}).get("quota_total", 0) or 0)
        if total and used >= total:
            report["error"] = f"publishing quota exhausted ({used}/{total}); try after the 24 h window"
            print(json.dumps(report, indent=2))
            return 1
    except Exception:
        pass

    params = {"media_type": "REELS", "upload_type": "resumable", "caption": caption, "share_to_feed": "true"}
    if args.thumb_offset_ms is not None:
        params["thumb_offset"] = str(args.thumb_offset_ms)
    r = s.post(f"{GRAPH}/{v}/{args.ig_user_id}/media", data=params, headers=auth, timeout=60)
    if not r.ok:
        report["error"] = f"container creation failed: {r.status_code} {r.text[:500]}"
        print(json.dumps(report, indent=2))
        return 1
    cid = r.json()["id"]
    report["container_id"] = cid

    with video.open("rb") as fh:
        r = s.post(f"{RUPLOAD}/{v}/{cid}",
                   headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
                   data=fh, timeout=600)
    if not r.ok:
        report["error"] = f"upload failed: {r.status_code} {r.text[:500]}"
        print(json.dumps(report, indent=2))
        return 1

    deadline = time.time() + args.timeout_s
    status = None
    while time.time() < deadline:
        r = s.get(f"{GRAPH}/{v}/{cid}", params={"fields": "status_code,status"}, headers=auth, timeout=30)
        status = r.json().get("status_code") if r.ok else None
        if status in ("FINISHED", "ERROR", "EXPIRED"):
            break
        time.sleep(8)
    report["status_code"] = status
    if status != "FINISHED":
        report["error"] = "container did not finish processing; create a new container rather than retrying this one"
        print(json.dumps(report, indent=2))
        return 1

    r = s.post(f"{GRAPH}/{v}/{args.ig_user_id}/media_publish", data={"creation_id": cid}, headers=auth, timeout=60)
    if not r.ok:
        report["error"] = f"publish failed: {r.status_code} {r.text[:500]}"
        print(json.dumps(report, indent=2))
        return 1
    report["ok"] = True
    report["media_id"] = r.json().get("id")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
