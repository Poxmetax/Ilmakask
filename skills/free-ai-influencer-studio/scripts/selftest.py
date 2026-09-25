#!/usr/bin/env python3
"""Smoke-test every studio script on synthetic media in a temporary folder.

Usage:
    python selftest.py [--keep]

Needs ffmpeg/ffprobe on PATH and the reportlab package (pip install reportlab).
Prints one line per check and a JSON summary; exit 0 only if everything passed.
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(args, cwd, expect=0):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.returncode == expect, (r.stdout + r.stderr)[-600:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    results = {}
    if not shutil.which("ffmpeg"):
        print(json.dumps({"ok": False, "error": "ffmpeg not on PATH"}))
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="studio_selftest_"))
    P = "studio/test.persona"
    today = dt.date.today().isoformat()
    try:
        results["init"] = run([PY, HERE / "studio_init.py", "--name", "Test Persona", "--handle", "test.persona",
                               "--root", "studio"], tmp)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=24:duration=6",
                        "-f", "lavfi", "-i", "sine=frequency=220:duration=6", "-shortest", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "gen.mp4"], cwd=tmp, check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
                        "-ar", "48000", "voice.wav"], cwd=tmp, check=True)
        out = f"{P}/publish/queue/final.mp4"
        results["assemble"] = run([PY, HERE / "assemble_clip.py", "--video", "gen.mp4", "--voice", "voice.wav",
                                   "--out", out], tmp)
        results["qc_pass"] = run([PY, HERE / "qc_clip.py", out], tmp)
        results["qc_rejects_landscape"] = run([PY, HERE / "qc_clip.py", "gen.mp4"], tmp, expect=1)
        with (tmp / P / "ledger.csv").open("a", encoding="utf-8") as f:
            f.write(f"tool:tts,,tool,TTS,Apache-2.0,yes,no,https://example.com,{today},,\n")
            f.write(f"tool:vid,,tool,Video,free,no,yes,https://example.com,{today},,\n")
            # ledger file paths are relative to the project folder
            f.write(f"final,publish/queue/final.mp4,render,ffmpeg,local,yes,no,,{today},tool:tts;tool:vid,\n")
        led = (tmp / P / "ledger.csv").read_text(encoding="utf-8")
        results["gate_blocks_noncommercial"] = run([PY, HERE / "license_gate.py", "--project", P], tmp, expect=1)
        led = led.replace("tool:tts;tool:vid", "tool:tts")
        (tmp / P / "ledger.csv").write_text(led, encoding="utf-8")
        results["gate_passes_clean"] = run([PY, HERE / "license_gate.py", "--project", P, "--out", "gate.json"], tmp)
        (tmp / "cap.txt").write_text("Test caption. AI-generated character", encoding="utf-8")
        results["publish_dry_run"] = run([PY, HERE / "ig_publish.py", "--ig-user-id", "1", "--video", out,
                                          "--caption-file", "cap.txt", "--gate-report", "gate.json"], tmp)
        (tmp / "ideas.json").write_text(json.dumps([{"id": "a", "title": "A"}, {"id": "b", "title": "B"}]), encoding="utf-8")
        results["calendar"] = run([PY, HERE / "plan_calendar.py", "--ideas", "ideas.json", "--start", today,
                                   "--slots", "mon@18:00,thu@18:00", "--out", "cal.csv"], tmp)
        spec = HERE.parent / "assets" / "example_spec.json"
        try:
            import reportlab  # noqa: F401
            results["product_pdf"] = run([PY, HERE / "build_product_pdf.py", str(spec), "--out", "p.pdf"], tmp)
        except ImportError:
            results["product_pdf"] = (False, "reportlab not installed: pip install reportlab")
    finally:
        summary = {k: ("pass" if ok else "FAIL") for k, (ok, _) in results.items()}
        for k, (ok, log) in results.items():
            print(f"{'pass' if ok else 'FAIL'}  {k}")
            if not ok:
                print("      " + log.replace("\n", "\n      "))
        ok_all = all(ok for ok, _ in results.values())
        print(json.dumps({"ok": ok_all, "checks": summary, "workdir": str(tmp) if args.keep else "deleted"}, indent=2))
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
