# ElevenLabs brief: Ilma Kask voice

Paste this whole file into any ElevenLabs agent or session (or read it yourself) before generating a line. The live source of truth is the project passport: https://raw.githubusercontent.com/Poxmetax/Ilmakask/main/project/ilma_kask.project.json (section `voice` and `timing`).

## Settings (copy exactly)
- Model: **Eleven v3** (`eleven_v3`)
- Voice: **Veda Sky – Friendly, Warm and Clear**, voice ID `625jGFaa0zTLtQfxwc6Q`
- Settings: leave at defaults (do not change stability, similarity, style or speed)
- Text: the plain script line only. No audio tags like [warm], no `<break>`, no descriptions of the voice, no stage directions.
- Output: MP3 44.1 kHz. File name `clip<N>_vo_take<k>.mp3`.

## The reference
The voice must sound like the approved Balti Jaama Turg market reel (clip 4): warm, clear, relaxed, friendly, talking to one friend, no announcer energy.

## Accept a take only if
1. Its length plus 0.4 s fits the planned clip length (see the table).
2. It sounds like the same person as the market reel (timbre, pitch, age, pace). If not, generate again; Eleven v3 varies from take to take.

## Lines
| Clip | Line | Max take length |
|---|---|---|
| 1 | Ten minutes outside before nine. Real sky, not a window. Grey sky still counts. | 6.6 s (7 s clip) |
| 3 | This loop stays lit all night. So too dark isn't a reason anymore. Walk it if running feels like a fight. | 7.6 s (8 s clip) |
| 5 | Easy most days, long once a week. The bog doesn't care about your pace. | 5.6 s (6 s clip) |
| 7 | Missed yesterday? Don't catch up. Don't double today. Just do today's box. | 5.6 s (6 s clip) |
| 8 | Sunday night, ten minutes: fill next week's board. Empty boxes are decisions. The board's in my bio. | 6.6 s (7 s clip) |

Clips 2, 4 and 6 are approved; do not regenerate their voice.

## When you finish
Reply with a HANDOFF ENTRY so the next agent knows what you did:

```json
{"when": "<ISO-8601>", "agent": "ElevenLabs", "app": "elevenlabs", "task": "<one line>",
 "changed": ["clip 8 take 2, 6.41 s"], "ids": {"files": "clip8_vo_take2.mp3"},
 "credits_spent": 0, "result": "ok", "next": ["render clip 8 in Melius with this take, 7 s"]}
```
