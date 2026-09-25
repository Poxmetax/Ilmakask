# Prompt library

All prompts are English. Fill every [BRACKET] before handing a prompt over; an unfilled bracket is a bug. The identity paragraph (IDP) is written once in Phase 3, stored in `influencer.json` as `identity.anchor_paragraph`, and pasted verbatim everywhere it appears below.

## Contents
1. Face anchor
2. Three-panel character sheet
3. Golden-set edits and plate compositing
4. Relight, light stability and the physics library
5. Crowds, props and acting
6. Clip templates: talking (Route A and B), b-roll, continuation
7. Plate protocol (for the user's own photos)
8. Face-fix edit
9. QC checklists

## 1. Face anchor

Why a separate tight portrait: identity detail survives best at head-and-shoulders scale, and every later image references this one.

```
Cinematic close-up portrait photograph of a real [woman/man] — head and shoulders framing, face filling the frame at maximum identity detail. [NATIONALITY/REGION] [woman/man] with [SKIN TONE, e.g. FAIR LIGHT] skin, clearly reads [AGE] years old — NOT [AGE-8], NOT [AGE+8]. Editorial photography, 85mm f1.4, shallow depth of field, hyperrealistic, ultra detailed skin texture, photorealistic with completely matte unretouched natural skin showing authentic visible pores, fine peach fuzz, natural skin imperfections, real human texture, no plastic skin, no doll-like overdone features, no airbrushing, no skin smoothing, no CGI rendering. No celebrity likeness, no real-person likeness — an original face.
Character — strict facial consistency: [FACE SHAPE], [CHEEKBONES], [JAW], [NOSE], [LIPS], [EYES with a NOT-saturated / no-contact-lens qualifier] (signature anchor — [ANCHOR 1]; second anchor — [ANCHOR 2]; third anchor — [ANCHOR 3]). [HAIR colour with a NOT-drift qualifier, length, texture, parting]. [MAKEUP LINE: either "COMPLETELY BARE NO-MAKEUP FACE — absolutely no makeup" or "GLOWING MINIMAL NATURAL MAKEUP — fresh dewy-but-matte skin, groomed natural brows, a hint of mascara, soft natural lip tone"].
Clothing: plain [COLOUR] crew-neck knit, no logos.
Lighting: soft directional daylight from one side like a large window, gentle falloff, a soft real shadow on the far cheek, every pore and anchor clearly readable. Calm alive gaze, relaxed eyes, the faintest hint of warmth at the corners of the lips.
```

Anchor rules: 2 to 3 anchors, each visible from the front (freckle pattern, a brow colour that contrasts with the hair, a mole, a small scar, one specific earring). Accessories as anchors are counted ("exactly ONE small plain gold hoop in each ear"). Hair colours drift toward the model's default (platinum goes golden), so name the drift you forbid.

## 2. Three-panel character sheet

```
Three-panel character reference sheet of the SAME real [NATIONALITY] [woman/man], [SKIN], clearly reads [AGE] years old, [HAIR SHORT FORM], [KEY ACCESSORY], FULLY CLOTHED in the same outfit in all three panels — ONE SINGLE OUTFIT across the entire sheet. Neutral mid-grey seamless studio backdrop with a soft mottled painterly texture and a gentle natural vignette, the floor fading into the same grey; the subject stands well in front of the backdrop with a soft natural shadow behind — real photographic depth. [PHOTO + ANTI-PLASTIC BLOCK from section 1]. No real brand logos, no copyrighted graphics or text. No celebrity likeness, no real-person likeness.
Panel 1 (left third) — Full body: relaxed lookbook stance, weight on one leg, [HAND POSITION], calm editorial gaze.
Panel 2 (center third) — Side profile MEDIUM bust, strict 90°, wearing the SAME [TOP LAYER] over the SAME [BASE LAYER].
Panel 3 (right third) — Frontal MEDIUM bust, SAME outfit, calm alive gaze, faint warmth at the lips.
Framing rule for panels 2 and 3: face in the upper-middle third, shoulders and upper chest showing, NO tight face crops.
[IDP]
Build: [BUILD with NOT-too-thin / NOT-bulky qualifiers], realistic anatomy, five fingers per hand.
Outfit (identical in all three panels): [ITEMS, generic designs, no logos]. Modest fully-clothed styling, opaque fabric, no body emphasis.
Lighting: soft directional studio daylight from one side, soft real shadows behind the subject. Face identical across all three panels — same person photographed three times. [PALETTE] palette. 16:9 aspect ratio.
```

Keep it under about 3500 characters; long prompts get their tail silently dropped by some generators, so put age, gender, ethnicity and "fully clothed" in the first paragraph.

## 3. Golden-set edits and plate compositing

Golden-set edit (attach the face anchor plus the best sheet panel):

```
Using the attached reference images of the same person, create a new photograph of EXACTLY this person — identical face, bone structure, eye colour, [ANCHORS VERBATIM], hair colour and length. Change only: [ANGLE e.g. three-quarter view facing left] / [EXPRESSION e.g. open natural smile showing teeth] / [LIGHT e.g. warm indoor lamp light from the right] / [OUTFIT]. Photorealistic, matte natural skin with pores, no smoothing, no beauty filter. Do not change the face.
```

Plate composite (start frame for Route B; attach 2 to 3 golden-set images and the user's plate):

```
Place EXACTLY the person from the reference photos into the attached location photo as if photographed there at the same moment. Keep the location photo unchanged: same camera position, lens, perspective, weather and time of day. The person stands [POSITION in frame, e.g. lower-middle, 3 m from camera], [POSE], wearing [OUTFIT]. Relight the person to the location: key light [DIRECTION + COLOUR matching the plate], fill [SKY COLOUR], colour bounce from [NAMED SURFACE], contact shadows under the feet falling [SAME DIRECTION AS OTHER SHADOWS IN THE PLATE]. Match the plate's grain, sharpness and white balance. Identity must match the references 100%: [ANCHORS VERBATIM]. No text, no logos.
```

## 4. Relight, light stability and the physics library

RELIGHT (mandatory in every clip; references are studio images and their light must not leak in):

```
CRITICAL — RELIGHT: discard the reference lighting entirely. Key: [SOURCE, DIRECTION relative to the frame, COLOUR TEMPERATURE]. Fill: [SOURCE]. Colour bounce: [COLOUR] from [NAMED SURFACE] onto [BODY PART]. True contact shadows [WHERE], falling the same direction as every other shadow in the scene. Must look physically present and photographed in the location — never a cut-out; never brighter than the environment.
LIGHT STABILITY: the lighting state is constant for the whole take — not a time-lapse.
```

Light logic worksheet (do this before writing the key light): where is the sun at this place, date and time (use a sun-position tool); which way is the character facing; therefore which side of the face is lit; what colour is the biggest surface near them (that is the bounce).

Physics library (pick what the action needs):

- Walking: "each step lands with weight, heel then toe, no foot sliding; hair and coat hem swing with the stride and settle."
- Wind: "a steady breeze from [DIRECTION] moves loose strands, scarf fringe and grass the SAME direction throughout."
- Breath vapour: only when cold and humid; about 5°C or below reliably, faint above that. "Breath clouds form on each exhale and dissipate within a second, drifting downwind."
- Steam off skin or hair after heat: strongest below freezing; "thin wisps rise from the hair and neck and drift downwind."
- Water: "small wind ripples, reflections of [LIGHTS] break and re-form on the surface."
- Fabric: "heavy wool swings slowly; nylon shell rustles and creases at the elbows."
- Exertion: "chest rises visibly for the first seconds, then settles; a light flush on the cheeks."
- Gravity check phrase: "everything held has weight: the bag pulls on the forearm, the phone dips slightly when lowered."

## 5. Crowds, props and acting

CROWD block (only where crowds are natural for the place and time):

```
Background life: [2 to 6] people at mid-distance doing their own business — [SPECIFIC ACTIONS that fit the place]. All soft-focus, natural pace, never frozen, never looping, never duplicated; faces never sharp or identifiable; nobody crosses in front of the subject's face.
```

Why these rules: background faces are where generators warp first, and identifiable strangers raise privacy issues.

PROP RULE: "[PROP] is present from frame one, never appears, disappears or changes design, and moves only when [SCRIPTED BEAT]."

ACTING TASK (for any clip with a face; direct intentions, not emotions):

```
ACTING TASK — [NAME] (fully invested; the work reads through the eyes):
SCENE DIRECTION (unspoken): [what this take is for]
MOTIVE: [why this person cares, from the backstory]
GOAL: [what they want the viewer to do or feel]
OBSTACLE: [what could make it land wrong]
TACTIC: [how they play it; eyes check the lens after each point]
Moment to moment: «[line 1]» — [action verb + eye work]. «[line 2]» — [...]. Mark the one beat where the register changes.
(Safety: gaze always engaged, natural blink cadence, lips completely still when the audio is silent, no added words, no other voices.)
```

## 6. Clip templates

### 6a. Talking clip, Route B (audio attached, lip sync in the generator or after)

```
TOP PRIORITY (read first):
1. Face and identity match @image1 100% for the entire take.
2. Lip-sync exactly to @audio1; speaks ONLY [LANGUAGE], never any other language.
3. Relit to the real location in @image2 — [ONE-LINE LIGHT LOGIC].
4. [THE ONE PHYSICS RULE THIS CLIP LIVES OR DIES BY]
5. [CROWD RULE or "No other people in frame."]
=== REFERENCE KEY (attach in this order) ===
@image1 — identity reference ONLY (face, hair, outfit), NEVER its lighting. [IDP]
@image2 — the user's own photo of [PLACE] at [TIME, WEATHER]: scene reference only, no readable text, no signage.
@audio1 — this audio file is the ONLY spoken content; use it exactly as recorded. Delivery: [REGISTER].
[RELIGHT block]
IMAGE QUALITY: clean modern flagship phone look; real skin, no smoothing, no cinematic grade, no film grain, no vignette.
Camera: [handheld selfie on her own extended arm, walking bob, mild wide distortion | propped on a ledge, one settle-wobble then locked with a slight tilt | handheld by a companion, micro-sway]. Never a fixed tripod.
Outfit: [OUTFIT]. [PROP RULE]
[ACTING TASK]
Physics: [FROM LIBRARY]
[CROWD block]
Composition: vertical 9:16, face in the upper-middle third, [BACKGROUND ELEMENTS], no readable signs.
Editing: single continuous take.
ON-SCREEN TEXT: none. (Added in post.)
Audio: @audio1 plus ducked ambience — [3 to 4 DIEGETIC SOUNDS]. No music.
SHOT BREAKDOWN: [0.0–x.x s beats keyed to the lines, with one named centerpiece beat, and a short silent hold at the end]
```

### 6b. Talking clip, Route A (native audio-video model)

Same as 6a but replace the audio reference with:

```
VOICE: [age, gender, accent with anti-drift qualifiers e.g. "light Estonian accent, NOT Russian-sounding, NOT American"], [timbre], [pace], [energy].
DIALOGUE (spoken exactly, nothing added): "[LINE]"
```

Keep the line short enough for the clip (about 2.3 to 2.6 words per second) and leave a 0.5 to 1 s silent tail.

### 6c. Lip-sync-ready silent clip (Route B, before a separate lip-sync tool)

Lip-sync models fail on turned heads, occluded mouths and motion blur. Generate the silent clip with: face within about 30° of frontal, mouth unobstructed (no hands, cups, scarves over the lips), even light on the mouth, slow camera, lips gently parted and moving as if talking quietly, no fast head turns. Then run lip sync with the TTS line.

### 6d. Text-over b-roll (no dialogue)

Use 6a minus the audio and acting sections, plus: "TEXT-SAFE FRAME: upper third visually calm", one micro-action with a small arc, 8 to 12 s, last frame close to the first for a clean loop, ambient SFX only.

### 6e. Continuation (part 2 from part 1's last frame)

"CONTINUE THE VIDEO from the last frame of the attached reference clip — seamlessly, with no visual reset. All visuals (person, place, outfit, light, framing, camera) come from that last frame; do not redescribe them." Keep only TOP PRIORITY, reference key, acting task, audio and shot breakdown.

## 7. Plate protocol (give this to the user in Phase 5)

- Vertical 9:16 on the phone's 1x lens (the ultra-wide distorts edges), camera at chest to eye height, level horizon.
- Lock exposure and focus; no portrait mode, no filters, no beauty mode.
- Leave empty space where the character will stand.
- From the same spot shoot: (a) the empty plate, (b) the same frame with a person standing where the character will stand, as a shadow and scale reference, (c) 10 s of video of the empty scene for background motion reference.
- Note date, time and weather in the file name, e.g. `patkuli_2026-10-03_1640_sunny.jpg`.
- Keep strangers small and unidentifiable, or blur them.
- Private property (shops, markets, saunas, marinas): ask permission for commercial content.

## 8. Face-fix edit (for a full-body panel or frame whose face went soft)

```
Edit the existing image. Keep the layout, background, outfit, pose and every other region completely unchanged. Redraw ONLY the head and face of the person so it becomes the same identical face as in the reference portrait — identical structure and features, [ANCHORS VERBATIM]. Sharp, photorealistic, natural matte skin, correct proportions at this scale. Do not change the pose, body, clothing or framing. Preserve the original lighting and colours.
```

## 9. QC checklists

Identity (every image and every clip's first and last frame, against the golden set): face shape; eye colour and shape; every anchor present and on the correct side; hair colour and length; skin texture not plastic; age reads right; hands have five fingers and plausible joints.

Clip: lips move only when audio is present; mouth interior not smeared; no mouth box or blur patch; feet planted, no sliding; shadows point the same way as the plate's shadows; the face is not brighter than the environment; hair and fabric move with the stated wind; background faces not warping; no readable fake text; no logos; no sudden light change; props do not appear or vanish.

On a fail, retry with the failure named in TOP PRIORITY ("previous take: feet slid on the cobbles; feet must stay planted").
