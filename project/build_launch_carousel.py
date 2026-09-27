"""Build the 5 Oct 2026 launch carousel for The Weather Week (Instagram, 1080x1350).

Rules (user, 27 Sep 2026): the paid product is never shown on Instagram; posts may only
describe what it contains. The only page shown is the free First Seven sample page.
Every slide carries the ad marker (own product) and the AI-character footer.
Usage: python3 project/build_launch_carousel.py --free-page <png of the free First Seven page> --out posts/
"""
import argparse
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = (247, 243, 234)
GREEN = (62, 83, 66)
RUST = (181, 88, 48)
INK = (35, 40, 45)
GREY = (85, 95, 105)
SHADOW = (208, 199, 184)
FD = "/usr/share/fonts/truetype/dejavu/"


def font(style, size):
    name = {"b": "DejaVuSerif-Bold.ttf", "i": "DejaVuSerif-Italic.ttf", "r": "DejaVuSerif.ttf"}[style]
    return ImageFont.truetype(FD + name, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, fill, max_w=940, gap=1.28):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * gap)
    return y


def base(n, total):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([29, 29, W - 29, H - 29], outline=GREEN, width=2)
    d.text((70, 1272), "AD · ILMA KASK · AI-GENERATED CHARACTER", font=font("r", 22), fill=GREY)
    t = f"{n}/{total}"
    d.text((W - 70 - d.textlength(t, font=font("r", 22)), 1272), t, font=font("r", 22), fill=GREY)
    return im, d


def bullets(d, x, y, items, fnt, max_w=900):
    for it in items:
        d.rectangle([x, y + 16, x + 12, y + 28], fill=RUST)
        y = block(d, x + 36, y, it, fnt, INK, max_w=max_w - 36) + 18
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--free-page", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    total = 6
    slides = []

    im, d = base(1, total)
    d.text((70, 300), "AD · MY OWN PRODUCT", font=font("b", 30), fill=RUST)
    y = block(d, 70, 360, "Six weeks to a training week that survives a six-hour day.", font("b", 76), GREEN, gap=1.18)
    y = block(d, 70, y + 30, "The Weather Week: my plan for training, light and sauna through a northern winter.", font("i", 40), INK)
    d.text((70, y + 40), "The weather is the coach.", font=font("i", 36), fill=RUST)
    d.text((W - 70 - d.textlength("swipe >", font=font("r", 26)), 1228), "swipe >", font=font("r", 26), fill=GREY)
    slides.append(im)

    im, d = base(2, total)
    d.text((70, 120), "WHAT'S INSIDE", font=font("b", 30), fill=RUST)
    y = block(d, 70, 175, "A 27-page printable plan, built for the dark months.", font("i", 44), INK)
    bullets(d, 70, y + 50, [
        "Six weekly boards: train, outdoor, recover, deep work.",
        "A session library: strength, outdoor, mobility.",
        "Light, the Baltic way.",
        "Sauna, the Estonian way, with the safety notes that matter.",
        "A simple food spine: defaults, not a diet.",
        "Three bonuses, including eight real Estonian places.",
    ], font("r", 38))
    slides.append(im)

    im, d = base(3, total)
    d.text((70, 120), "HOW IT WORKS", font=font("b", 30), fill=RUST)
    y = block(d, 70, 175, "One board a week. One rule. One real place.", font("b", 60), GREEN, gap=1.2)
    weeks = ["Week 1 · The Board", "Week 2 · Two in the Tank", "Week 3 · The Wobble",
             "Week 4 · Heat, Then Air", "Week 5 · The Long Easy", "Week 6 · Keep Five"]
    y += 40
    for wk in weeks:
        d.text((70, y), wk, font=font("r", 40), fill=INK)
        y += 64
    block(d, 70, y + 30, "Tick what you did. Miss a day, keep the week.", font("i", 40), RUST)
    slides.append(im)

    im, d = base(4, total)
    d.text((70, 120), "IT'S FOR YOU IF", font=font("b", 30), fill=RUST)
    y = block(d, 70, 175, "You live where winter steals the daylight.", font("b", 60), GREEN, gap=1.2)
    bullets(d, 70, y + 50, [
        "The dark months keep winning.",
        "You want short sessions that survive a bad day.",
        "You would rather walk a lit loop than skip.",
        "You like a sauna. No sauna? A hot shower works too.",
    ], font("r", 40))
    slides.append(im)

    im, d = base(5, total)
    d.text((70, 120), "FREE FOR EVERYONE", font=font("b", 30), fill=RUST)
    block(d, 70, 170, "Start with the free first week.", font("i", 50), INK)
    page = Image.open(a.free_page).convert("RGB")
    # show only the filled part of the free page, large enough to read on a phone
    pw0, ph0 = page.size
    page = page.crop((int(pw0 * 0.08), int(ph0 * 0.06), int(pw0 * 0.92), int(ph0 * 0.46)))
    pw = 900
    ph = int(page.height * pw / page.width)
    page = page.resize((pw, ph), Image.LANCZOS)
    x0, y0 = (W - pw) // 2, 290
    d.rectangle([x0 + 10, y0 + 10, x0 + pw + 10, y0 + ph + 10], fill=SHADOW)
    im.paste(page, (x0, y0))
    d.rectangle([x0, y0, x0 + pw, y0 + ph], outline=GREY, width=1)
    block(d, 70, y0 + ph + 50, "One small thing a day for seven days. Free for everyone at the link in my bio.", font("r", 38), INK)
    slides.append(im)

    im, d = base(6, total)
    d.text((70, 300), "LAUNCH PRICE", font=font("b", 30), fill=RUST)
    y = block(d, 70, 360, "$10 until the clocks go back on 25 October.", font("b", 76), GREEN, gap=1.18)
    y = block(d, 70, y + 30, "Then $13. The free first week and the full plan are at the link in my bio.", font("r", 40), INK)
    y = block(d, 70, y + 40, "Ad · my own product. Not medical advice. Ilma is an AI-generated character; the places are real.", font("r", 32), GREY)
    slides.append(im)

    os.makedirs(a.out, exist_ok=True)
    for i, s in enumerate(slides, 1):
        s.save(os.path.join(a.out, f"2026-10-05_carousel_launch_slide_{i:02d}.jpg"), quality=92)
    print("built", len(slides))


if __name__ == "__main__":
    main()
