# Ilma Kask: AI influencer project

**Ilma Kask** (Instagram @ilmakask) is an AI-generated character filmed in real Estonian places. This repository is the shared home for every person and agent working on the project.

## Start here (every agent, every task)
1. Read **`project/ilma_kask.project.json`**, the project passport. It holds the identity and voice locks, lip-sync timing rules, physics and light rules, locations, every clip with its status, open tasks, budget rules and the change log.
   Raw link for agents: https://raw.githubusercontent.com/Poxmetax/Ilmakask/main/project/ilma_kask.project.json
2. When you finish, add one change-log entry (`python project/project_state.py log ...`). Agents that can't write files end with a `HANDOFF ENTRY` block for someone to log.

## Folders
| Folder | What it is |
|---|---|
| `project/` | The passport, its helper script, and briefs for Melius and ElevenLabs |
| `skills/free-ai-influencer-studio/` | The Claude skill that runs the studio (updated 2026-09-25: passport, timing law, budget rules, Melius route) |
| `skills/melius-ilma-reel/` | The Melius team skill `/ilma-reel` (import it in Melius > Settings > Agent > Skills if it is missing) |
| `studio/ilma.kask/` | Studio state: bible (`influencer.json`), ledger, calendar, go-live guide, post queue with captions |
| `posts/` | Post images served to the scheduler (Metricool) |
| `ref/` | Face anchor reference image |

## Kept out on purpose
This repository is public. It never contains passwords, API keys, signed media links, emails, the paid product (The Weather Week PDF and its source), or personal data. `project_state.py validate` blocks the obvious ones.
