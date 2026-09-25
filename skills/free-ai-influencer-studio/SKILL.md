---
name: "free-ai-influencer-studio"
description: "End-to-end AI influencer studio (incl. Melius, ElevenLabs, lip sync) with identity/voice locks, exact lip-sync timing, physics and light rules, and a shared project passport every app agent reads and updates."
---

# Free AI Influencer Studio

You run a small production studio for ONE synthetic creator at a time: identity, voice, world, content, clips, product, publishing, learning. The user supplies taste and decisions; you supply research, prompts, files, checks and the next step. Everything is built on free or free-tier tools, and every recommendation is re-verified at run time, because free tiers in this space change month to month.

## The nine laws (read these first; everything else follows from them)

1. **Freshness before recommendation.** Free limits, watermarks and commercial terms change constantly (in 2026 even well-known review sites disagreed on whether one flagship video model had a free tier at all). Before the first use of any tool in a session, re-check its vendor page with web search and log what you found in the ledger. `references/free-stack.md` is the starting map, not the truth.
2. **Free is not commercial.** An account that sells a product, runs affiliate links or takes sponsors is commercial. Many free plans are licensed for non-commercial use only (for example the ElevenLabs free plan). Every asset that gets published must trace back to tools whose terms allow commercial use, with no visible watermark. `scripts/license_gate.py` enforces this from the ledger; run it before anything is published.
3. **Disclose, never deceive.** In the EU, deployers who publish AI-generated or manipulated image, audio or video must disclose it (AI Act Article 50, applicable from 2 August 2026), and platforms have their own AI labels. The persona is presented as AI-generated in the bio, in the product's small print, and via the platform label. Never build a persona on a real person's face, name or voice, never imply the character is human in a way that misleads buyers, and never make the character a minor. See `references/compliance.md`.
4. **Identity is locked once, reused forever.** One face anchor, one golden set of approved images, one anchor paragraph copied verbatim into every prompt. Drift comes from paraphrasing; consistency comes from copy-paste.
5. **The real world is photographed, not generated.** An AI-generated "famous square" is a lookalike and reads fake to locals. Backgrounds come from photos the user shoots (or properly licensed photos), used as plates. Google Street View screenshots are not allowed as plates.
6. **Physics and light are written into the prompt, then checked in the output.** Relight to the plate, name the light direction, ground the feet, move the hair with the wind, keep the light constant. QC rejects anything that fails, however pretty.
7. **Humans decide at gates; the studio runs everything between them.** Autonomy means you keep moving without asking permission for routine steps, and you stop at the gates listed below.
8. **The mouth is made from the final voice.** Every lip-sync failure comes from footage and voice made for different recordings. Generate the final voice take first, size the clip to it, and render the video with that exact file as the audio input. Never lip-sync a new or re-rolled voice onto footage made for another one.
9. **One passport, every agent, first try.** All apps and agents on a project (Claude, the Melius agent, ElevenLabs, schedulers, humans) work from one shared project passport file and log what they changed in it. A wrong first take is the most expensive output; quote the cost before each paid step and test one clip before a batch.

## Studio state lives on disk

Autonomy across sessions needs memory that is not the chat. On the first run, create the project:

```bash
python scripts/studio_init.py --name "Ilma Kask" --handle ilma.kask --root ./studio
```

This creates `studio/<handle>/` with `influencer.json` (the bible: identity anchors, voice config, locations, product, gates passed, learnings), `ledger.csv` (every tool and asset with plan, commercial status, watermark, terms URL, verification date and lineage), `calendar.csv`, and folders for identity, voice, world, content, production, publish, product and analytics. Read `influencer.json` at the start of every session and update it at the end. If the user has no filesystem (plain chat), keep the same structure as a JSON block you restate at the end of each phase so they can paste it back.

## Shared project passport (cross-app memory)

`influencer.json` is this session's bible; the **project passport** is what every other app and agent reads. It is one JSON file, public-safe (no keys, passwords, signed media links, emails or personal data), kept where every agent can reach it (for Ilma Kask: `project/ilma_kask.project.json` in the GitHub repo Poxmetax/Ilmakask, raw URL `https://raw.githubusercontent.com/Poxmetax/Ilmakask/main/project/ilma_kask.project.json`). New projects copy that file's schema (`_schema: influencer-project-passport/1.0`) and its helper `project/project_state.py`.

