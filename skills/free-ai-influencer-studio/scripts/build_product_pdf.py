#!/usr/bin/env python3
"""Build a styled, sellable product PDF from spec.json and audit it.

Usage:
    python build_product_pdf.py spec.json --out product.pdf [--audit audit.json] [--thumbs thumbs_dir]
        [--pagesize A4|LETTER]

Spec format: see references/product.md section 6.
Design: serif type, generous margins, thin page frame, paper colour, running footer
"TITLE · NAME" with page numbers, a cover, an auto contents page with page numbers taken
from the real build, one unit per page, drawn checkboxes (no unicode tick glyphs),
fill-in lines, tables with repeated headers and header-fit checks.
Audit: glyph coverage, table header fit, units spilling past one page, near-empty
pages (needs pdftotext), contents entries vs real pages, optional PNG thumbnails
(needs pdftoppm). Exit 0 if the audit has no failures.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).resolve().parent
FONT_DIRS = [HERE.parent / "assets" / "fonts", Path("/usr/share/fonts/truetype/dejavu"),
             Path("C:/Windows/Fonts"), Path("/Library/Fonts")]
FONT_FILES = {"regular": "DejaVuSerif.ttf", "bold": "DejaVuSerif-Bold.ttf", "italic": "DejaVuSerif-Italic.ttf"}

AUDIT = {"fails": [], "warnings": [], "info": {}}


# ---------- fonts and text ----------
def register_fonts():
    for d in FONT_DIRS:
        paths = {k: d / v for k, v in FONT_FILES.items()}
        if all(p.exists() for p in paths.values()):
            pdfmetrics.registerFont(TTFont("Body", str(paths["regular"])))
            pdfmetrics.registerFont(TTFont("Body-Bold", str(paths["bold"])))
            pdfmetrics.registerFont(TTFont("Body-Italic", str(paths["italic"])))
            pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold",
                                          italic="Body-Italic", boldItalic="Body-Bold")
            AUDIT["info"]["font"] = f"DejaVu Serif from {d}"
            return "Body", "Body-Bold", "Body-Italic", True
    AUDIT["warnings"].append("DejaVu Serif not found; using Times (Windows-1252 glyphs only)")
    AUDIT["info"]["font"] = "Times"
    return "Times-Roman", "Times-Bold", "Times-Italic", False


def glyph_check(text: str, ttf: bool, where: str):
    bad = set()
    if ttf:
        face = pdfmetrics.getFont("Body").face
        cmap = getattr(face, "charToGlyph", {})
        for ch in text:
            if ch in "\n\r\t":
                continue
            if ord(ch) not in cmap:
                bad.add(ch)
    else:
        for ch in text:
            try:
                ch.encode("cp1252")
            except UnicodeEncodeError:
                bad.add(ch)
    if bad:
        AUDIT["fails"].append(f"{where}: characters the font cannot draw: {''.join(sorted(bad))!r}")


def md(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", t)
    return t.replace("\n", "<br/>")


# ---------- flowables ----------
class Marker(Flowable):
    """Zero-size flowable used to record page numbers during the build."""
    def __init__(self, kind, label):
        super().__init__()
        self.kind, self.label = kind, label
        self.width = self.height = 0

    def draw(self):
        pass


class CheckRow(Flowable):
    def __init__(self, labels, font, size, color, box=4.2 * mm, gap=5 * mm):
        super().__init__()
        self.labels, self.font, self.size, self.color, self.box, self.gap = labels, font, size, color, box, gap
        self.height = self.box + 2

    def wrap(self, aw, ah):
        self.width = aw
        widths = [self.box + 2 * mm + pdfmetrics.stringWidth(l, self.font, self.size) for l in self.labels]
        rows, x = 1, 0
        for w in widths:
            if x and x + w > aw:
                rows += 1
                x = 0
            x += w + self.gap
        self.height = rows * (self.box + 3 * mm)
        return aw, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(0.8)
        c.setFont(self.font, self.size)
        x, y = 0, self.height - self.box
        for l in self.labels:
            w = self.box + 2 * mm + pdfmetrics.stringWidth(l, self.font, self.size)
            if x and x + w > self.width:
                x = 0
                y -= self.box + 3 * mm
            c.rect(x, y, self.box, self.box, stroke=1, fill=0)
            c.setFillColor(colors.black)
            c.drawString(x + self.box + 1.5 * mm, y + 0.8 * mm, l)
            x += w + self.gap


class FillLine(Flowable):
    def __init__(self, label, font, size, color, lines=1):
        super().__init__()
        self.label, self.font, self.size, self.color, self.lines = label, font, size, color, lines

    def wrap(self, aw, ah):
        self.width = aw
        self.height = self.lines * 9 * mm
        return aw, self.height

    def draw(self):
        c = self.canv
        c.setFont(self.font, self.size)
        c.setFillColor(colors.black)
        lw = pdfmetrics.stringWidth(self.label, self.font, self.size)
        c.setStrokeColor(self.color)
        c.setLineWidth(0.6)
        for i in range(self.lines):
            y = self.height - (i + 1) * 9 * mm + 2 * mm
            if i == 0:
                c.drawString(0, y + 1, self.label)
                c.line(lw + 2 * mm, y, self.width, y)
            else:
                c.line(0, y, self.width, y)


class ProgressBar(Flowable):
    def __init__(self, done, total, fg, bg, height=2.2 * mm):
        super().__init__()
        self.done, self.total, self.fg, self.bg, self.h = done, total, fg, bg, height

    def wrap(self, aw, ah):
        self.width = min(aw, 60 * mm)
        return self.width, self.h + 2 * mm

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.h, stroke=0, fill=1)
        c.setFillColor(self.fg)
        c.rect(0, 0, self.width * self.done / max(self.total, 1), self.h, stroke=0, fill=1)


# ---------- document ----------
class ProductDoc(BaseDocTemplate):
    def __init__(self, *a, **k):
        self.records = []
        super().__init__(*a, **k)

    def beforeDocument(self):
        self.records = []

    def afterFlowable(self, f):
        if isinstance(f, Marker):
            self.records.append((f.kind, f.label, self.page))
        elif isinstance(f, Paragraph) and getattr(f, "toc_level", None) is not None:
            text = f.getPlainText()
            self.notify("TOCEntry", (f.toc_level, text, self.page))
            self.records.append(("toc", text, self.page))


def build(spec: dict, out: str, pagesize):
    body_font, bold_font, ital_font, ttf = register_fonts()
    pal = {"ink": "#1F2A2E", "primary": "#3E5641", "accent": "#C8612B", "paper": "#FBF8F2", "muted": "#6B7780"}
    pal.update(spec.get("palette", {}))
    C = {k: colors.HexColor(v) for k, v in pal.items()}

    all_text = json.dumps(spec, ensure_ascii=False)
    glyph_check(re.sub(r'"(type|palette|cover_image|progress|page_break_before)"', "", all_text), ttf, "spec")
    if spec.get("forbid_em_dash") and "\u2014" in all_text:
        AUDIT["fails"].append("spec contains em dashes but forbid_em_dash is set")

    W, H = pagesize
    margin = 22 * mm
    ss = {
        "title": ParagraphStyle("title", fontName=bold_font, fontSize=34, leading=40, textColor=C["primary"], alignment=TA_LEFT),
        "subtitle": ParagraphStyle("subtitle", fontName=ital_font, fontSize=14, leading=19, textColor=C["ink"]),
        "promise": ParagraphStyle("promise", fontName=bold_font, fontSize=15, leading=21, textColor=C["accent"]),
        "byline": ParagraphStyle("byline", fontName=body_font, fontSize=11, leading=15, textColor=C["muted"]),
        "h1": ParagraphStyle("h1", fontName=bold_font, fontSize=20, leading=25, textColor=C["primary"], spaceBefore=10, spaceAfter=8),
        "kicker": ParagraphStyle("kicker", fontName=bold_font, fontSize=9, leading=12, textColor=C["muted"]),
        "rule": ParagraphStyle("rule", fontName=ital_font, fontSize=13, leading=18, textColor=C["accent"], spaceAfter=8),
        "body": ParagraphStyle("body", fontName=body_font, fontSize=10.5, leading=15.5, textColor=C["ink"], spaceAfter=7),
        "small": ParagraphStyle("small", fontName=body_font, fontSize=9, leading=13, textColor=C["ink"], spaceAfter=6),
        "cell": ParagraphStyle("cell", fontName=body_font, fontSize=8.8, leading=11.5, textColor=C["ink"]),
        "cellh": ParagraphStyle("cellh", fontName=bold_font, fontSize=8.8, leading=11.5, textColor=colors.white),
        "signoff": ParagraphStyle("signoff", fontName=ital_font, fontSize=12, leading=17, textColor=C["accent"], spaceBefore=6),
        "divider": ParagraphStyle("divider", fontName=bold_font, fontSize=28, leading=34, textColor=C["primary"], alignment=TA_LEFT),
        "center": ParagraphStyle("center", fontName=body_font, fontSize=10, leading=14, alignment=TA_CENTER, textColor=C["muted"]),
    }
    footer = spec.get("footer", spec.get("title", "").upper())

    def paper(c):
        c.saveState()
        c.setFillColor(C["paper"])
        c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setStrokeColor(C["primary"])
        c.setLineWidth(0.6)
        c.rect(10 * mm, 10 * mm, W - 20 * mm, H - 20 * mm, stroke=1, fill=0)
        c.restoreState()

    def on_cover(c, d):
        paper(c)

    def on_body(c, d):
        paper(c)
        c.saveState()
        c.setFont(body_font, 8)
        c.setFillColor(C["muted"])
        c.drawString(margin, 14 * mm, footer)
        c.drawRightString(W - margin, 14 * mm, str(d.page))
        c.restoreState()

    doc = ProductDoc(out, pagesize=pagesize, leftMargin=margin, rightMargin=margin,
                     topMargin=margin, bottomMargin=24 * mm, title=spec.get("title", ""),
                     author=spec.get("byline", ""))
    frame = Frame(margin, 24 * mm, W - 2 * margin, H - margin - 24 * mm, id="f")
    doc.addPageTemplates([PageTemplate("cover", [frame], onPage=on_cover),
                          PageTemplate("body", [frame], onPage=on_body)])
    aw = W - 2 * margin

    story = [Spacer(1, 40 * mm)]
    story.append(Paragraph(md(spec.get("title", "")), ss["title"]))
    story.append(Spacer(1, 6 * mm))
    if spec.get("subtitle"):
        story.append(Paragraph(md(spec["subtitle"]), ss["subtitle"]))
    story.append(Spacer(1, 12 * mm))
    if spec.get("promise"):
        story.append(Paragraph(md(spec["promise"]), ss["promise"]))
    img = spec.get("cover_image")
    if img and Path(img).exists():
        from reportlab.platypus import Image
        im = Image(img)
        ratio = im.imageHeight / im.imageWidth
        max_h = 85 * mm
        w = min(aw * 0.6, max_h / ratio)
        im.drawWidth, im.drawHeight = w, w * ratio
        im.hAlign = "LEFT"
        story += [Spacer(1, 8 * mm), im]
    elif img:
        AUDIT["warnings"].append(f"cover_image not found: {img}")
    else:
        AUDIT["warnings"].append("no cover portrait; the typographic cover ships, the portrait is the next upgrade")
    story.append(Spacer(1, 14 * mm))
    if spec.get("catchphrase"):
        story.append(Paragraph(md(spec["catchphrase"]), ss["signoff"]))
    if spec.get("byline"):
        story.append(Paragraph(md(spec["byline"]), ss["byline"]))
    story += [NextPageTemplate("body"), PageBreak()]

    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("toc1", fontName=body_font, fontSize=10.5, leading=14, textColor=C["ink"])]
    toc.dotsMinLevel = 0
    story += [Paragraph("Contents", ss["h1"]), Spacer(1, 4 * mm), toc, PageBreak()]

    def heading(text, style="h1"):
        p = Paragraph(md(text), ss[style])
        p.toc_level = 0
        return p

    def make_table(tbl, where):
        header = tbl["header"]
        rows = tbl.get("rows", [])
        pad = 14  # 6 pt cell padding each side plus a little air
        plain = lambda x: re.sub(r"[*_]", "", str(x))
        def col(i):
            return [plain(r[i]) for r in rows if i < len(r)]
        # a column can never be narrower than its header or its longest unbreakable word
        need = []
        for i, h in enumerate(header):
            words = [w for c in col(i) for w in c.split()] or [""]
            longest = max(pdfmetrics.stringWidth(w, body_font, 8.8) for w in words)
            need.append(max(pdfmetrics.stringWidth(plain(h), bold_font, 8.8), longest) + pad)
        lens = [max([len(plain(h))] + [len(c) for c in col(i)]) for i, h in enumerate(header)]
        spare = aw - sum(need)
        if spare < 0:
            AUDIT["fails"].append(f"{where}: headers or single words need {sum(need):.0f} pt but only {aw:.0f} pt available; shorten them or drop a column")
            widths = [aw / len(header)] * len(header)
        else:
            tot = sum(lens) or 1
            widths = [n + spare * l / tot for n, l in zip(need, lens)]
        data = [[Paragraph(md(h), ss["cellh"]) for h in header]]
        for r in rows:
            data.append([Paragraph(md(str(c)), ss["cell"]) for c in r] + [""] * (len(header) - len(r)))
        rh = tbl.get("row_height")
        heights = [None] + [rh] * (len(data) - 1) if rh else None
        t = Table(data, colWidths=widths, repeatRows=1, rowHeights=heights)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C["primary"]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, C["muted"]),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C["paper"]]),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    for i, s in enumerate(spec.get("sections", [])):
        kind = s.get("type", "text")
        title = s.get("title", "")
        where = f"section {i + 1} ({kind}: {title})"
        if s.get("page_break_before") or kind in ("unit", "divider") and i > 0:
            story.append(PageBreak())
        if kind == "divider":
            story += [Marker("divider", title), Spacer(1, 60 * mm), heading(title, "divider"), Spacer(1, 6 * mm)]
            if s.get("line"):
                story.append(Paragraph(md(s["line"]), ss["subtitle"]))
            else:
                AUDIT["fails"].append(f"{where}: divider without a line of copy")
            story.append(PageBreak())
            continue
        if kind == "unit":
            story.append(Marker("unit_start", title))
            prog = s.get("progress")
            if prog:
                story += [Paragraph(f"{s.get('progress_label', 'PART')} {prog[0]} OF {prog[1]}", ss["kicker"]),
                          ProgressBar(prog[0], prog[1], C["accent"], colors.HexColor("#DDD6CA")), Spacer(1, 3 * mm)]
        story.append(heading(title) if title else Spacer(1, 1))
        if s.get("rule"):
            story.append(Paragraph(md(s["rule"]), ss["rule"]))
        style = ss["small"] if kind == "smallprint" else ss["body"]
        for para in s.get("paragraphs", []):
            story.append(Paragraph(md(para), style))
        if kind == "letter" and s.get("signoff"):
            story.append(Paragraph(md(s["signoff"]), ss["signoff"]))
        if kind == "scorecard":
            measures = s.get("measures", [])
            data = {"header": ["Measure", "Start /10", "End /10"], "rows": [[m, "", ""] for m in measures]}
            story += [make_table(data, where), Spacer(1, 5 * mm)]
            if s.get("future_line"):
                story.append(FillLine(s["future_line"], body_font, 10, C["muted"], lines=3))
        if s.get("table"):
            story += [Spacer(1, 2 * mm), make_table(s["table"], where), Spacer(1, 4 * mm)]
        if kind == "checklist":
            for item in s.get("items", []):
                story.append(CheckRow([item], body_font, 10, C["primary"]))
        if s.get("checkboxes"):
            story += [Paragraph("Done:", ss["kicker"]), Spacer(1, 1.5 * mm),
                      CheckRow(s["checkboxes"], body_font, 9.5, C["primary"]), Spacer(1, 3 * mm)]
        for fl in s.get("fill_lines", []):
            story.append(FillLine(fl, body_font, 10, C["muted"], lines=int(s.get("fill_line_count", 2))))
        if kind == "unit":
            story.append(Marker("unit_end", title))

    doc.multiBuild(story)
    return doc


def audit_pdf(doc, out: str, thumbs: str | None):
    recs = doc.records
    AUDIT["info"]["contents"] = [(t, p) for k, t, p in recs if k == "toc"]
    starts = {t: p for k, t, p in recs if k == "unit_start"}
    ends = {t: p for k, t, p in recs if k == "unit_end"}
    for t, p in starts.items():
        e = ends.get(t, p)
        if e != p:
            AUDIT["fails"].append(f"unit '{t}' spills from page {p} to {e}; trim it to one page")
    dividers = {p for k, t, p in recs if k == "divider"}
    if shutil.which("pdftotext") and shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", out], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", info)
        n = int(m.group(1)) if m else 0
        AUDIT["info"]["pages"] = n
        for pg in range(3, n + 1):
            if pg in dividers:
                continue
            txt = subprocess.run(["pdftotext", "-f", str(pg), "-l", str(pg), "-layout", out, "-"],
                                 capture_output=True, text=True).stdout
            body = re.sub(r"\s+", " ", txt).strip()
            body = body.replace(str(pg), "").strip()
            if len(body) < 120:
                AUDIT["warnings"].append(f"page {pg} looks near-empty ({len(body)} characters)")
        first_body = min([p for k, t, p in recs if k == "toc"] or [3])
        toc_txt = subprocess.run(["pdftotext", "-f", "2", "-l", str(max(2, first_body - 1)), "-layout", out, "-"],
                                 capture_output=True, text=True).stdout
        if first_body > 3:
            AUDIT["warnings"].append(f"contents runs over {first_body - 2} pages; consider fewer section titles")
        toc_lines = [re.sub(r"\s+", " ", ln).strip() for ln in toc_txt.splitlines()]
        for title, page in AUDIT["info"]["contents"]:
            short = re.sub(r"\s+", " ", title).strip()[:22]
            line = next((ln for ln in toc_lines if ln.startswith(short)), "")
            nums = re.findall(r"(\d+)\s*$", line.strip())
            if not nums:
                AUDIT["warnings"].append(f"contents: could not locate '{short}' on the contents page")
            elif int(nums[-1]) != page:
                AUDIT["fails"].append(f"contents says '{short}' is on p{nums[-1]} but it is on p{page}")
    else:
        AUDIT["warnings"].append("pdftotext/pdfinfo not found; near-empty and contents checks skipped")
    if thumbs:
        if shutil.which("pdftoppm"):
            Path(thumbs).mkdir(parents=True, exist_ok=True)
            subprocess.run(["pdftoppm", "-png", "-r", "45", out, str(Path(thumbs) / "page")], check=False)
            AUDIT["info"]["thumbs"] = str(thumbs)
        else:
            AUDIT["warnings"].append("pdftoppm not found; thumbnails skipped")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit")
    ap.add_argument("--thumbs")
    ap.add_argument("--pagesize", choices=["A4", "LETTER"], default="A4")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    doc = build(spec, args.out, A4 if args.pagesize == "A4" else LETTER)
    audit_pdf(doc, args.out, args.thumbs)
    AUDIT["ok"] = not AUDIT["fails"]
    AUDIT["out"] = args.out
    txt = json.dumps(AUDIT, indent=2, ensure_ascii=False)
    print(txt)
    if args.audit:
        Path(args.audit).write_text(txt, encoding="utf-8")
    return 0 if AUDIT["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
