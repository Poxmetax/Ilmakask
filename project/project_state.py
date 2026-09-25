#!/usr/bin/env python3
"""Project passport helper: read, brief, time and log changes to the shared project file.

Usage (run from the repo root):
  python project/project_state.py show [--app melius|elevenlabs|metricool|stan|github] [--last 10]
  python project/project_state.py brief --app melius|elevenlabs      # paste-ready brief for an agent without file access
  python project/project_state.py beats --clip 8 [--duration-ms 6557] # phrase timings + clip length for a talking clip
  python project/project_state.py beats --text "Line..." --duration-ms 6200
  python project/project_state.py set clips.8.status "APPROVED"       # dot path; list items by id, JSON values allowed
  python project/project_state.py log --agent Claude --app melius --task "..." --changed "a" --changed "b" [--next "..."] [--credits 0] [--result ok]
  python project/project_state.py log --from-json entry.json          # paste a HANDOFF ENTRY from Mel/ElevenLabs
  python project/project_state.py validate

Standard library only. Every write bumps the patch version and updated_at, and appends to the changelog.
"""
import argparse, datetime as dt, json, math, pathlib, re, sys

DEFAULT = pathlib.Path(__file__).with_name("ilma_kask.project.json")
FORBIDDEN = [
    (re.compile(r"Signature=|X-Amz-Signature|Key-Pair-Id"), "signed media URL"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\b(sk|xi|mel)[-_][A-Za-z0-9]{16,}"), "API key-like string"),
]
REQUIRED = ["_protocol", "version", "project", "identity", "voice", "timing", "physics", "lighting",
            "quality_lock", "locations", "clips", "apps", "budget", "open_tasks", "changelog"]


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def save(path, data):
    problems = validate(data)
    if problems:
        sys.exit("refusing to save:\n- " + "\n- ".join(problems))
    pathlib.Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat(timespec="seconds")


def bump(data, agent):
    major, minor, patch = (int(x) for x in data["version"].split("."))
    data["version"] = f"{major}.{minor}.{patch + 1}"
    data["updated_at"] = now()
    data["updated_by"] = agent


def validate(data):
    out = [f"missing section: {k}" for k in REQUIRED if k not in data]
    ids = [c.get("id") for c in data.get("clips", [])]
    if len(ids) != len(set(ids)):
        out.append("duplicate clip ids")
    text = json.dumps(data, ensure_ascii=False)
    for rx, what in FORBIDDEN:
        if rx.search(text):
            out.append(f"contains a {what}; the repo is public, remove it")
    for i, e in enumerate(data.get("changelog", [])):
        for k in ("when", "agent", "app", "task", "changed"):
            if k not in e:
                out.append(f"changelog[{i}] missing '{k}'")
    return out


def resolve(data, dotted):
    """Walk a dot path; list segments match an item's 'id' (e.g. clips.8) or an index."""
    cur, parts = data, dotted.split(".")
    for p in parts[:-1]:
        cur = _step(cur, p)
    return cur, parts[-1]


def _step(cur, p):
    if isinstance(cur, list):
        for item in cur:
            if isinstance(item, dict) and str(item.get("id")) == p:
                return item
        return cur[int(p)]
    return cur[p]


PAUSES = {".": 0.30, "?": 0.30, "!": 0.30, ":": 0.22, ";": 0.20, ",": 0.14}


def syllables(word):
    """Rough English syllable count (vowel groups, silent final e)."""
    w = re.sub(r"[^a-z0-9]", "", word.lower())
    if not w:
        return 0
    if w.isdigit():
        return 2
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    if w.endswith(("es", "ed")) and n > 1 and not w.endswith(("ted", "ded", "ses", "ces", "zes", "ges")):
        n -= 1
    return max(1, n)


def beats(text, duration_ms, lead=0.20, trail=0.12):
    """Estimate phrase start/end inside a VO take: ~0.2 s lead-in, punctuation pauses, speech spread by syllables.
    Accuracy is about +-0.3 s; the video model follows the audio itself, the breakdown only keeps gestures and the
    closed-mouth tail in step with it. Returns rows, clip length (s) and tail (s)."""
    D = duration_ms / 1000
    phrases = [p.strip() for p in re.split(r"(?<=[.?!:;,])\s+", text) if p.strip()]
    pauses = [PAUSES.get(p[-1], 0.0) for p in phrases]
    pauses[-1] = 0.0
    syl = [sum(syllables(w) for w in p.split()) for p in phrases]
    per = max(0.05, (D - lead - trail - sum(pauses)) / max(1, sum(syl)))
    t, rows = lead, []
    for p, s_, pa in zip(phrases, syl, pauses):
        rows.append((round(t, 2), round(t + s_ * per, 2), p))
        t += s_ * per + pa
    clip = max(3, min(15, math.ceil(D + 0.4)))
    return rows, clip, round(clip - D, 2)


def cmd_show(a, data):
    print(f"{data['project']['name']}  v{data['version']}  updated {data['updated_at']} by {data['updated_by']}\n")
    print("PROTOCOL (start):"); [print("  -", s) for s in data["_protocol"]["at_task_start"]]
    print("PROTOCOL (end):"); [print("  -", s) for s in data["_protocol"]["at_task_end"]]
    print("\nOPEN TASKS:")
    for t in data["open_tasks"]:
        print(f"  {t['id']}: {t['what']}" + (f"  [{t.get('credits')} cr]" if t.get("credits") else "") + (f"  blocked by: {t['blocked_by']}" if t.get("blocked_by") else ""))
    print("\nCLIPS:")
    for c in data["clips"]:
        print(f"  {c['id']}  {c['date']}  {c['place_id']:<18} {c['status']}")
    print(f"\nLAST {a.last} CHANGES:")
    for e in data["changelog"][-a.last:]:
        print(f"  {e['when']}  {e['agent']}@{e['app']}: {e['task']}  -> {e.get('result','')}")
    if a.app:
        print(f"\nAPP SECTION: {a.app}")
        print(json.dumps(data["apps"].get(a.app, {}), indent=2, ensure_ascii=False))


def cmd_brief(a, data):
    if a.app == "elevenlabs":
        v = data["voice"]
        print("ELEVENLABS BRIEF, Ilma Kask (read fully before generating)\n")
        print(f"Voice: {v['recipe']['voice_name']} (voice_id {v['recipe']['voice_id']}), model {v['recipe']['model']}.")
        print(f"Settings: {v['recipe']['settings']}. Text: {v['recipe']['text']}.")
        print(f"Master reference: {v['master']['description']}")
        print("Rejected: " + "; ".join(v["rejected"]))
        print("Take selection: " + " | ".join(v["take_selection"]))
        print("Timing: " + " ".join(data["timing"]["rules"][:3]))
        print("Lines to voice:")
        for c in data["clips"]:
            print(f"  clip {c['id']}: \"{c['script']}\"  ({c['status'].split(':')[0]})")
        print("\nWhen done, reply with a HANDOFF ENTRY JSON: " + json.dumps(data["_protocol"]["changelog_entry_format"], ensure_ascii=False))
    elif a.app == "melius":
        m = data["apps"]["melius"]
        print("MELIUS BRIEF, Ilma Kask\n")
        print(f"Canvas: {m['canvas_url']}")
        print("Identity (verbatim): " + data["identity"]["anchor_paragraph"])
        print("\nQuality lock node " + data["quality_lock"]["melius_node"] + " must be wired into every video node.")
        print("Timing rules:\n  " + "\n  ".join(data["timing"]["rules"]))
        print("\nOpen tasks:")
        for t in data["open_tasks"]:
            print(f"  {t['id']}: {t['what']} ({t.get('credits','-')} cr)")
        print("\nWhen done, reply with a HANDOFF ENTRY JSON: " + json.dumps(data["_protocol"]["changelog_entry_format"], ensure_ascii=False))
    else:
        sys.exit("--app must be melius or elevenlabs")


def cmd_beats(a, data):
    if a.clip is not None:
        c = next((c for c in data["clips"] if c["id"] == a.clip), None)
        if not c:
            sys.exit(f"no clip {a.clip}")
        text, dur = c["script"], a.duration_ms or c.get("melius", {}).get("vo_ms")
    else:
        text, dur = a.text, a.duration_ms
    if not (text and dur):
        sys.exit("need a script and --duration-ms (measure the final VO first)")
    rows, clip, tail = beats(text, dur)
    print(f"VO {dur/1000:.2f} s -> clip length {clip} s (closed-mouth tail {tail} s)")
    if tail > 1.2:
        print("warning: tail over 1.2 s; trim the line or re-roll a longer take")
    if tail < 0.4:
        print("warning: tail under 0.4 s; the last word may be cut")
    end = rows[-1][1]
    print(f"\nTIMING (the take is exactly {clip} s and follows the audio track): her lips move ONLY while her words are heard, "
          f"from about {rows[0][0]:.1f} s to {end:.1f} s. Between sentences the mouth pauses with the voice. "
          f"From {end:.1f} s to {clip}.0 s there is no speech: lips closed and still until the last frame.\n")
    print("SHOT BREAKDOWN:")
    print(f"0.0-{rows[0][0]:.1f} s: silent, lips closed, eyes on the lens.")
    for s_, e, p in rows:
        print(f"{s_:.1f}-{e:.1f} s: says \"{p}\" with [ONE GESTURE].")
    print(f"{end:.1f}-{clip}.0 s: silent: lips closed and still, [closed-mouth action that keeps the scene going].")
    print("\n(merge short phrases so there is about one gesture per 1.5-2.5 s of speech)")


def cmd_set(a, data):
    parent, key = resolve(data, a.path)
    try:
        value = json.loads(a.value)
    except json.JSONDecodeError:
        value = a.value
    old = parent.get(key) if isinstance(parent, dict) else None
    parent[key] = value
    data["changelog"].append({"when": now(), "agent": a.agent, "app": a.app, "task": f"set {a.path}",
                              "changed": [f"{a.path}: {json.dumps(old, ensure_ascii=False)[:120]} -> {json.dumps(value, ensure_ascii=False)[:120]}"],
                              "ids": {}, "result": "ok", "next": []})
    bump(data, a.agent)
    save(a.file, data)
    print(f"set {a.path}; version {data['version']}")


def cmd_log(a, data):
    if a.from_json:
        raw = pathlib.Path(a.from_json).read_text(encoding="utf-8")
        entry = json.loads(re.sub(r"^```\w*|```$", "", raw.strip(), flags=re.M))
    else:
        entry = {"when": now(), "agent": a.agent, "app": a.app, "task": a.task, "changed": a.changed or [],
                 "ids": json.loads(a.ids) if a.ids else {}, "credits_spent": a.credits, "result": a.result, "next": a.next or []}
    entry.setdefault("when", now()); entry.setdefault("result", "ok"); entry.setdefault("changed", [])
    data["changelog"].append(entry)
    bump(data, entry.get("agent", "unknown"))
    save(a.file, data)
    print(f"logged; version {data['version']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(DEFAULT))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show"); s.add_argument("--app"); s.add_argument("--last", type=int, default=10)
    s = sub.add_parser("brief"); s.add_argument("--app", required=True)
    s = sub.add_parser("beats"); s.add_argument("--clip", type=int); s.add_argument("--text"); s.add_argument("--duration-ms", type=int)
    s = sub.add_parser("set"); s.add_argument("path"); s.add_argument("value"); s.add_argument("--agent", default="Claude"); s.add_argument("--app", default="claude")
    s = sub.add_parser("log")
    for k in ("agent", "app", "task", "ids", "from-json"):
        s.add_argument(f"--{k}")
    s.add_argument("--changed", action="append"); s.add_argument("--next", action="append")
    s.add_argument("--credits", type=int, default=0); s.add_argument("--result", default="ok")
    sub.add_parser("validate")
    a = ap.parse_args()
    data = load(a.file)
    if a.cmd == "validate":
        p = validate(data)
        print("valid" if not p else "\n".join(p)); sys.exit(1 if p else 0)
    if a.cmd == "log" and not a.from_json and not (a.agent and a.app and a.task):
        sys.exit("log needs --agent, --app and --task (or --from-json)")
    {"show": cmd_show, "brief": cmd_brief, "beats": cmd_beats, "set": cmd_set, "log": cmd_log}[a.cmd](a, data)


if __name__ == "__main__":
    main()
