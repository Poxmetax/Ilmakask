# Free stack map (starting point, not truth)

Last compiled: 2026-09-25 from web sources listed per row. Free tiers in this market change monthly and review sites often contradict each other. Before using any row, confirm on the vendor's own pricing or terms page and write a ledger row with `verified_on`. When sources conflict, the vendor page wins; when the vendor page is silent on commercial use, treat it as `unknown`, which the license gate blocks.

## Contents
1. The three questions for every tool
2. Image and identity
3. Video (silent and native-audio)
4. Lip sync
5. Voice (TTS)
6. Assembly, captions, audio
7. Posting
8. Selling the product
9. Hardware routes
10. Known traps

## 1. The three questions for every tool

1. **Allowance:** how much is free, and does it refresh daily or is it a one-time trial?
2. **Watermark:** is there a visible watermark on free exports? (Invisible provenance marks such as SynthID are not a problem; they help with disclosure.)
3. **Commercial use:** do the terms for the free plan allow commercial use of outputs? Also check the model license separately for open weights (code license and weights license can differ) and any regional exclusion.

A tool is only usable for publishing if the answers are: some allowance, no visible watermark, and commercial use allowed. Removing or cropping out a watermark usually breaches the terms, so watermarked outputs are for testing only.

## 2. Image and identity

| Option | Type | What it is good for | Notes as compiled |
|---|---|---|---|
| Google Gemini app image model (Nano Banana family) | cloud, free tier | multi-image reference editing, compositing the character into a plate | Free allowance exists; the Pro variant is much more limited on free; SynthID watermark on all outputs; Google account required (datacamp.com, June 2026). Check commercial terms. |
| ChatGPT Images (gpt-image-2) | cloud, free tier | conversational edits | Launched 21 April 2026; free tier roughly 2 to 3 images per rolling 24 h per community reports, not an official number (datacamp.com). Too tight for volume. |
| OpenArt, Leonardo | cloud, daily credits | consistent-character workflows, training a style | Daily-credit models; check whether free plan outputs are commercial. |
| Krea | cloud, daily pool | fast Flux generation | Free plan reported as not including commercial use (zplatform.ai, 2026). Treat as non-commercial unless the vendor says otherwise. |
| Qwen-Image / Qwen-Image-Edit | open weights | local generation and multi-reference editing | Reported as Apache 2.0 (muapi.ai model list). Needs a GPU locally; hosted endpoints are paid per image. |
| FLUX.2 family | open weights (some variants) | high quality local generation | Licenses differ per variant; read the specific model card before commercial use. |

Identity method on free tools: a reference-edit model fed with 2 to 4 golden-set images beats pure text prompting. Character LoRA training is the strongest lock but needs a GPU or a paid trainer.

## 3. Video

| Option | Free allowance as compiled | Native audio + lip sync | Notes |
|---|---|---|---|
| Kling (3.0 family) | about 66 credits per day, 5 s free clips (ToolChase via dreamina.capcut.com, Sept 2026) | Yes, audio sync with lip sync in 5 languages including English (aivideopicks.com, Aug 2026) | Free exports reported as watermarked (heygen.com blog, Sept 2026). Watermark means not publishable. |
| Seedance 2.x via Dreamina / CapCut | 120 credits per day for eligible US web accounts (dreamina.capcut.com, Sept 2026) | Yes, joint audio-video with phoneme-level lip sync (aivideopicks.com) | Watermark reports conflict between sources; eligibility varies by country. Verify both. |
| Google Veo 3.1 | Sources conflict: some list free daily credits via Flow and AI Studio (aivideopicks.com, Aug 2026), others say video generation is effectively paid-only (felloai.com, toolchase.com, 2026) | Yes | Verify on Google's own pages for the user's country and account type. |
| Hailuo (MiniMax) | daily credits; free credits limited to 768p and 6 s (atlascloud.ai, Aug 2026) | No (silent) per aivideopicks.com | Strong on human faces. Check watermark. |
| Wan (open weights) | unlimited locally | Depends on version | Runs through ComfyUI with as little as 8 GB VRAM per one 2026 source (aiimagetovideo.pro). |
| HunyuanVideo | local / HF Spaces | | The Tencent license restricts EU commercial use (aiimagetovideo.pro, July 2026). Do not use for an EU-based commercial account. |

Rule of thumb from 2026 reviews: most free tiers cap at 720p to 768p and 5 to 10 s, and many watermark. Plan clips at 5 to 10 s and stitch.

## 4. Lip sync (Route B only)

| Option | Character | Where to run free | License notes |
|---|---|---|---|
| LatentSync 1.6 (ByteDance) | best visual fidelity of the open models, slower, heavy on compute | free playgrounds on Fal, Sieve or Replicate per sync.so (July 2026); locally needs a strong GPU | Check the repo license and the weights license before commercial use. |
| MuseTalk (Tencent Lyra Lab) | balance of speed and quality | same playgrounds | Check license. |
| Wav2Lip | best raw sync accuracy, soft mouth on HD, light hardware | local on modest GPUs | The original repo is research-oriented; its authors point commercial users to sync.so. Treat the open model as non-commercial unless verified otherwise. |
| HeyGen | hosted | free plan for 1-minute videos (biff.ai, Sept 2026) | Check watermark and commercial terms on free. |

Lip-sync failure modes reported by practitioners: full-frame blur, visible mouth boxes, artificial teeth, identity drift, jitter, crop damage and sync drift (instavar.com, May 2026). The QC checklist covers each.

