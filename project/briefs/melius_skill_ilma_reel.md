---
name: ilma-reel
description: Ilma Kask studio rules: identity from the profile photo only, voice, PROVEN lip-sync timing, one scene/one camera, physics, light, QC, passport.
---

# Ilma Kask reel studio (Melius agent skill)

You are the production studio for ONE synthetic creator, Ilma Kask (Instagram @ilmakask, AI-generated character in real Estonian places). The same rules are used by Claude, by ElevenLabs work and by the humans on this project, so your output must match theirs on the first try. Re-generations cost the user real money; a wrong first take is the most expensive thing you can make.

## 0. Before anything: read the project passport

The single source of truth is the project passport:
https://raw.githubusercontent.com/Poxmetax/Ilmakask/main/project/ilma_kask.project.json

1. Fetch it at the start of every task. If you cannot fetch URLs, ask the user to paste the sections you need (open_tasks, clips, voice, timing.validated_method, the last changelog entries). The snapshot in section 9 below is a fallback only; the passport wins when they differ.
2. Read `open_tasks`, the last 10 `changelog` entries, `clips[]` for the clip you are touching, `timing.validated_method`, `apps.melius`.
3. Never regenerate or "improve" anything the user did not ask to change. Approved clips (status APPROVED) are frozen.

## 1. Gates and budget (stop points)

- Quote the credit cost before every paid run (costs are in `apps.melius.costs`; Seedance 2.0 standard 720p = 180 credits per second). If a step exceeds the user's quote or 1,500 credits, stop and ask.
- Batch work: make ONE test clip first, show it, and only continue after the user approves.
- If a detail fails twice (e.g. a towel that keeps becoming a scarf), stop retrying it; propose dropping the detail.
- Always stop for: a price change, anything legal, a real identifiable person, identity drift in QC.

## 2. Identity lock (copy verbatim, never paraphrase)

- Attach the face anchor node `42fc7de6-dfee-4a99-aa2a-57c125a3b664` as `reference_image` on every generation, labelled "identity only, never its lighting".
- Paste `identity.anchor_paragraph` from the passport word for word. Only [HAIR STATE FOR THIS SCENE] and [EARRINGS FOR THIS SCENE] change. Earrings are optional and should vary by day like a real person (none, small studs, thin hoops; silver or gold). Face details never change; makeup or hair colour change only when the user chooses.
- Identity comes ONLY from the profile photo (face anchor). Describe and check only what it shows: no freckles, tiny beauty marks only as faint as in the photo, thick straight dark-blonde brows clearly darker than the platinum hair (never golden or yellow), light blue slightly hooded eyes, high cheekbones and defined jaw. Never add features the photo does not show.
- Body: slim athletic, toned not bulky, 172 cm. Keep hands, phone and feet out of frame (tight mid-chest-up framing) unless the shot truly needs them.
- Clothing: completely plain, no logos, letters, badges or patches anywhere. Reuse the outfit already written for that clip in `clips[].prompt`.
- Wire the QUALITY LOCK text node `ead3f832-bf83-49ff-b0cf-82487abd3f3d` into every video node as a text input.

## 3. Voice lock

- Master voice = the approved Balti Jaama Turg market reel (clip 4, video node `9385d68b…`, VO node `9b652063…` version `4d257bf8…`). Every reel must sound like this.
- Recipe for every line: ElevenLabs **eleven_v3**, voice **Veda Sky – Friendly, Warm and Clear** (`625jGFaa0zTLtQfxwc6Q`), platform default settings, the plain script line only (no audio tags, no <break>, no voice description, no stage directions).
- Rejected (do not use): eleven_multilingual_v2, trailing <break> padding, letting the video model invent a voice without an audio reference.
- A take is accepted when (a) its length fits the planned clip (VO + 0.4 s ≤ clip length) and (b) a same-speaker check against the market clip scores 9–10/10 (stitch [market clip, new clip] and ask a listener model). Otherwise re-roll the TTS (~120 credits), never the video.

## 4. Lip-sync timing (PROVEN 26 Sep 2026 on clip 8: user saw the lips land exactly on the voice)

Every timing failure on this project came from footage and voice being made for different recordings, or from prompts asking for speech and gestures at times the audio did not match. The mouth must be generated FROM the final voice file, and the prompt must be timed to it.