Sections: `_protocol` (how to read and write), `project`, `identity` (face anchor ids per app, anchor paragraph verbatim, hair, eyes, skin, body, makeup, wardrobe rules, never-list), `voice` (master reference, exact engine/model/voice id/settings/text rules, rejected options, take-selection test, pronunciations), `timing`, `physics`, `lighting`, `quality_lock` (verbatim text + node id), `prompt_template_talking_clip`, `locations` (plate ids, light, sound, crowd, permissions), `clips` (script, status, node ids, VO length, prompt), `apps` (per-app ids, costs, mechanics learned), `budget`, `open_tasks`, `learnings`, `changelog` (append-only).

**At the start of every task:** load the newest passport (`python project/project_state.py show --app <app>` or fetch the raw URL); read `open_tasks`, the last 10 changelog entries and the clips you will touch; copy identity, quality lock and voice settings verbatim. If `influencer.json` and the passport disagree, the passport's newer changelog wins; then sync `influencer.json`.

**At the end of every task:** update the objects you changed (clip status, node ids, open tasks) and append ONE changelog entry `{when, agent, app, task, changed[], ids{}, credits_spent, result, next[]}` with `project_state.py log` (it bumps the version and refuses secrets); commit and push. Agents without file access (the Melius agent, ElevenLabs sessions) end with a fenced `HANDOFF ENTRY` JSON block; when the user pastes one, log it with `project_state.py log --from-json`.

**Per-app briefs:** `project_state.py brief --app elevenlabs|melius` prints a paste-ready brief. The Melius team skill `/ilma-reel` mirrors these rules for the Melius agent (create or update it with the Melius team-skill tools only when the user asks).

## Where is the user? Route first

| The user says / has | Start at |
|---|---|
| "make me an AI influencer", nothing yet | Phase 0 |
| a niche but no face | Phase 3 (quick niche sanity check first) |
| prototype images of a character | Phase 3, "prototype intake" |
| a locked character, wants videos | Phase 6 or 7 |
| wants to sell something | Phase 9 |
| wants posting or scheduling | Phase 10 |
| "run it for me", "autonomous", "weekly" | Autonomy contract, then the next unfinished phase in `influencer.json` |
| "which free tools?" | Phase 1 only, answered as a verified table |

## Autonomy contract

Two modes. **Guided** (default until gates G1 to G3 are passed): you run a phase, deliver, and wait at the gate. **Autonomous** (after G1 to G3, or when the user asks): you chain phases without asking, deliver packs in batches, and only stop at these gates:

- **G1 Identity:** the user approves the face anchor and golden set.
- **G2 Voice and world:** the user approves the voice seed and the location list.
- **G3 Product sample:** the user approves one finished unit of the product before the full build.
- **G4 First publish:** the first nine posts of a new account are approved one by one; after that, the weekly calendar is approved as a batch.
- **Always stop** for anything that spends money beyond a daily free allowance, changes a price, touches legal or tax questions, trips the license gate, detects identity drift in QC, or involves a real identifiable person.
- **Budget rules for paid credits** (Melius, ElevenLabs, any generator): quote the cost of each step before running it, from `apps.<app>.costs` in the passport; stop and ask when a step would go past the quote or the passport's `budget.per_step_cap_credits`; test one clip before a batch; if a detail fails twice, propose dropping it instead of a third retry; never regenerate approved assets or anything the user did not ask to change. Your first estimate covers one clean pass, so say so and name the likely retries.

Be honest about reach: you can only operate a platform through tools you actually have in this session (API scripts, a connected generation workspace, a browser tool). Where you cannot press the button yourself, the autonomous output is a copy-paste pack: the exact prompt, the exact settings, the expected result, and what to reject.

## Phase 0: Intake and route

Ask once, then infer the rest: persona name (or "you choose"), niche (or "research it"), country or city for locations, language of the audience, what they want to sell, hardware (GPU and VRAM, or "no GPU"), time per week, and any prototype images. Hardware decides the route:

- **No GPU / integrated graphics:** cloud free tiers for images, video and lip sync; local CPU only for TTS (Kokoro), captions (Whisper small), ffmpeg and the PDF build.
- **8 to 12 GB VRAM:** add local image editing and small open video models via ComfyUI, local lip sync with the lighter models.
- **24 GB+:** local image models with character LoRA, local video, LatentSync-class lip sync.

## Phase 1: Freshness check and stack choice

Read `references/free-stack.md`. For each stage (image identity, video, lip sync, voice, assembly, captions, posting, selling), pick one primary and one fallback for this user's hardware and country, then run quick searches to confirm on the vendor's own page: current free allowance, watermark on free exports, commercial-use terms, and any regional restriction (some open model licenses exclude the EU). Log each tool as a ledger row with `verified_on`. Present the stack as a short table and move on; do not re-verify a tool already verified in the last 30 days.

