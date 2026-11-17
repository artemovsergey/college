#!/usr/bin/env python3
"""Рендерер презентации: presentations/*.md -> PPTX (+ PDF через LibreOffice)."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Pt, Inches
except ImportError:
    print("ERROR: python-pptx не установлен. pip install python-pptx", file=sys.stderr)
    sys.exit(2)

NAVY = RGBColor(0x1F, 0x38, 0x64)
ACCENT = RGBColor(0x2E, 0x5C, 0x8A)
CODE_BG = RGBColor(0xF2, 0xF2, 0xF2)


def split_slides(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"\n---\n", text) if s.strip()]


def parse_slide(raw: str) -> dict:
    title = None
    bullets: list[str] = []
    code_blocks: list[tuple[str, str]] = []
    notes = None
    in_code = False
    lang = ""
    buf: list[str] = []
    for line in raw.splitlines():
        if line.startswith("```"):
            if in_code:
                code_blocks.append((lang, "\n".join(buf)))
                buf = []
                in_code = False
            else:
                in_code = True
                lang = line[3:].strip()
            continue
        if in_code:
            buf.append(line)
            continue
        m = re.match(r"^#{1,2}\s+(.*)", line)
        if m:
            if title is None:
                title = m.group(1).strip()
            continue
        m = re.search(r"<!--\s*notes:\s*(.*?)\s*-->", line)
        if m:
            notes = m.group(1).strip()
            continue
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        if s.startswith(("-", "*")):
            bullets.append(s[1:].strip())
        else:
            bullets.append(s)
    if in_code and buf:
        code_blocks.append((lang, "\n".join(buf)))
    return {"title": title or "Без заголовка", "bullets": bullets,
            "code": code_blocks, "notes": notes}


def add_title_slide(prs, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    if subtitle and len(slide.placeholders) > 1:
        slide.placeholders[1].text = subtitle
    return slide


def add_content_slide(prs, data: dict):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = data["title"]
    tf = slide.placeholders[1].text_frame
    tf.clear()
    for i, b in enumerate(data["bullets"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = b
        p.font.size = Pt(18)
    # code blocks as separate text boxes
    for lang, code in data["code"]:
        left = Inches(0.5)
        top = Inches(4.2)
        width = Inches(9.0)
        height = Inches(2.0)
        box = slide.shapes.add_textbox(left, top, width, height)
        tfr = box.text_frame
        tfr.clear()
        p = tfr.paragraphs[0]
        run = p.add_run()
        run.text = code
        run.font.name = "Consolas"
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        box.fill.solid()
        box.fill.fore_color.rgb = CODE_BG
    if data["notes"]:
        slide.notes_slide.notes_text_frame.text = data["notes"]
    return slide


def render_deck(md_path: Path, out_dir: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    slides = split_slides(text)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    data_list = [parse_slide(s) for s in slides]
    # first slide as title if it has no bullets/code
    first = data_list[0]
    if not first["bullets"] and not first["code"]:
        add_title_slide(prs, first["title"], "")
        rest = data_list[1:]
    else:
        rest = data_list
    for d in rest:
        add_content_slide(prs, d)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (md_path.stem + ".pptx")
    prs.save(out_path)
    return out_path


def to_pdf(pptx: Path, out_dir: Path) -> Path | None:
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
        )
    except Exception:
        return None
    pdf = out_dir / (pptx.stem + ".pdf")
    return pdf if pdf.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Markdown-колода или каталог")
    ap.add_argument("--out", default="dist/presentations", help="Каталог вывода")
    args = ap.parse_args()
    inp = Path(args.input)
    out = Path(args.out)
    files = [inp] if inp.is_file() else sorted(inp.rglob("presentation-*.md"))
    if not files:
        print("ERROR: не найдены файлы презентации", file=sys.stderr)
        sys.exit(1)
    for md in files:
        pptx = render_deck(md, out)
        print(f"PPTX: {pptx}")
        pdf = to_pdf(pptx, out)
        if pdf:
            print(f"PDF:  {pdf}")
        else:
            print("PDF:  soffice недоступен, пропущено")


if __name__ == "__main__":
    main()
PY