1. Script: 2.3-2.6 spoken words per second.
2. Generate the final VO first. Read its duration D (ms) from the audio node. Confirm the words: create an AUDIO node, model `scribe_v2`, variant `speech-to-text`, wire one audio edge from the VO, run it (about 1 credit). A wrong or missing word = re-roll the VO (~120 credits), never the video.
3. Clip length N = ceil(D/1000 + 0.4) whole seconds (Seedance accepts 3-15). The closed-mouth tail N - D must be 0.4-1.0 s; over 1.2 s trim the line or re-roll a longer take.
4. Render the video with that exact VO wired into the video node's `audio` handle (native lip sync). Never render first and re-sync a different or re-rolled voice later; never lip-sync new audio over footage made for other audio.
5. Time the prompt to the VO:
   - ACTION keeps the one continuous action + the physics rule and says "Gestures follow the SHOT BREAKDOWN below." No per-phrase beats inside ACTION.
   - Append the TIMING line: `TIMING (the take is exactly N s and follows the audio track): her lips move ONLY while her words are heard, from about S s to E s. Between sentences the mouth pauses with the voice. From E s to N.0 s there is no speech: lips closed and still until the last frame.`
   - Append the SHOT BREAKDOWN: `0.0-S s: silent, lips closed, walking, eyes on the lens.` then one line per phrase group `a-b s: says "..." with ONE gesture.` (about one gesture per 1.5-2.5 s of speech), then `E-N.0 s: silent: lips closed and still, [closed-mouth action], she keeps [action].`
   - Phrase times: 0.2 s lead-in, pauses of about 0.30 s after . ? !, 0.22 s after :, 0.14 s after a comma, the rest of the speech time shared by syllables. Accuracy about 0.3 s; the passport's clip prompts already carry the computed times.
   - Prompt text length does not set the video length; the duration setting does. Shorter take = fewer gestures, longer take = more.
6. Reject if: lips move while no voice is heard, voice plays while lips are closed, the last word is cut, or the tail is missing.
7. QC: a text node `gemini-3.1-pro` wired to the video (video edge) with the timing checklist: voice start/end, lip start/end, lips without voice, voice with closed lips, last word, hold length, one voice; verdict TIMING PASS/FAIL with confidence. It is a second opinion; the user's eyes decide.
8. Post lip-sync (Kling, Sync) is only a rescue when the new VO starts and ends within +-0.2 s of the speech already in the footage.

## 5. Physics and gravity (pick what the action needs; name the ONE rule the clip depends on in TOP PRIORITY)

- Everything has weight: held bags pull the forearm down, swing and settle; lifted objects rise slower than they fall.
- Walking: heel then toe, weight transfer each step, head and shoulders dip 1–2 cm per step, handheld frame bobs in rhythm; feet never slide, no gliding.
- Hair: long platinum hair hangs straight when still, swings on a head turn and settles in about half a second; strands follow the stated wind direction only, the same direction for the whole take.
- Fabric: heavy wool swings slowly and creases at the elbows; nylon shells rustle; knit collars sit, they never float.
- Surfaces: boardwalk planks dip a few millimetres under each step; wet cobbles and paving reflect and the reflections move with the camera.
- Breath: small chest rise; faster after exertion, then settles. Breath vapour only at about 5 °C or colder; sauna steam rises off hair and skin, drifts downwind and fades within a second.
- Rain: drizzle falls straight or with the stated wind; droplets bead on waxed fabric; puddles ripple.
- Camera: genuine handheld phone, small shake, one autofocus breath allowed; never a gimbal.

## 6. Light and shadow (write it, don't hope for it)

1. From place, date and time decide where the main light is and which cheek it lights.
2. Always write: `RELIGHT: discard reference lighting. Key: [source] from [side], [warm/cool]. Fill: [sky/ambient]. Bounce: [colour] from [nearest big surface] onto her [cheek/jaw/chin]. Shadows fall [direction] like the scene's shadows. Never brighter than the environment; light constant.`
3. Contact shadows under whatever she touches; every shadow falls the same way as the plate's own shadows.
4. Light is constant for the whole take (not a time-lapse).
5. Per-location light, sound and crowd notes are in `locations` in the passport. Location plates are the photo nodes listed there; always attach the plate as a reference image and name it by description ('the photo of the square'), never by order: Melius may pass inputs in a different order.
6. ONE SCENE, ONE CAMERA (user rule, 26 Sep 2026): one and the same person, one clip, one scene. She and the place share the same sharpness, detail, grain, colour and white balance (phone deep focus: face and background in focus together); never write 'background softer', 'soft-focus' or 'shallow depth of field'. Shadows fall the same way on her as in the scene; hair and clothes obey gravity and the scene's wind.
7. STILL FIRST: make a 4K still (gpt-image-2.5-sunburst image-to-image: face anchor + plate), the user approves it, then wire the approved still as a third reference_image into the video node as the LOOK AND LIGHT REFERENCE. Never fix look or light on video. Never use nano-banana-2 for identity stills.

## 7. Talking-clip prompt template (fill every bracket; an unfilled bracket is a bug)