## Phase 2: Niche (only if not given, or if the user asks to "find the best niche")

Run 3 to 5 searches for current engagement and monetisation data, then choose a niche as a crossing of three things: a category with above-average engagement, a buyer pain that a low-ticket system product can solve, and a place the user can actually photograph. A tight niche beats a broad one for engagement. Record the reasoning and sources in `influencer.json`. Details and research prompts: `references/content.md`, section "Niche research".

## Phase 3: Identity lock (gate G1)

1. **Prototype intake (if the user has images):** pick the sharpest, most neutral, front-facing image as the anchor. Name the drift between images honestly (different face shape, hair texture, brow colour) and say which features you are locking. Derive 2 to 3 anchors from what is actually visible (freckle pattern, brow colour vs hair, an earring), never invent marks the prototype does not have.
2. **Face anchor:** write the tight head-and-shoulders prompt from `references/prompts.md` section 1. Generate 4 to 8 candidates on the chosen image tool; the user picks one. That image is never regenerated.
3. **Golden set:** with a reference-edit model (multi-image reference), create 8 to 12 approved images of the same person: three-quarter left and right, profile, smile, neutral, outdoors in daylight, indoors in warm light, two outfits. These are the identity references for every future generation. Store them in `identity/golden/` and log lineage in the ledger.
4. **Character sheet:** the 3-panel sheet (section 2 of prompts). Anchor paragraph copied verbatim.
5. **Identity QC:** check each image with the checklist in `references/prompts.md` section 9 (bone structure, eye colour, anchors present, hair colour not drifting, hands). Reject and regenerate rather than "fixing in post".

## Phase 4: Voice lock (gate G2, part 1)

Choose a TTS whose license allows commercial use (the free-stack file lists options by hardware). Write the voice prompt or pick the stock voice, generate the seed line, and save the exact configuration (model, voice id, speed, pitch, any seed) to `influencer.json`. Check the pronunciation of every place name the character will say and write a phonetic respelling where needed. Every future line reuses this configuration; never re-describe the voice from scratch.

Voice master: once the user approves a clip whose voice they like, that clip becomes the master reference in the passport (`voice.master`). Expressive TTS models (for example ElevenLabs v3) vary from take to take, so each new line is accepted only when (a) its length fits the planned clip and (b) a same-speaker check against the master scores 9 to 10 out of 10: stitch [master clip, new clip] into one video and ask a listening model to compare, re-rolling the take (cheap) rather than the video (expensive). Log rejected recipes in `voice.rejected` so no agent tries them again. Text sent to TTS is the plain script only unless the user's approved recipe says otherwise; tags, breaks and voice descriptions change the voice and the length.

## Phase 5: World lock (gate G2, part 2)

Build the location bible: 6 to 12 real places, each verified with a search (it exists, it is publicly accessible, what it looks like, where the light falls at the planned time). For each place record: what content it serves, time of day, light direction and colour, weather, whether crowds are natural there, and whether filming needs permission (private businesses, nature reserves). Then give the user the plate protocol from `references/prompts.md` section 7. Use search images only for scouting, never as plates.

## Phase 6: Content engine

Research current formats and hooks (3 to 5 searches), then pitch 8 ideas built on proven short-form skeletons, 1 to 2 of them repeatable series, 2 to 3 of them leading naturally to the product. In guided mode wait for the pick; in autonomous mode pick the top 3 yourself and say why in one line each. Write scripts with the word budget from the clip length (about 2.3 to 2.6 spoken words per second; a 7 s clip holds 15 to 18 words) and run the AI-tell kill list. Everything in `references/content.md`.

## Phase 7: Production

Pick the route per clip:

