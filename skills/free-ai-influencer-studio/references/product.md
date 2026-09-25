# Digital product method

The goal is a finished, sellable low-ticket product ($9 to $27) that buyers actually use, because used products do not get refunded and do get recommended.

## 1. Pick the format from the buyer's moment

| Buyer's moment when they hit buy | Format | Shape |
|---|---|---|
| Daily grinding pain (tired, unfit, scattered) | Challenge or plan | One task per day or per week, tick boxes, themed weeks |
| Avoiding something shameful (money mess, clutter) | Reckoning plus ritual workbook | One guided honest sitting, then a short repeating ritual |
| Acute crisis, needs help now | Swipe file | Situation-indexed cards with word-for-word lines |
| Wants a skill or an output | Workbook or template pack | Fill-in artefacts that produce the thing |

Systems sell and information does not: people pay for structure they can picture using. The persona is the flavour; the transformation is the purchase. Never sell something that contradicts what the persona posts.

## 2. Spec (one screen, before writing)

Title and subtitle; the cover promise line (would this line alone make the buyer want it?); buyer and price; full skeleton with every unit named; palette taken from the persona's wardrobe and world; running footer "TITLE · NAME"; where the catchphrase appears (cover plus one or two designed moments only).

## 3. Sample gate (G3)

Write ONE unit (a day, a week, a card) at finished quality and stop for approval. This locks voice, weight per unit, structure per unit, and how facts are handled. Building everything in one pass produces thin, repetitive middles.

## 4. Full build architecture

Front matter, in order: a letter from the persona (removes shame, states the promise, ends on the catchphrase); "why this works" (the mechanism in plain words, hedged evidence, what the product is not); the measurement loop opening (2 to 3 self-scores out of ten plus a line to their future self, or a usage log for reactive products); "what to expect" (predict the dip); the failure page (no restarts, no catching up, no doubling, just do the next one); "make it fit your life" (3 to 4 adaptations plus the serious-case route to real, named free help).

Body: one unit per page with an identical structure; every unit has a named rule; sequential products get a tick box and a "What I noticed:" line per unit and a progress indicator; a midpoint letter where motivation historically dies (for anything longer than about three weeks); the ending closes the measurement loop and hands over a keep-forever routine.

Back: a divider page with a line of copy; the working pages (the whole method on one page, a printable tracker); a bonus stack of 3 to 6 items mined from seams in the content (a quickstart, a printable, a reference card), never duplicating body content; honest small print (the persona is AI-generated, what the product is not, real free help, written warmly).

Writing: the persona's voice on every page; facts specific, true and hedged; British or American spelling matching the persona; no em dashes if the persona style forbids them.

Safety: health means habits and traditions only, no cures or dosages; money means principles and habits only, no investment advice; relationships mean clarity and self-respect only, with a named helpline for unsafe situations.

## 5. Pricing and platform

$9 to $17 for a thin single document; up to $27 for a full system with a bonus stack. Use the platform the user chooses; otherwise pick by fee and tax handling (see `free-stack.md` section 8). Confirm current fees on the vendor page, and match the launch mechanics to the plan's features: no discount codes means a manual price change on the deadline date; no email flows means the follow-up emails go through a separate email tool.

## 6. spec.json format for build_product_pdf.py

```json
{
  "title": "The Weather Week",
  "subtitle": "Ilma Kask's six-week system for training, light and sauna through an Estonian winter",
  "promise": "Six weeks to a training week that survives a six-hour day.",
  "catchphrase": "The weather is the coach.",
  "byline": "by Ilma Kask, 27, Tallinn",
  "footer": "THE WEATHER WEEK · ILMA KASK",
  "palette": {"ink": "#1F2A2E", "primary": "#3E5641", "accent": "#C8612B", "paper": "#F2EDE3", "muted": "#4A5A66"},
  "cover_image": null,
  "sections": [
    {"type": "letter", "title": "A letter from Ilma", "paragraphs": ["...", "..."], "signoff": "The weather is the coach."},
    {"type": "text", "title": "Why this works", "paragraphs": ["..."]},
    {"type": "scorecard", "title": "Your starting scores", "measures": ["Energy", "Sleep", "Consistency"], "future_line": "A line to you in six weeks:"},
    {"type": "unit", "title": "Week 3 · The Wobble", "progress": [3, 6], "rule": "Shrink the session, never the week.",
     "paragraphs": ["..."],
     "table": {"header": ["DAY", "TRAIN", "OUTDOOR", "RECOVER"], "rows": [["MON", "Lower strength", "10 min walk", "Sleep window"]]},
     "checkboxes": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
     "fill_lines": ["What I noticed:"]},
    {"type": "divider", "title": "The working pages", "line": "Print these. Stick one on the fridge."},
    {"type": "checklist", "title": "Winter kit", "items": ["Headlamp", "Ice spikes"]},
    {"type": "smallprint", "title": "The honest small print", "paragraphs": ["Ilma Kask is an AI-generated character..."]}
  ]
}
```

Section types: `letter`, `text`, `scorecard`, `unit` (always starts on a new page), `divider` (new page, title plus one line of copy), `checklist`, `table` (a standalone table), `smallprint`. Any section may set `"page_break_before": true`. Tables accept `"row_height"` (points) for write-in rows. The cover image is capped at 85 mm high; a square or 4:5 portrait works best. Markdown-style `**bold**` and `*italic*` inside strings are converted. The contents page is generated automatically from section titles with verified page numbers.