## 5. Voice (TTS)

| Option | Commercial on free? | Hardware | Notes |
|---|---|---|---|
| Kokoro-82M | Yes, Apache 2.0 | runs on CPU | Best choice for a no-GPU machine. Stock voices only. |
| Chatterbox (Resemble AI) | Yes, MIT | GPU recommended, around 8 GB | Voice cloning from a few seconds of audio; only clone voices you own or have permission for. A vendor-published blind test reported a preference over ElevenLabs. |
| Google Cloud TTS, Amazon Polly | publish output-use terms and free usage routes (oakgen.ai, Aug 2026) | cloud | Needs a billing account for the free tier; watch the quota. |
| ElevenLabs Free | **No.** The free plan has no commercial license; attribution does not change that (oakgen.ai; bigvu.tv, 2026) | cloud | Commercial use starts on the paid Starter plan. Fine for prototyping a voice only. |
| Fish Audio S2 Pro weights | No, CC-BY-NC (nerdynav.com) | GPU | Non-commercial. |

## 6. Assembly, captions, audio

- **ffmpeg:** free, local, scriptable. `scripts/assemble_clip.py` wraps the common operations.
- **Captions:** Whisper (open source, runs on CPU for short clips) to make an SRT, then burn with the assembly script, or add native captions in the platform editor.
- **Music:** do not use copyrighted songs in the file. Add licensed audio from the platform's own library at posting time, or use royalty-free tracks whose license covers commercial social use.
- **CapCut desktop:** reported to export without a watermark on free (heygen.com blog, Sept 2026). Check its terms for commercial use of templates and effects before relying on it.

## 7. Posting

- **Native scheduling** in the Instagram app or Meta Business Suite: free, no code.
- **Instagram Graph API:** free; requires a Professional (Business or Creator) account linked to a Facebook Page and a Meta app. Local files can be uploaded through the resumable upload host `rupload.facebook.com`, so no public server is needed; this flow is available for apps using Facebook Login for Business (developers.facebook.com, updated March 2026). Publishing quotas are reported as 25, 50 or 100 per 24 h by different sources, and even Meta's pages have been inconsistent; always read the live quota from the `content_publishing_limit` endpoint. Details in `posting.md`.

## 8. Selling the product

The user's choice of platform wins. If they name one, use it; if it is not free, say so plainly, give the fixed cost and the break-even against a percentage-fee platform, then set it up properly. Never swap their choice for a "free" default without asking.

| Platform | Cost as compiled | Free plan? | Tax handling | Notes |
|---|---|---|---|---|
| Stan Store | Creator $29/month or $300/year; Creator Pro $99/month or $948/year; 14-day free trial; 0% Stan transaction fee (Stripe/PayPal processing still applies) | **No** | Not a Merchant of Record. Optional tax collection through Stripe (sellers in the EU and several other regions), and Stripe only collects for the tax regions you are registered in; the seller files and remits | Creator includes the storefront, lead magnets (email capture), community and Instagram AutoDM. Discount codes, email broadcasts and flows, upsells, funnels, affiliates and pixels are Creator Pro only, which changes how a launch price and a follow-up email sequence are run |
| Payhip | Free plan: 5% per sale plus processing; paid plans lower it | Yes | Collects EU VAT; confirm remittance for the seller's country | Pay-what-you-want with `0+` makes free lead magnets; preview files supported |
| Gumroad | 10% + $0.50 per direct sale, 30% through its marketplace, plus processing | Yes | Merchant of Record since 1 January 2025 | Simplest tax position for EU buyers |
| Lemon Squeezy | 5% + $0.50 | Yes | Merchant of Record; Stripe-owned since 2024 | |

Sources: help.stan.store (Creator vs Creator Pro; sales tax article), stan.store pricing blog, help.payhip.com, schoolmaker.com, designrr.io, fungies.io (2026). Fungies publishes comparisons that favour its own product. Confirm every fee on the vendor's page at setup.

Break-even rule of thumb: a fixed monthly fee F beats a percentage fee p on a price P once monthly sales exceed F / (p x P). Example: $29/month against Payhip's 5% on a 24-unit product is roughly two dozen sales a month (exchange rate aside).

## 9. Hardware routes

- **No GPU (integrated graphics, 8 to 16 GB RAM):** everything visual in cloud free tiers; local Kokoro TTS, Whisper small, ffmpeg, PDF build, API publishing. Budget the day around daily credit refreshes: batch prompts, generate when credits refresh, never burn credits on untested prompts (test composition on the cheapest model first).
- **8 to 12 GB VRAM:** add ComfyUI with a small open video model and an image-edit model; light lip sync locally.
- **24 GB+:** local character LoRA, local video, LatentSync-class lip sync; cloud only for native-audio clips.

## 10. Known traps

- Watermarked free export used in a post: not allowed, and cropping it out usually breaches terms.
- Free TTS plan used on a monetised account: license breach even with attribution.
- Open weights with a non-commercial or region-restricted license (check the weights, not just the code).
- Google Maps, Earth or Street View imagery used as a background plate: not allowed.
- Stock or tourism-board photos licensed only for promoting a country, used to sell a product: not allowed.
- Calling a paid platform free (for example Stan Store, which has a trial but no free plan), or planning a discount code or email sequence on a plan that does not include those features.
- A trend audio track baked into the MP4 file instead of added in-app from the licensed library.