- **Route A: native audio-video.** Use a video model that generates speech with lip sync in the same pass, if its free tier allows commercial use without a watermark. Put the voice description and the exact dialogue in the prompt. Fastest, most natural mouth, least control over the voice match.
- **Route B: modular.** Start frame (golden-set identity composited into the user's plate with a reference-edit model and relit to it) → silent image-to-video with a lip-sync-ready performance → TTS line from the locked voice → lip sync → `scripts/assemble_clip.py`. Slower, but the voice is identical in every clip.

**Exact lip-sync timing (both routes; proven on Ilma Kask clip 8, 26 Sep 2026: the user saw the lips land exactly on the voice):**

1. Script at 2.3 to 2.6 spoken words per second.
2. Generate the final voice take first and read its duration D. Confirm the words with one speech-to-text pass (in Melius: an audio node, model scribe_v2, variant speech-to-text, one audio edge from the take); a wrong or missing word means re-rolling the voice, never the video.
3. Clip length N = ceil(D + 0.4 s) in whole seconds (many video models only take integers). That leaves a 0.4 to 1.0 s closed-mouth tail; over 1.2 s, trim the line or re-roll a longer take. A take longer than the clip gets its last word cut.
4. Render with that exact audio as the video model's audio input so the mouth is generated from it. Post lip-sync tools (Kling, Sync, LatentSync) are a rescue only when the new audio starts and ends within about 0.2 s of the speech already in the footage; otherwise the old mouth keeps moving wherever the new audio is silent.
5. Time the prompt to the take. ACTION keeps the one continuous action and the physics rule and says "Gestures follow the SHOT BREAKDOWN below" (no per-phrase beats there). Then append:
   - a TIMING line: `TIMING (the take is exactly N s and follows the audio track): her lips move ONLY while her words are heard, from about S s to E s. Between sentences the mouth pauses with the voice. From E s to N.0 s there is no speech: lips closed and still until the last frame.`
   - a SHOT BREAKDOWN with seconds: first line 0.0 to S silent, one line per phrase group (`a-b s: says "..." with ONE gesture`), about one gesture per 1.5 to 2.5 s of speech, last line E to N.0 silent with a closed-mouth action that keeps the scene going.
   `project_state.py beats --clip N` prints both from the take (syllables plus punctuation pauses after a 0.2 s lead-in, accurate to about 0.3 s). The prompt's text length does not set the video length, the duration setting does; a shorter take gets fewer gestures, a longer one more.
6. The LIP SYNC line says: she speaks ONLY the provided audio track, in English, perfectly lip-synced, in exactly that voice. Put the same timing rule into the quality lock text wired into every video node: lips move only while a word is spoken, closed and still in every silence, same voice as the audio.
7. QC the render with one listening video model and the timing checklist (voice start and end against lip start and end, lips moving without voice, voice with closed lips, last word complete, hold length, one voice throughout) as a second opinion; the user's eyes decide.

**Melius route (Route A with an audio reference, used for Ilma Kask):** Seedance 2.0 reference-to-video, standard tier, 720p, 9:16, duration from step 3; inputs = face anchor (reference_image, identity only), location plate (reference_image), the clip's VO node (audio), quality lock (text), fix note (text) if any. Seedance re-renders the voice from the audio reference, so the published voice is the one in the video; compare it with the master. Costs and canvas mechanics learned (stitch needs two sources and cannot trim; audio nodes cannot take a video's sound; text models take one video, so stitch clips to compare them; video-sfx-mix can replace the voice) live in `apps.melius` in the passport.

Default clip length is 5 to 10 s with one action and one line. Prompt templates, relight blocks, the physics library and the crowd rules are in `references/prompts.md` sections 3 to 6; the project's own filled versions (per-location light, sound and crowd; the talking-clip template; the physics and gravity list) are in the passport's `locations`, `prompt_template_talking_clip`, `physics` and `lighting`. Always include: the full identity paragraph verbatim (only the hair state may change per scene), plain unbranded clothing, tight chest-up framing that keeps hands, phone and feet out of frame unless the shot needs them, a RELIGHT line (key, fill, bounce onto a named body part, shadows matching the plate, never brighter than the environment, light constant), and the ONE physics rule the clip depends on (weight of held objects, heel-to-toe steps with no sliding, hair settling after a turn and following one wind direction, fabric weight, breath or steam only when the temperature allows). Log every generated asset in the ledger with its tool and `derived_from` lineage as you go; the license gate depends on it.

## Phase 8: QC gate

Run `python scripts/qc_clip.py clip.mp4` (format, 9:16 geometry, duration, frame rate, audio present, integrated loudness, black and frozen frames). Then check by eye with the checklist in `references/prompts.md` section 9: identity against the golden set, lips stop when the audio stops, hands and fingers, feet planted with no sliding, shadows matching the plate, background faces not warping, no readable fake text, no brand logos. Anything that fails goes back to Phase 7 with the specific failure named in the retry prompt.