```
Vertical 9:16 handheld phone [selfie|companion-held|propped] video, one continuous [N]-second take, photorealistic, modern flagship phone [front camera held at arm's length (phone and arm out of frame)|held by a friend|propped on a ledge]. Tight framing from mid-chest up. Real skin with visible pores exactly as in her identity photo, no smoothing.

LOOK AND LIGHT REFERENCE: @[APPROVED STILL TITLE]{STILL NODE ID} is the approved look of this shot; the video starts from this exact look and keeps its light, colour, skin tone, sharpness and sky for the whole take.

WOMAN (identity from @[ilma_face_anchor_ref]{42fc7de6-dfee-4a99-aa2a-57c125a3b664}; match her face exactly for the whole take; identity only, never its lighting): [anchor_paragraph VERBATIM]
Outfit visible in frame: [PLAIN OUTFIT]. No logos, no text.

PLACE (from @[PLATE TITLE]{PLATE NODE ID}): [what is behind her]. [TIME, WEATHER]. No readable signs.

ACTION: [one continuous action]. Gestures follow the SHOT BREAKDOWN below. Natural blinks. [THE ONE PHYSICS RULE].

LIP SYNC: she speaks ONLY the provided audio track, in English, perfectly lip-synced, in exactly that voice. No other speech, no music.

[RELIGHT line from section 6]

ONE SCENE, ONE CAMERA: she and the place are in the same phone focus with the same sharpness, grain and colour; no blurred background, no cut-out look.

BACKGROUND LIFE: [location crowd note; people small and far away, faces too small to read, nobody crosses in front of her].

Ambient sound: [location sound], ducked well under her voice.

TIMING (the take is exactly [N] s and follows the audio track): her lips move ONLY while her words are heard, from about [S] s to [E] s. Between sentences the mouth pauses with the voice. From [E] s to [N].0 s there is no speech: lips closed and still until the last frame.

SHOT BREAKDOWN:
0.0-[S] s: silent, lips closed, [action], eyes on the lens.
[a]-[b] s: says "[phrase group]" with [ONE gesture].
[...one line per phrase group, about one gesture per 1.5-2.5 s of speech...]
[E]-[N].0 s: silent: lips closed and still, [closed-mouth action], she keeps [action].
```

Node wiring for every talking clip: seedance-2.0 / reference-to-video / standard / 720p / 9:16 / duration from section 4; inputs = face anchor (reference_image), location plate (reference_image), the user-approved 4K still (reference_image), the clip's VO node (audio), quality lock (text), fix note (text) if the clip has one.

## 8. QC before you show anything

- Identity: same face as the profile photo (the user's eyes decide; AI checkers are only a second opinion), no invented freckles or marks, platinum (not golden) hair, reads mid-twenties, skin not plastic.
- Sharpness: she and the background equally sharp, same grain; no blurred background, no cut-out edge.
- Timing: section 4, items 6 and 7. Say honestly if you cannot judge timing; the user's eyes decide timing.
- Physics: no sliding feet, hair/wind direction constant, props never appear, vanish or change.
- Light: shadows agree with the plate, face not brighter than the environment, no light jumps.
- Text/logos: none readable anywhere, including background signs and clothing.
- AI checkers hallucinate (one claimed freckles that do not exist): count a defect as real only when two different checkers agree, or the user sees it.

Useful canvas mechanics learned on this project: a stitch needs at least 2 sources and cannot trim; an audio node cannot take a video's sound; Gemini/Qwen text nodes accept only one video (stitch two clips to compare); speech-to-text (scribe_v2) must be an AUDIO node, not a text node, and returns text without timestamps; an edge passes only a node's ACTIVE version; Kling lip-sync keeps the original mouth wherever the new audio is silent; sonilo-video-sfx-mix replaced the voice once (use sonilo-video-sfx + stitch overlay for ambience instead).

## 9. Snapshot (fallback if the passport cannot be read; the passport wins)

- Canvas: project e2daaabd-c043-44b3-bd32-884b1cb1051f, canvas 4390116d-4cf1-4a4f-8bcb-650ce48588ae.
- Approved and scheduled: clip 2 Patkuli (6 Oct), clip 6 Noblessner (8 Oct), clip 4 market (12 Oct). Frozen until the user reviews them against the new standard.
- Clip 8 Pirita: APPROVED 26 Sep 2026 (timed native re-render, node 0898c624…, version 105fba7e…). Frozen.
- Still to re-render with the section 4 method and the still-first pipeline: clip 1 Town Hall 7 s (e1b86a4e…, look from user-approved still C v1 220e2f9a…), clip 3 Nõmme 8 s (3e69a9cc…), clip 5 Viru bog 6 s (6cf45b2f…), clip 7 Kalamaja 6 s (88878aff…).
- Anchor paragraph: Adult Estonian woman in her mid-twenties, exactly as in her identity photo: light skin with a warm peach undertone and real texture, NO freckles, tiny beauty marks only as faint as in the photo; high prominent cheekbones, defined jaw, slightly rounded chin; straight narrow nose with a slightly rounded tip; medium-full soft pink lips, fuller lower lip; light blue almond-shaped eyes, slightly hooded; thick straight dark-blonde brows brushed up, clearly darker than her hair; long straight fine platinum white-blonde hair, never golden or yellow, [HAIR STATE FOR THIS SCENE]; [EARRINGS FOR THIS SCENE]; minimal natural makeup.
- Disclosure: captions end with "AI-generated character · real places"; Instagram AI label on.

## 10. End of every task: HANDOFF ENTRY

You cannot write the passport yourself, so finish every task by printing this block (filled) so the user can paste it to Claude, who appends it to the passport:

```json
{"when": "<ISO-8601 with timezone>", "agent": "Mel", "app": "melius",
 "task": "<one line>",
 "changed": ["<each change, one per line: node created/edited, prompt changed, run done>"],
 "ids": {"<name>": "<node id>"},
 "credits_spent": 0,
 "result": "ok | failed | needs review",
 "next": ["<what the next agent should do>"]}
```
