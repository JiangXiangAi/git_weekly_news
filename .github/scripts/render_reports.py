from pathlib import Path
import re, html
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

ROOT = Path(".")
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
pdfmetrics.registerFont(TTFont("NotoCJK", FONT_PATH, subfontIndex=0))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CJKTitle", parent=styles["Title"], fontName="NotoCJK", fontSize=19, leading=26, textColor=colors.HexColor("#16324F"), spaceAfter=14))
styles.add(ParagraphStyle(name="CJKH1", parent=styles["Heading1"], fontName="NotoCJK", fontSize=15, leading=21, spaceBefore=12, spaceAfter=8))
styles.add(ParagraphStyle(name="CJKH2", parent=styles["Heading2"], fontName="NotoCJK", fontSize=12, leading=18, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name="CJKBody", parent=styles["BodyText"], fontName="NotoCJK", fontSize=9.2, leading=14, alignment=TA_LEFT, spaceAfter=5, wordWrap="CJK"))
styles.add(ParagraphStyle(name="CJKSmall", parent=styles["BodyText"], fontName="NotoCJK", fontSize=8, leading=11, textColor=colors.HexColor("#555555"), spaceAfter=4, wordWrap="CJK"))

def inline_markup(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#1769aa"><u>\1</u></link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    return text

def render(md_path):
    raw = md_path.read_text(encoding="utf-8")
    out = md_path.with_suffix(".pdf")
    doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title=md_path.stem)
    story = []
    in_code = False
    list_items = []
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith(chr(96)*3):
            in_code = not in_code
            continue
        if in_code:
            story.append(Paragraph(inline_markup(s), styles["CJKSmall"]))
            continue
        if not s:
            if list_items:
                story.extend(list_items)
                list_items = []
            story.append(Spacer(1, 2))
            continue
        if s.startswith("|"):
            story.append(Paragraph(inline_markup(s.replace("|", "   │   ")), styles["CJKSmall"]))
        elif s.startswith("# "):
            story.append(Paragraph(inline_markup(s[2:]), styles["CJKTitle"]))
        elif s.startswith("## "):
            story.append(Paragraph(inline_markup(s[3:]), styles["CJKH1"]))
        elif s.startswith("### "):
            story.append(Paragraph(inline_markup(s[4:]), styles["CJKH2"]))
        elif s.startswith(">"):
            story.append(Paragraph(inline_markup(s.lstrip("> ")), styles["CJKSmall"]))
        elif re.match(r"^[-*] ", s):
            list_items.append(Paragraph("• " + inline_markup(s[2:]), styles["CJKBody"]))
        elif re.match(r"^\d+\. ", s):
            list_items.append(Paragraph(inline_markup(s), styles["CJKBody"]))
        elif s == "---":
            story.append(Spacer(1, 4))
        else:
            if list_items:
                story.extend(list_items)
                list_items = []
            story.append(Paragraph(inline_markup(s), styles["CJKBody"]))
    if list_items:
        story.extend(list_items)
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("NotoCJK", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(18*mm, 10*mm, "Git Weekly News · 2026 年第 41 周")
        canvas.drawRightString(A4[0]-18*mm, 10*mm, str(document.page))
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Rendered", out)

for md in sorted(ROOT.glob("2026/2026-10-05_2026-10-11/*.md")):
    if md.name != "README.md":
        render(md)