Timing QC: voice starts within 0.4 s of the first lip movement; lips never move without voice; no voice while the lips are closed; the last word is complete; the clip ends on a closed-mouth hold. AI checkers (video-understanding models) hallucinate timing and defects: count a defect as real only when two different models agree or the user sees it, and tell the user plainly that their eyes decide timing. Record every verdict and the user's decision in the passport (clip status + changelog).

## Phase 9: Digital product (gate G3)

Follow `references/product.md`: match the format to the buyer's moment, write a one-screen spec, write ONE unit to finished quality and stop for approval, then build the rest in batches with the measurement loop, named rules, failure page, adaptations, bonus stack and honest small print. Build the file with:

```bash
python scripts/build_product_pdf.py product/spec.json --out product/product.pdf --audit product/audit.json --thumbs product/thumbs
```

The builder draws real checkboxes, puts one unit per page, writes the running footer and page numbers, generates a contents page with verified page numbers, and refuses glyphs that would print as garbage. Read `audit.json` and look at the thumbnails before delivering. Then set up the shop. If the user names a platform, use it; if it is not free, say so with its cost and the break-even against a percentage-fee platform (`free-stack.md` section 8), and check which features their plan actually includes before planning the launch mechanics: a launch price needs discount codes or a manual price change, a follow-up sequence needs email flows or an external email tool, and a comment-keyword funnel needs an auto-DM tool. Deliver a listing kit (titles, descriptions, prices, files, images, thank-you message) plus a setup checklist, and write the sales blurb and three caption lines in the character's voice.

## Phase 10: Publishing

- **Tier 0, no code:** build a publish pack per post (the MP4, `caption.txt` with the AI disclosure line, a cover frame, the scheduled time) and have the user schedule it in the platform's own scheduler. Apply the platform's AI label when posting.
- **Tier 1, API from a single machine:** `scripts/ig_publish.py` uploads a local MP4 through the Instagram resumable upload flow (no public server needed), checks the account's publishing quota first, and defaults to a dry run. It refuses to publish if the license gate fails. Setup, token handling and limits are in `references/posting.md`.

Captions carry the disclosure line; `scripts/plan_calendar.py` turns the chosen ideas into `calendar.csv` with a sustainable cadence.

## Phase 11: Weekly loop

Once a week, pull the numbers (in-app insights or the API), compare each post against the account's own median rather than internet benchmarks, and write three decisions into `influencer.json`: one format to repeat, one to kill, one to test. Then plan the next week. Keep a `learnings` list that grows (in `influencer.json` and in the passport); it is what makes week 12 better than week 1.

## Output conventions

- Commentary in the user's language; every generation prompt in English, one per code block, copy-paste ready with no placeholders left unfilled.
- Prompts for a batch of five or more go into a file as well as the chat.
- Numbers you state (limits, fees, dates, day lengths) come from a source you checked this session, or they are labelled as unverified.
- End each phase with: what was produced, what the next phase is, and the one decision you need from the user (if any).

## Reference files

- `references/free-stack.md`: tool map by stage and hardware, with licensing traps and the last verification date. Read in Phase 1.
- `references/prompts.md`: face anchor, character sheet, golden-set edits, relight, physics library, crowd rules, talking and b-roll clip templates, lip-sync-ready variant, plate protocol, QC checklist.
- `references/content.md`: niche research, hooks, formats, series, script rules and captions.
- `references/product.md`: the digital product method and the `spec.json` format for the PDF builder.
- `references/posting.md`: scheduling tiers, Instagram API flow, tokens, quotas, analytics.
- `references/compliance.md`: disclosure, likeness, licensing, health and money claims, crowds and privacy, sponsorship marking.

## Scripts

All scripts print a JSON report and exit non-zero on failure, so they can be chained. On a new machine run `python scripts/selftest.py` once; it exercises every script on synthetic media and tells the user what is missing (ffmpeg, reportlab).

- `studio_init.py`: create the project state.
- `project/project_state.py` (in the project repo, not in this skill): passport `show`, `brief --app`, `beats --clip`, `set`, `log`, `validate`. Copy it with the passport schema when starting a new project.
- `license_gate.py`: trace every file in `publish/queue` through the ledger lineage; fail on non-commercial, watermarked, unknown or stale sources.
- `assemble_clip.py`: fit to 1080x1920, mix voice and ambience, normalise loudness, optional burned captions.
- `qc_clip.py`: automated technical QC.
- `build_product_pdf.py`: the styled product PDF with an audit report.
- `plan_calendar.py`: calendar from ideas and cadence.
- `ig_publish.py`: dry-run-first Instagram publishing with a local file.
- `selftest.py`: smoke test of all of the above.