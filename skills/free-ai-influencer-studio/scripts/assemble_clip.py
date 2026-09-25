#!/usr/bin/env python3
"""Assemble a publish-ready vertical clip with ffmpeg.

Usage:
    python assemble_clip.py --video gen.mp4 [--voice line.wav] [--ambience room.wav]
        [--srt captions.srt] [--video-audio keep|duck|drop] [--voice-delay 0.3]
        [--tail 0.8] [--lufs -14] --out final.mp4

What it does:
  - scales to cover 1080x1920 and centre-crops (no letterbox bars), 30 fps, H.264 High, yuv420p
  - mixes: generated-video audio (kept, ducked to -18 dB, or dropped) + voice + optional ambience
  - trims to voice end + tail when a voice track is given (never longer than the video)
  - normalises loudness to the target integrated LUFS (default -14) with a -1.5 dBTP ceiling
  - burns captions from an SRT if given (needs ffmpeg built with libass)
  - adds a silent audio track if the result would otherwise have none
Prints a JSON report; exit 0 on success.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def duration(info: dict) -> float:
    try:
        return float(info["format"]["duration"])
    except Exception:
        return max((float(s.get("duration", 0) or 0) for s in info.get("streams", [])), default=0.0)


def has_audio(info: dict) -> bool:
    return any(s.get("codec_type") == "audio" for s in info.get("streams", []))


def srt_filter_path(p: str) -> str:
    # escape for the ffmpeg filtergraph (colons, backslashes, quotes)
    return str(Path(p).resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--ambience")
    ap.add_argument("--srt")
    ap.add_argument("--video-audio", choices=["keep", "duck", "drop"])
    ap.add_argument("--voice-delay", type=float, default=0.3)
    ap.add_argument("--tail", type=float, default=0.8)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(json.dumps({"ok": False, "error": "ffmpeg/ffprobe not found on PATH"}))
        return 2

    vinfo = probe(args.video)
    vdur = duration(vinfo)
    video_audio = args.video_audio or ("duck" if args.voice else "keep")
    if not has_audio(vinfo):
        video_audio = "drop"

    inputs = ["-i", args.video]
    idx = 1
    voice_idx = amb_idx = None
    target = vdur
    if args.voice:
        inputs += ["-i", args.voice]
        voice_idx = idx
        idx += 1
        vo_dur = duration(probe(args.voice))
        target = min(vdur, args.voice_delay + vo_dur + args.tail)
    if args.ambience:
        inputs += ["-stream_loop", "-1", "-i", args.ambience]
        amb_idx = idx
        idx += 1

    W, H = args.width, args.height
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={args.fps},setsar=1")
    if args.srt:
        style = ("FontName=DejaVu Sans,FontSize=13,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H80000000,BorderStyle=1,Outline=2,Shadow=0,"
                 "Alignment=2,MarginV=75")
        vf += f",subtitles='{srt_filter_path(args.srt)}':force_style='{style}'"
    vf += "[vout]"

    parts, labels = [], []
    if video_audio in ("keep", "duck"):
        gain = "-18dB" if video_audio == "duck" else "0dB"
        parts.append(f"[0:a]aresample=48000,volume={gain}[a0]")
        labels.append("[a0]")
    if voice_idx is not None:
        ms = int(args.voice_delay * 1000)
        parts.append(f"[{voice_idx}:a]aresample=48000,adelay={ms}:all=1[vo]")
        labels.append("[vo]")
    if amb_idx is not None:
        parts.append(f"[{amb_idx}:a]aresample=48000,volume=-20dB[amb]")
        labels.append("[amb]")
    if not labels:
        parts.append("anullsrc=r=48000:cl=stereo[a0]")
        labels.append("[a0]")

    mix = (f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,"
           if len(labels) > 1 else f"{labels[0]}")
    loud = f"loudnorm=I={args.lufs}:TP=-1.5:LRA=11,aresample=48000[aout]"
    afilter = (mix + loud) if len(labels) > 1 else f"{labels[0]}{loud}"
    graph = ";".join([vf] + parts + [afilter])

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
           "-t", f"{target:.3f}",
           "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", args.out]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(json.dumps({"ok": False, "error": res.stderr.strip()[-2000:], "cmd": cmd}, indent=2))
        return 1

    oinfo = probe(args.out)
    v = next(s for s in oinfo["streams"] if s["codec_type"] == "video")
    print(json.dumps({
        "ok": True, "out": args.out, "duration_s": round(duration(oinfo), 3),
        "size": f"{v['width']}x{v['height']}", "video_audio": video_audio,
        "voice": bool(args.voice), "ambience": bool(args.ambience), "captions": bool(args.srt),
        "target_lufs": args.lufs,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
