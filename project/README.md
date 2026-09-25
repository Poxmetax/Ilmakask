# Project passport: shared state for every agent

`ilma_kask.project.json` is the single source of truth for the Ilma Kask project: identity and voice locks, lip-sync timing, physics and light rules, locations, every clip with its status and node IDs, open tasks, budget rules and an append-only changelog.

**Every agent (Claude, Melius agent, ElevenLabs, a person) does two things:**
1. **Start:** read the newest file: https://raw.githubusercontent.com/Poxmetax/Ilmakask/main/project/ilma_kask.project.json
2. **Finish:** add one changelog entry describing what changed. Agents that can't write files print a `HANDOFF ENTRY` JSON block; paste it to Claude, who logs it.

Helper (Python 3, no installs):
```
python project/project_state.py show --app melius       # briefing at task start
python project/project_state.py beats --clip 8          # phrase timings + clip length from the VO
python project/project_state.py brief --app elevenlabs  # paste-ready brief
python project/project_state.py log --from-json entry.json
python project/project_state.py validate                # also blocks secrets and signed URLs
```

Briefs: `briefs/melius_skill_ilma_reel.md` (installed as the Melius team skill `/ilma-reel`) and `briefs/elevenlabs_brief.md`.

This repository is public: never put keys, passwords, signed media links, emails or personal data in these files.
