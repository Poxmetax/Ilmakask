#!/usr/bin/env python3
"""Automated technical QC for a vertical social clip.

Usage:
    python qc_clip.py clip.mp4 [--min-dur 3] [--max-dur 90] [--lufs -14] [--lufs-tol 2]

Checks: container/codecs (H.264 or HEVC video, AAC audio), 9:16 geometry within 1%,
at least 1080 px wide (warning below), 24+ fps, duration range, audio present,
integrated loudness near target, true peak below -1 dBTP, black segments,
frozen segments (a common generation stall), and silent start longer than 1 s.
Human checks (identity, lips, hands, shadows, crowd faces) are listed in
references/prompts.md section 9 and are NOT replaced by this script.
Prints a JSON report; exit 0 if no failures (warnings allowed), 1 otherwise.
"""
import argparse
import json
import re
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def fraction(s: str) -> float:
    try:
        a, b = s.split("/")
        return float(a) / float(b) if float(b) else 0.0
    except Exception:
        try:
            return float(s)
        except Exception:
            return 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--min-dur", type=float, default=3.0)
    ap.add_argument("--max-dur", type=float, default=90.0)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--lufs-tol", type=float, default=2.0)
    args = ap.parse_args()

    fails, warns, info = [], [], {}
    p = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", args.clip])
    if p.returncode != 0:
        print(json.dumps({"ok": False, "fails": ["ffprobe could not read the file"], "stderr": p.stderr[-500:]}))
        return 1
    meta = json.loads(p.stdout)
    vs = [s for s in meta["streams"] if s.get("codec_type") == "video"]
    aus = [s for s in meta["streams"] if s.get("codec_type") == "audio"]
    dur = float(meta["format"].get("duration", 0) or 0)
    info["duration_s"] = round(dur, 3)

    if not vs:
        fails.append("no video stream")
    else:
        v = vs[0]
        w, h = int(v["width"]), int(v["height"])
        fps = fraction(v.get("avg_frame_rate") or v.get("r_frame_rate") or "0")
        info.update(width=w, height=h, fps=round(fps, 3), vcodec=v.get("codec_name"), pix_fmt=v.get("pix_fmt"))
        if v.get("codec_name") not in ("h264", "hevc"):
            fails.append(f"video codec {v.get('codec_name')} (use h264 or hevc)")
        if abs((w / h) - (9 / 16)) > 0.01 * (9 / 16):
            fails.append(f"aspect {w}x{h} is not 9:16")
        if w < 1080:
            warns.append(f"width {w} px is below 1080; platform will upscale")
        if fps < 24:
            fails.append(f"frame rate {fps:.2f} below 24")
        if v.get("pix_fmt") not in ("yuv420p", "yuvj420p"):
            warns.append(f"pixel format {v.get('pix_fmt')}; yuv420p is safest")

    if not (args.min_dur <= dur <= args.max_dur):
        fails.append(f"duration {dur:.2f}s outside {args.min_dur}-{args.max_dur}s")

    if not aus:
        fails.append("no audio stream")
    else:
        info["acodec"] = aus[0].get("codec_name")
        if aus[0].get("codec_name") != "aac":
            warns.append(f"audio codec {aus[0].get('codec_name')}; AAC is safest")
        r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", args.clip, "-map", "0:a:0",
                 "-af", "ebur128=peak=true", "-f", "null", "-"])
        txt = r.stderr
        m_i = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", txt)
        m_tp = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", txt)
        if m_i:
            lufs = float(m_i[-1]) if m_i[-1] != "-inf" else float("-inf")
            info["integrated_lufs"] = lufs
            if lufs == float("-inf"):
                fails.append("audio is completely silent")
            elif abs(lufs - args.lufs) > args.lufs_tol:
                warns.append(f"loudness {lufs} LUFS (target {args.lufs} ±{args.lufs_tol}); run assemble_clip.py")
        if m_tp and m_tp[-1] != "-inf":
            tp = float(m_tp[-1])
            info["true_peak_dbtp"] = tp
            if tp > -1.0:
                warns.append(f"true peak {tp} dBTP above -1; risk of clipping after platform encode")
        s = run(["ffmpeg", "-hide_banner", "-nostats", "-i", args.clip, "-map", "0:a:0",
                 "-af", "silencedetect=n=-45dB:d=1", "-f", "null", "-"]).stderr
        starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", s)]
        if starts and starts[0] <= 0.05:
            warns.append("audio is silent for more than 1 s at the start; hook should land immediately")

    if vs:
        b = run(["ffmpeg", "-hide_banner", "-nostats", "-i", args.clip, "-map", "0:v:0",
                 "-vf", "blackdetect=d=0.3:pix_th=0.10,freezedetect=n=0.003:d=1.0",
                 "-f", "null", "-"]).stderr
        blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", b)
        freezes = re.findall(r"freeze_start: ([\d.]+)", b)
        if blacks:
            info["black_segments"] = [(float(a), float(c)) for a, c in blacks]
            fails.append(f"{len(blacks)} black segment(s) of 0.3 s or more")
        if freezes:
            info["freeze_starts"] = [float(x) for x in freezes]
            warns.append(f"{len(freezes)} frozen segment(s) of 1 s or more; check for a generation stall")

    report = {"ok": not fails, "clip": args.clip, "info": info, "fails": fails, "warnings": warns,
              "human_checks": "see references/prompts.md section 9"}
    print(json.dumps(report, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
