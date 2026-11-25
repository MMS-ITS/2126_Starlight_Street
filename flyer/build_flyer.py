#!/usr/bin/env python3
"""Build the 2126 Starlight Street print flyer and browser-readable source.

The PDF uses original downloaded/uploaded image files without cropping, filters,
retouching, or overlays. Interior images are identified as artistic impressions.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable, Sequence

import cairosvg
import pymupdf as fitz
from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
PDF_OUT = HERE / "2126-Starlight-Street-Flyer.pdf"
HTML_OUT = HERE / "2126-Starlight-Street-Flyer.html"

PAGE_W, PAGE_H = letter
PAGE_COUNT = 18
DATE_DISPLAY = "25 NOVEMBER 2026"
DATE_LONG = "25 November 2026"
ADDRESS = "2126 Starlight Street | Angleton, TX 77515"
MLS = "MLS 62207090"

NAVY = HexColor("#062F38")
DEEP = HexColor("#041F26")
TEAL = HexColor("#00A6A6")
TEAL_DARK = HexColor("#007C7C")
MINT = HexColor("#CFF5EC")
PALE = HexColor("#EAF8F5")
CREAM = HexColor("#F7F1E7")
CORAL = HexColor("#FF6655")
GOLD = HexColor("#F2C14E")
INK = HexColor("#102A2E")
MID = HexColor("#4E6468")
LINE = HexColor("#BBDAD4")
WHITE = white

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_OBLIQUE = "Helvetica-Oblique"

PARA_BODY = ParagraphStyle(
    "body",
    fontName=FONT,
    fontSize=9.4,
    leading=13.2,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=0,
)
PARA_SMALL = ParagraphStyle(
    "small",
    fontName=FONT,
    fontSize=7.6,
    leading=10.4,
    textColor=MID,
    alignment=TA_LEFT,
    spaceAfter=0,
)
PARA_WHITE = ParagraphStyle(
    "white",
    fontName=FONT,
    fontSize=9.4,
    leading=13.2,
    textColor=WHITE,
    alignment=TA_LEFT,
    spaceAfter=0,
)
PARA_WHITE_SMALL = ParagraphStyle(
    "white-small",
    fontName=FONT,
    fontSize=7.6,
    leading=10.4,
    textColor=WHITE,
    alignment=TA_LEFT,
    spaceAfter=0,
)
PARA_CENTER = ParagraphStyle(
    "center",
    fontName=FONT,
    fontSize=8.4,
    leading=11.2,
    textColor=INK,
    alignment=TA_CENTER,
    spaceAfter=0,
)


def p(text: str) -> Path:
    return ASSETS / text


UPLOADED_FRONT = ROOT / "preview.webp"
UPLOADED_FIRST = ROOT / "preview (2).webp"
UPLOADED_SECOND = ROOT / "preview (1).webp"
UPLOADED_COMMUNITY_MAP = ROOT / "preview (3).webp"
VECTOR_MAP_PDF = ROOT / "Windrose Map Starlight Street.pdf"


def preprocess() -> None:
    """Create print-ready derivatives while retaining every original file."""
    for svg_name, png_name in (
        ("lennar-canon-first-floor.svg", "lennar-canon-first-floor.png"),
        ("lennar-canon-second-floor.svg", "lennar-canon-second-floor.png"),
    ):
        svg = p(svg_name)
        png = p(png_name)
        if not png.exists() or png.stat().st_mtime < svg.stat().st_mtime:
            cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=1800)

    map_png = p("windrose-map.png")
    if not map_png.exists() or map_png.stat().st_mtime < VECTOR_MAP_PDF.stat().st_mtime:
        doc = fitz.open(VECTOR_MAP_PDF)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
        pix.save(map_png)
        doc.close()


def paragraph(
    c: canvas.Canvas,
    text: str,
    x: float,
    top: float,
    width: float,
    style: ParagraphStyle = PARA_BODY,
    max_height: float = 1000,
) -> float:
    flow = Paragraph(text, style)
    _, height = flow.wrap(width, max_height)
    flow.drawOn(c, x, top - height)
    return top - height


def rounded_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill=WHITE,
    stroke=LINE,
    radius: float = 12,
    line_width: float = 0.8,
) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(line_width)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)


def draw_image_contain(
    c: canvas.Canvas,
    image_path: Path,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    background=WHITE,
    stroke=LINE,
    radius: float = 8,
    inset: float = 4,
) -> None:
    """Draw a whole image inside a box. Nothing is cropped or retouched."""
    rounded_card(c, x, y, width, height, fill=background, stroke=stroke, radius=radius)
    with Image.open(image_path) as image:
        source_w, source_h = image.size
    inner_w = width - 2 * inset
    inner_h = height - 2 * inset
    scale = min(inner_w / source_w, inner_h / source_h)
    draw_w = source_w * scale
    draw_h = source_h * scale
    draw_x = x + (width - draw_w) / 2
    draw_y = y + (height - draw_h) / 2
    c.drawImage(
        ImageReader(str(image_path)),
        draw_x,
        draw_y,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )


def small_caps(c: canvas.Canvas, text: str, x: float, y: float, color=TEAL, size: float = 8.5) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD, size)
    c.drawString(x, y, text.upper())


def section_title(
    c: canvas.Canvas,
    title: str,
    subtitle: str,
    *,
    dark: bool = False,
    kicker: str = "2126 STARLIGHT STREET",
) -> None:
    color = WHITE if dark else NAVY
    small_caps(c, kicker, 34, 754, color=GOLD if dark else TEAL)
    c.setFillColor(color)
    c.setFont(FONT_BOLD, 25)
    c.drawString(34, 718, title)
    c.setFont(FONT, 9.4)
    c.setFillColor(MINT if dark else MID)
    c.drawString(34, 700, subtitle)
    c.setStrokeColor(TEAL if not dark else GOLD)
    c.setLineWidth(2.2)
    c.line(34, 688, 578, 688)


def footer(c: canvas.Canvas, page_number: int, *, dark: bool = False) -> None:
    color = MINT if dark else MID
    c.setStrokeColor(HexColor("#28535B") if dark else LINE)
    c.setLineWidth(0.6)
    c.line(34, 34, 578, 34)
    c.setFillColor(color)
    c.setFont(FONT, 6.9)
    c.drawString(34, 20, f"{ADDRESS}  |  {MLS}  |  PREPARED {DATE_DISPLAY}")
    page_text = f"PAGE {page_number:02d} / {PAGE_COUNT:02d}"
    c.setFont(FONT_BOLD, 6.9)
    c.drawRightString(578, 20, page_text)


def label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill=TEAL, color=WHITE) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, 18, 7, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont(FONT_BOLD, 7.2)
    c.drawCentredString(x + width / 2, y + 5.4, text.upper())


def metric(c: canvas.Canvas, x: float, y: float, width: float, value: str, name: str, *, dark: bool = False) -> None:
    c.setFillColor(WHITE if dark else NAVY)
    c.setFont(FONT_BOLD, 18)
    c.drawCentredString(x + width / 2, y + 22, value)
    c.setFillColor(MINT if dark else MID)
    c.setFont(FONT_BOLD, 6.8)
    c.drawCentredString(x + width / 2, y + 8, name.upper())


def info_block(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    body: str,
    *,
    fill=WHITE,
    title_color=TEAL_DARK,
    body_style: ParagraphStyle = PARA_BODY,
) -> None:
    rounded_card(c, x, y, width, height, fill=fill, stroke=LINE)
    small_caps(c, title, x + 14, y + height - 22, color=title_color, size=7.8)
    paragraph(c, body, x + 14, y + height - 34, width - 28, body_style, max_height=height - 45)


def artwork_ribbon(c: canvas.Canvas, detail: str) -> None:
    c.setFillColor(NAVY)
    c.roundRect(34, 646, 544, 29, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 7.5)
    c.drawString(46, 657, "CANON PLAN ARTISTIC IMPRESSIONS")
    c.setFillColor(GOLD)
    c.drawRightString(566, 657, detail.upper())


def image_tile(
    c: canvas.Canvas,
    image: str,
    caption: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    draw_image_contain(c, p(image), x, y + 15, width, height - 15, background=WHITE, stroke=LINE, radius=7, inset=3)
    c.setFillColor(MID)
    c.setFont(FONT_BOLD, 6.7)
    c.drawString(x + 2, y + 3.5, caption.upper())


def cover(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, 748, PAGE_W, 44, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 7.8)
    c.drawString(34, 766, f"PROPERTY + COMMUNITY EDITION   |   {DATE_DISPLAY}")
    c.drawRightString(578, 766, MLS)

    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 48)
    c.drawString(34, 688, "2126")
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 22)
    c.drawString(34, 657, "STARLIGHT STREET")
    c.setFont(FONT, 10.5)
    c.setFillColor(MINT)
    c.drawString(34, 638, "ANGLETON, TEXAS 77515")

    draw_image_contain(c, UPLOADED_FRONT, 34, 270, 334, 348, background=WHITE, stroke=TEAL, radius=10, inset=4)
    label(c, "Actual supplied front photograph", 49, 282, 220, fill=TEAL_DARK)

    draw_image_contain(c, UPLOADED_FIRST, 382, 448, 196, 170, background=WHITE, stroke=GOLD, radius=10, inset=5)
    label(c, "First floor", 424, 457, 112, fill=CORAL)
    draw_image_contain(c, UPLOADED_SECOND, 382, 270, 196, 170, background=WHITE, stroke=GOLD, radius=10, inset=5)
    label(c, "Second floor", 424, 279, 112, fill=TEAL_DARK)

    rounded_card(c, 34, 78, 544, 168, fill=CREAM, stroke=CREAM, radius=14)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    for x in (34 + 544 / 3, 34 + 2 * 544 / 3):
        c.line(x, 92, x, 230)
    c.line(48, 160, 564, 160)
    values = [
        ("5", "BEDROOMS"),
        ("3", "FULL BATHS"),
        ("2,943", "SQ FT LIVING AREA"),
        ("2", "STORIES"),
        ("2-CAR", "ATTACHED GARAGE"),
        ("6,182", "SQ FT LOT - USER/BUILDER INFO"),
    ]
    for index, (value, name) in enumerate(values):
        col = index % 3
        row = index // 3
        metric(c, 34 + col * (544 / 3), 170 - row * 69, 544 / 3, value, name)

    c.setFillColor(MINT)
    c.setFont(FONT, 7.4)
    c.drawString(34, 52, "Lennar Canon plan 3550 | Bristol & Coastline Collections at Windrose Green")
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 7.4)
    c.drawRightString(578, 52, "INTERIOR IMAGES ARE BUILDER ARTISTIC IMPRESSIONS")
    footer(c, 1, dark=True)
    c.showPage()


def page_at_a_glance(c: canvas.Canvas) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "The home at a glance", "A property-specific front image, the builder's Canon rendering, and the verified plan profile.")

    draw_image_contain(c, p("zillow-01-actual-front.jpg"), 34, 448, 188, 222, background=WHITE, stroke=TEAL)
    label(c, "Property-specific front photo", 47, 460, 162, fill=TEAL_DARK)
    draw_image_contain(c, p("zillow-02-builder-exterior-rendering.jpg"), 236, 493, 342, 177, background=WHITE, stroke=GOLD)
    label(c, "Builder exterior rendering", 367, 505, 196, fill=CORAL)

    rounded_card(c, 236, 448, 342, 36, fill=NAVY, stroke=NAVY, radius=8)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 8.7)
    c.drawString(249, 462, "LENNAR CANON 3550")
    c.setFillColor(GOLD)
    c.drawRightString(565, 462, "5 BED | 3 BATH | 2 STORY | 2-CAR")

    cards = [
        ("2,943 SQ FT", "Builder-sourced total living area"),
        ("6,182 SQ FT LOT", "User-supplied as builder-confirmed; verify by survey"),
        ("2026", "New construction"),
        ("WINDROSE GREEN", "Bristol & Coastline Collections"),
    ]
    for i, (value, note) in enumerate(cards):
        col = i % 2
        row = i // 2
        x = 34 + col * 276
        y = 346 - row * 92
        rounded_card(c, x, y, 264, 78, fill=WHITE, stroke=LINE)
        c.setFillColor(TEAL_DARK)
        c.setFont(FONT_BOLD, 13.5)
        c.drawString(x + 14, y + 45, value)
        c.setFillColor(MID)
        c.setFont(FONT, 7.7)
        paragraph(c, note, x + 14, y + 32, 236, PARA_SMALL)

    info_block(
        c,
        34,
        95,
        544,
        128,
        "PROPERTY DESCRIPTION - PARAPHRASED",
        "The Canon's first floor places the owner's suite at the rear, Bedroom 2 near the foyer, and a separate study beside an open family, dining, and kitchen zone with access to a covered patio. Upstairs, Bedrooms 3-5 surround a large game room and shared full bath.<br/><br/><b>Floor-area split:</b> approximately 1,848 sq ft downstairs and 1,095 sq ft upstairs. These are drawing-derived estimates; only the 2,943 sq ft total is builder-sourced.",
        fill=PALE,
    )
    c.setFillColor(MID)
    c.setFont(FONT_OBLIQUE, 6.8)
    c.drawString(34, 72, "Source profile: HAR, Zillow, Lennar, and supplied floor plans. Accessed 25 November 2026.")
    footer(c, 2)
    c.showPage()


def room_line(c: canvas.Canvas, x: float, y: float, width: float, room: str, size: str) -> None:
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8.2)
    c.drawString(x, y, room)
    c.setFillColor(TEAL_DARK)
    c.drawRightString(x + width, y, size)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(x, y - 5, x + width, y - 5)


def page_first_floor(c: canvas.Canvas) -> None:
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "First-floor plan", "Owner's suite, Bedroom 2, study, open living, laundry, two full baths, garage, and patio.")
    draw_image_contain(c, p("lennar-canon-first-floor.png"), 34, 86, 344, 582, background=WHITE, stroke=TEAL, radius=12, inset=8)
    label(c, "Official Lennar vector plan", 102, 101, 208, fill=TEAL_DARK)

    rounded_card(c, 392, 86, 186, 582, fill=WHITE, stroke=LINE, radius=12)
    small_caps(c, "Approx. first-floor area", 406, 638, color=TEAL_DARK, size=7.5)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 25)
    c.drawString(406, 605, "1,848")
    c.setFont(FONT_BOLD, 8)
    c.setFillColor(CORAL)
    c.drawString(406, 589, "SQ FT - ESTIMATED")

    small_caps(c, "Published dimensions", 406, 555, color=TEAL_DARK, size=7.5)
    rows = [
        ("Owner's suite", "12' x 15'"),
        ("Bedroom 2", "11' x 11'"),
        ("Study", "11' x 11'"),
        ("Family room", "11' x 21'"),
        ("Dining", "9' x 19'"),
        ("2-car garage", "18' x 20'"),
        ("Covered patio", "21' x 5'"),
    ]
    y = 530
    for room, size in rows:
        room_line(c, 406, y, 158, room, size)
        y -= 29

    small_caps(c, "Plan highlights", 406, 304, color=TEAL_DARK, size=7.5)
    bullets = (
        "- Owner's suite and Bedroom 2 downstairs<br/>"
        "- Study/flex room beside the foyer<br/>"
        "- Kitchen open to family and dining<br/>"
        "- Interior utility room<br/>"
        "- Covered front porch and rear patio"
    )
    paragraph(c, bullets, 406, 287, 158, PARA_SMALL)
    paragraph(c, "<b>Area note:</b> The floor split is an estimate carried forward from the supplied flyer. It is not printed on the plan and is not builder-certified.", 406, 175, 158, PARA_SMALL)
    footer(c, 3)
    c.showPage()


def page_second_floor(c: canvas.Canvas) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Second-floor plan", "Three secondary bedrooms, one full bath, and a central game room.")
    draw_image_contain(c, p("lennar-canon-second-floor.png"), 34, 86, 344, 582, background=WHITE, stroke=GOLD, radius=12, inset=8)
    label(c, "Official Lennar vector plan", 102, 101, 208, fill=CORAL)

    rounded_card(c, 392, 86, 186, 582, fill=WHITE, stroke=LINE, radius=12)
    small_caps(c, "Approx. second-floor area", 406, 638, color=TEAL_DARK, size=7.5)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 25)
    c.drawString(406, 605, "1,095")
    c.setFont(FONT_BOLD, 8)
    c.setFillColor(CORAL)
    c.drawString(406, 589, "SQ FT - ESTIMATED")

    small_caps(c, "Published dimensions", 406, 555, color=TEAL_DARK, size=7.5)
    rows = [
        ("Bedroom 3", "12' x 13'"),
        ("Bedroom 4", "11' x 12'"),
        ("Bedroom 5", "14' x 11'"),
        ("Game room", "18' x 15'"),
    ]
    y = 530
    for room, size in rows:
        room_line(c, 406, y, 158, room, size)
        y -= 34

    small_caps(c, "Plan highlights", 406, 378, color=TEAL_DARK, size=7.5)
    paragraph(
        c,
        "- Three upstairs bedrooms<br/>- Shared Bath 3<br/>- Central game room<br/>- Dedicated closets<br/>- Open stair connection to the main level",
        406,
        360,
        158,
        PARA_SMALL,
    )
    info_block(
        c,
        406,
        134,
        158,
        132,
        "COMPLETE LAYOUT",
        "Together, the plans show five bedrooms, three full baths, a study, a game room, an interior laundry, a two-car garage, and covered outdoor space.",
        fill=PALE,
        body_style=PARA_SMALL,
    )
    paragraph(c, "The builder gallery does not publish separate artistic impressions for the foyer, garage, covered patio, or every closet.", 406, 118, 158, PARA_SMALL)
    footer(c, 4)
    c.showPage()


def gallery_page_five(
    c: canvas.Canvas,
    page_number: int,
    title: str,
    subtitle: str,
    detail: str,
    images: Sequence[tuple[str, str]],
    info_title: str,
    info_text: str,
) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, title, subtitle)
    artwork_ribbon(c, detail)
    top = images[:2]
    bottom = images[2:]
    for i, item in enumerate(top):
        image_tile(c, item[0], item[1], 34 + i * 276, 424, 268, 204)
    for i, item in enumerate(bottom):
        image_tile(c, item[0], item[1], 34 + i * 184, 250, 176, 158)
    info_block(c, 34, 76, 544, 150, info_title, info_text, fill=PALE)
    c.setFillColor(MID)
    c.setFont(FONT_OBLIQUE, 6.6)
    c.drawRightString(578, 57, "Builder artistic impressions; furniture, finishes, colors, windows, and selections may differ from the completed home.")
    footer(c, page_number)
    c.showPage()


def gallery_page_six(
    c: canvas.Canvas,
    page_number: int,
    title: str,
    subtitle: str,
    detail: str,
    images: Sequence[tuple[str, str]],
    info_text: str,
) -> None:
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, title, subtitle)
    artwork_ribbon(c, detail)
    for i, item in enumerate(images):
        col = i % 2
        row = i // 2
        image_tile(c, item[0], item[1], 34 + col * 276, 493 - row * 162, 268, 151)
    info_block(c, 34, 76, 544, 82, "PLAN NOTES", info_text, fill=WHITE, body_style=PARA_SMALL)
    footer(c, page_number)
    c.showPage()


def gallery_page_four(
    c: canvas.Canvas,
    page_number: int,
    title: str,
    subtitle: str,
    detail: str,
    images: Sequence[tuple[str, str]],
    left_title: str,
    left_text: str,
    right_title: str,
    right_text: str,
) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, title, subtitle)
    artwork_ribbon(c, detail)
    for i, item in enumerate(images):
        col = i % 2
        row = i // 2
        image_tile(c, item[0], item[1], 34 + col * 276, 403 - row * 195, 268, 180)
    info_block(c, 34, 76, 268, 108, left_title, left_text, fill=PALE, body_style=PARA_SMALL)
    info_block(c, 310, 76, 268, 108, right_title, right_text, fill=WHITE, body_style=PARA_SMALL)
    footer(c, page_number)
    c.showPage()


def gallery_page_three(c: canvas.Canvas) -> None:
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Laundry + secondary baths", "The complete published rendering set for the utility room, Bath 2, and Bath 3.")
    artwork_ribbon(c, "UTILITY + BATHS")
    image_tile(c, "zillow-33-laundry.jpg", "Laundry", 34, 390, 544, 238)
    image_tile(c, "zillow-34-bath-2.jpg", "Bath 2 - first floor", 34, 190, 268, 180)
    image_tile(c, "zillow-35-bath-3.jpg", "Bath 3 - second floor", 310, 190, 268, 180)
    info_block(
        c,
        34,
        76,
        544,
        90,
        "UTILITY + BATH FUNCTION",
        "The floor plans place the laundry inside the home, Bath 2 near Bedroom 2, and Bath 3 beside the upstairs bedrooms and game room. HAR lists washer connections plus both electric and gas dryer connections. Washer and dryer inclusion is builder-confirmed per owner-supplied information; the signed purchase agreement controls.",
        fill=WHITE,
        body_style=PARA_SMALL,
    )
    footer(c, 11)
    c.showPage()


def page_inclusions(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(
        c,
        "Included home package",
        "All eight items were reported by the user as confirmed by the builder for this address.",
        dark=True,
        kicker="BUILDER-CONFIRMED PER OWNER-SUPPLIED INFORMATION",
    )

    items = [
        ("01", "Refrigerator / fridge", "Plan-level public corroboration"),
        ("02", "Dishwasher", "Address-specific public corroboration"),
        ("03", "Washer + dryer", "Owner/builder confirmation"),
        ("04", "Built-in microwave", "Plan-level public corroboration"),
        ("05", "Blinds package", "Owner/builder confirmation"),
        ("06", "Storm shutters", "Owner/builder confirmation"),
        ("07", "Garage-door opener", "Plan-level public corroboration"),
        ("08", "Sprinkler system", "Plan-level public corroboration"),
    ]
    for i, (number, title, note) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 34 + col * 276
        y = 565 - row * 116
        rounded_card(c, x, y, 268, 98, fill=WHITE, stroke=TEAL, radius=12)
        c.setFillColor(TEAL)
        c.circle(x + 32, y + 49, 18, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(x + 32, y + 46, number)
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 13)
        c.drawString(x + 62, y + 56, title)
        c.setFillColor(TEAL_DARK)
        c.setFont(FONT_BOLD, 6.8)
        c.drawString(x + 62, y + 38, note.upper())
        c.setFillColor(MID)
        c.setFont(FONT, 7.2)
        c.drawString(x + 62, y + 22, "Included package - confirm final model/selection in contract")

    rounded_card(c, 34, 76, 544, 98, fill=DEEP, stroke=GOLD, radius=12)
    small_caps(c, "IMPORTANT SOURCE NOTE", 50, 147, color=GOLD, size=7.8)
    paragraph(
        c,
        "Public records independently support the dishwasher for this address. Current Canon materials also support the refrigerator, built-in microwave, garage-door opener, and front/back sprinklers at plan level. Public sources did not independently confirm the washer/dryer, blinds, or storm shutters for this address. <b>The signed purchase agreement or builder addendum is the source of record.</b>",
        50,
        132,
        512,
        PARA_WHITE_SMALL,
    )
    footer(c, 12, dark=True)
    c.showPage()


def feature_row(c: canvas.Canvas, x: float, y: float, title: str, text: str, width: float) -> float:
    c.setFillColor(TEAL)
    c.circle(x + 5, y - 3, 4, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 8.5)
    c.drawString(x + 16, y, title)
    return paragraph(c, text, x + 16, y - 11, width - 16, PARA_SMALL) - 9


def page_facts(c: canvas.Canvas) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Facts, features + construction", "Address-specific public facts are separated from current Canon plan standards.")

    draw_image_contain(c, p("zillow-02-builder-exterior-rendering.jpg"), 34, 492, 544, 176, background=WHITE, stroke=GOLD, radius=12)
    label(c, "Builder exterior rendering - not an actual photo", 280, 504, 282, fill=CORAL)

    blocks = [
        (
            34,
            "ADDRESS-SPECIFIC MLS FACTS",
            [
                ("Home", "Freestanding detached single-family residence; traditional style; 2026 new construction."),
                ("Shell", "Brick exterior, slab foundation, composition roof."),
                ("Outdoor", "Covered rear patio and fenced back yard; no private pool."),
            ],
        ),
        (
            218,
            "INTERIOR + LAYOUT",
            [
                ("Floors", "Carpet and vinyl listed by HAR."),
                ("Kitchen", "Breakfast bar; kitchen open to family room; kitchen/dining combination."),
                ("Bedrooms", "Owner's suite and Bedroom 2 down; Bedrooms 3-5 and game room up."),
            ],
        ),
        (
            402,
            "CURRENT CANON STANDARDS",
            [
                ("Kitchen", "Quartz counters, full-height backsplash, shaker cabinets, stainless gas range, undermount sink, and pantry."),
                ("Systems", "PEX plumbing, LED lighting, media enclosure, and smart thermostat."),
                ("Garage/yard", "Finished garage, overhead opener, sod, rear fence, and front/back sprinklers."),
            ],
        ),
    ]
    for x, title, items in blocks:
        rounded_card(c, x, 88, 176, 380, fill=WHITE, stroke=LINE, radius=12)
        small_caps(c, title, x + 14, 441, color=TEAL_DARK, size=7.1)
        y = 414
        for name, text in items:
            y = feature_row(c, x + 14, y, name, text, 148)

    c.setFillColor(MID)
    c.setFont(FONT_OBLIQUE, 6.5)
    c.drawString(34, 68, "Canon standards are plan-level information. Actual selections and substitutions are controlled by the purchase agreement.")
    footer(c, 13)
    c.showPage()


def page_energy(c: canvas.Canvas) -> None:
    c.setFillColor(DEEP)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Utilities, energy + green features", "Home systems and community infrastructure, with solar claims kept in their proper scope.", dark=True)

    info_block(
        c,
        34,
        390,
        260,
        278,
        "UTILITIES + CONNECTIVITY",
        "<b>Water + sewer</b><br/>Public service; official community material identifies the City of Angleton.<br/><br/><b>Electricity</b><br/>Retail provider selected through Texas Power to Choose.<br/><br/><b>Natural gas</b><br/>Community gas infrastructure; Centric is identified in community material.<br/><br/><b>Fiber</b><br/>Windrose Green advertises fiber infrastructure; official material lists AT&T and Centric.<br/><br/><b>Laundry connections</b><br/>Washer hookup plus electric and gas dryer connections.",
        fill=WHITE,
        body_style=PARA_SMALL,
    )
    info_block(
        c,
        318,
        390,
        260,
        278,
        "CURRENT CANON ENERGY STANDARDS",
        "- Energy-efficient HVAC and water heater<br/>- Multi-layer Low-E insulated windows<br/>- Polyseal envelope sealing<br/>- R-13 applicable exterior walls<br/>- R-22 applicable slopes/attic walls<br/>- R-38 applicable flat ceilings<br/>- Smart thermostat and LED lighting<br/>- Water-saving toilets<br/>- Third-party code-certified inspection",
        fill=WHITE,
        body_style=PARA_SMALL,
    )

    rounded_card(c, 34, 198, 544, 160, fill=TEAL_DARK, stroke=GOLD, radius=14)
    c.setFillColor(GOLD)
    c.circle(88, 278, 34, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 18)
    c.drawCentredString(88, 272, "SUN")
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 15)
    c.drawString(140, 306, "SOLAR-POWERED COMMUNITY STREETLIGHTS")
    paragraph(
        c,
        "Windrose Green identifies solar-powered streetlights as a community feature. That statement does <b>not</b> establish solar panels, batteries, or other on-site generation at 2126 Starlight Street.",
        140,
        286,
        410,
        PARA_WHITE,
    )

    rounded_card(c, 34, 76, 544, 92, fill=NAVY, stroke=HexColor("#28535B"), radius=12)
    small_caps(c, "VERIFY BEFORE CLOSING", 50, 142, color=GOLD, size=7.8)
    paragraph(c, "Utility providers, service territories, and builder substitutions can change. Confirm current assignments, equipment, insulation documentation, and final selections with the builder and utility providers.", 50, 127, 512, PARA_WHITE_SMALL)
    footer(c, 14, dark=True)
    c.showPage()


def page_amenities(c: canvas.Canvas) -> None:
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Windrose Green amenities", "Official community photography and currently advertised amenities.")
    tiles = [
        ("windrose-aerial.jpg", "Aerial view + community lakes"),
        ("windrose-community-amenities.jpg", "Playground"),
        ("windrose-entry-sign.jpg", "Windrose Green entrance"),
        ("windrose-picnic-pavilion.jpg", "Covered pavilion + recreation area"),
    ]
    for i, item in enumerate(tiles):
        col = i % 2
        row = i // 2
        image_tile(c, item[0], item[1], 34 + col * 276, 399 - row * 205, 268, 190)

    rounded_card(c, 34, 76, 544, 96, fill=NAVY, stroke=NAVY, radius=12)
    amenities = ["2 LAKES", "SPLASH PAD", "PLAYGROUND", "PAVILION", "ACTIVITY LAWNS", "PARKS", "WALKING TRAILS", "HIKE/BIKE TRAILS"]
    for i, item in enumerate(amenities):
        col = i % 4
        row = i // 4
        x = 49 + col * 130
        y = 133 - row * 34
        c.setFillColor(TEAL if row == 0 else GOLD)
        c.circle(x + 4, y + 2, 4, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 6.9)
        c.drawString(x + 14, y, item)
    footer(c, 15)
    c.showPage()


def page_map(c: canvas.Canvas) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Community map + surroundings", "Neighborhood orientation only. The supplied map does not clearly mark the subject homesite.")
    draw_image_contain(c, p("windrose-map.png"), 34, 273, 544, 395, background=WHITE, stroke=TEAL, radius=12, inset=7)
    label(c, "Windrose Green site map - exact lot not marked", 252, 287, 310, fill=TEAL_DARK)

    cards = [
        ("ROAD ACCESS", "Near Hwy 35 Bypass/FM 523 with access toward Hwy 288."),
        ("ANGLETON ISD", "The community is served by Angleton ISD. Confirm current attendance assignments directly."),
        ("COAST + CITIES", "Community FAQ estimates: Lake Jackson ~20 min; Surfside Beach ~25 min; Rosharon ~13 mi; Pearland ~30 mi; Houston under 50 mi."),
    ]
    for i, (title, body) in enumerate(cards):
        x = 34 + i * 184
        info_block(c, x, 76, 176, 174, title, body, fill=WHITE, body_style=PARA_SMALL)
    footer(c, 16)
    c.showPage()


def page_community(c: canvas.Canvas) -> None:
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Community + HOA profile", "Current public facts, with the management-company conflict disclosed.")

    draw_image_contain(c, p("windrose-aerial.jpg"), 34, 457, 544, 211, background=WHITE, stroke=GOLD, radius=12)
    label(c, "Official Windrose Green aerial", 370, 470, 190, fill=CORAL)

    facts = [
        ("154 ACRES", "Planned community scale stated in the current FAQ."),
        ("~648 HOMESITES", "Approximate build-out stated by the community."),
        ("MANDATORY HOA", "Windrose Green Community Association, Inc."),
        ("3 BUILDERS", "CastleRock Communities, Coventry Homes, and Lennar are currently listed."),
    ]
    for i, (title, body) in enumerate(facts):
        col = i % 2
        row = i // 2
        x = 34 + col * 276
        y = 342 - row * 106
        rounded_card(c, x, y, 268, 90, fill=WHITE, stroke=LINE, radius=11)
        c.setFillColor(TEAL_DARK)
        c.setFont(FONT_BOLD, 12.5)
        c.drawString(x + 14, y + 56, title)
        paragraph(c, body, x + 14, y + 42, 240, PARA_SMALL)

    info_block(
        c,
        34,
        76,
        544,
        136,
        "HOA + SCHOOL DUE DILIGENCE",
        "The supplied July 2026 community sheet names Preferred Management Services, while the current official community FAQ names KRJ Management. Because those sources conflict, this flyer does not publish a management contact. Confirm the current manager directly with the association.<br/><br/>The supplied sheet and the prior flyer also conflict on school names. This flyer identifies Angleton ISD only and directs readers to the district for current attendance zones.",
        fill=NAVY,
        title_color=GOLD,
        body_style=PARA_WHITE_SMALL,
    )
    footer(c, 17)
    c.showPage()


def source_link(c: canvas.Canvas, y: float, label_text: str, detail: str, url: str) -> float:
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 8.3)
    c.drawString(50, y, label_text)
    label_width = stringWidth(label_text, FONT_BOLD, 8.3)
    c.linkURL(url, (50, y - 2, 50 + label_width, y + 9), relative=0)
    paragraph(c, detail, 50, y - 9, 512, PARA_WHITE_SMALL)
    return y - 47


def page_sources(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    section_title(c, "Sources + verification notes", "Exact source pages, access date, image handling, and disputed-data labels.", dark=True)

    y = 650
    y = source_link(c, y, "HAR property record", "MLS, home configuration, 2,943 sq ft total, room dimensions, construction, utilities, and address-specific features.", "https://www.har.com/2126-starlight-st/sale_62207090")
    y = source_link(c, y, "Zillow property record", "Syndicated property description, configuration, front photograph, floor plans, and illustrative Canon gallery.", "https://www.zillow.com/homedetails/2126-Starlight-St-Angleton-TX-77515/464083448_zpid/")
    y = source_link(c, y, "Lennar Canon plan", "Plan identity, official vector floor plans, layout description, and current plan-level standards.", "https://www.lennar.com/new-homes/texas/houston/angleton/windrose-green/bristol-coastline-collections/canon")
    y = source_link(c, y, "Windrose Green amenities", "Community lakes, recreation, parks, trails, gas/fiber infrastructure, solar-powered streetlights, and official photos.", "https://www.windrosegreen.com/amenities/")
    y = source_link(c, y, "Windrose Green FAQ", "Community scale, builders, HOA context, road access, amenities, and surrounding destinations.", "https://www.windrosegreen.com/faq")

    rounded_card(c, 34, 192, 544, 222, fill=DEEP, stroke=HexColor("#28535B"), radius=12)
    small_caps(c, "SUPPLIED FILES USED", 50, 388, color=TEAL, size=7.7)
    paragraph(c, "Front photo: <b>preview.webp</b> | First floor: <b>preview (2).webp</b> | Second floor: <b>preview (1).webp</b> | Community source: <b>Community Info_WindroseGreen.pdf</b> | Site map: <b>Windrose Map Starlight Street.pdf</b> | Prior flyer challenged: <b>2126 Starlight Street - Property Flyer Claude Opus 5.5 low.pdf</b>", 50, 373, 512, PARA_WHITE_SMALL)

    small_caps(c, "VERIFICATION NOTES", 50, 315, color=GOLD, size=7.7)
    paragraph(
        c,
        "1. Lot size is shown as 6,182 sq ft because the user supplied it as builder-confirmed; public portal fields do not verify it and the prior flyer says 5,400 sq ft.<br/>2. The 1,848/1,095 sq ft floor split is an estimate; the builder-sourced total is 2,943 sq ft.<br/>3. All 31 interior images are Canon-plan artistic impressions, not actual interior photographs.<br/>4. The public gallery contains one property-specific front photograph; the second exterior image is a builder rendering.<br/>5. The purchase agreement, survey, title documents, builder addenda, and current provider/HOA confirmations control where sources differ.",
        50,
        299,
        512,
        PARA_WHITE_SMALL,
    )

    rounded_card(c, 34, 76, 544, 92, fill=TEAL_DARK, stroke=GOLD, radius=12)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 10)
    c.drawString(50, 142, "PREPARED " + DATE_DISPLAY)
    paragraph(c, "Public accessibility does not itself grant republication rights. Confirm image-use rights before distribution. Public-source text was paraphrased. Financial and listing-market details were intentionally excluded.", 50, 127, 512, PARA_WHITE_SMALL)
    footer(c, 18, dark=True)
    c.showPage()


def build_pdf() -> None:
    c = canvas.Canvas(str(PDF_OUT), pagesize=letter, pageCompression=1)
    c.setTitle("2126 Starlight Street Property and Community Flyer")
    c.setAuthor("Property research compilation")
    c.setSubject("Lennar Canon home and Windrose Green community profile, prepared 25 November 2026")
    c.setKeywords("2126 Starlight Street, Angleton, Windrose Green, Lennar Canon, MLS 62207090")

    cover(c)
    page_at_a_glance(c)
    page_first_floor(c)
    page_second_floor(c)
    gallery_page_five(
        c,
        5,
        "Family room + open living",
        "Five published views of the Canon plan's connected family, dining, and kitchen zone.",
        "FAMILY ROOM 11' x 21'",
        [
            ("zillow-05-family-1.jpg", "Family room - view 1"),
            ("zillow-06-family-2.jpg", "Family room - view 2"),
            ("zillow-07-family-3.jpg", "Open living - view 3"),
            ("zillow-08-family-4.jpg", "Open living - view 4"),
            ("zillow-09-family-5.jpg", "Open living - view 5"),
        ],
        "OPEN, CONNECTED LIVING",
        "The plan places the family room beside the dining area and island kitchen, with direct access to the covered patio. The floor plan verifies the spatial relationship; the five images show builder artistic impressions rather than this home's completed finishes.",
    )
    gallery_page_six(
        c,
        6,
        "Dining + kitchen",
        "All six published dining and kitchen impressions from the public Canon gallery.",
        "DINING 9' x 19' | KITCHEN DIMENSION NOT PUBLISHED",
        [
            ("zillow-10-dining-1.jpg", "Dining - view 1"),
            ("zillow-11-dining-2.jpg", "Dining - view 2"),
            ("zillow-12-dining-3.jpg", "Dining - view 3"),
            ("zillow-13-kitchen-1.jpg", "Kitchen - view 1"),
            ("zillow-14-kitchen-2.jpg", "Kitchen - view 2"),
            ("zillow-15-kitchen-3.jpg", "Kitchen - view 3"),
        ],
        "The current Canon specification lists quartz counters, full-height backsplash, shaker cabinetry, stainless gas range, built-in microwave, dishwasher, undermount sink, and pantry. Actual colors, appliance models, and substitutions are controlled by the purchase agreement.",
    )
    gallery_page_five(
        c,
        7,
        "Owner's suite + bath",
        "Two suite views plus the published closet and bath impressions.",
        "OWNER'S SUITE 12' x 15' | FIRST FLOOR",
        [
            ("zillow-16-owner-suite-1.jpg", "Owner's suite - view 1"),
            ("zillow-17-owner-suite-2.jpg", "Owner's suite - view 2"),
            ("zillow-18-owner-closet.jpg", "Walk-in closet"),
            ("zillow-19-owner-bath-1.jpg", "Owner's bath - shower"),
            ("zillow-20-owner-bath-2.jpg", "Owner's bath - vanity"),
        ],
        "PRIVATE FIRST-FLOOR SUITE",
        "The floor plan locates the owner's suite at the rear of the first floor with an en-suite bath and walk-in closet. HAR lists double sinks and a separate shower. Rendered finishes, fixtures, and shelving may differ.",
    )
    gallery_page_four(
        c,
        8,
        "Bedroom 2 + study",
        "The complete published impression set for the first-floor secondary bedroom and study.",
        "BEDROOM 2 11' x 11' | STUDY 11' x 11'",
        [
            ("zillow-21-bedroom-2-1.jpg", "Bedroom 2 - view 1"),
            ("zillow-22-bedroom-2-2.jpg", "Bedroom 2 - view 2"),
            ("zillow-29-study-1.jpg", "Study - view 1"),
            ("zillow-30-study-2.jpg", "Study - view 2"),
        ],
        "BEDROOM 2",
        "Located near the foyer and Bath 2, adding a second first-floor sleeping room.",
        "STUDY / FLEX",
        "A separate room off the main living area for office, reading, or flex use.",
    )
    gallery_page_four(
        c,
        9,
        "Bedrooms 3 + 4",
        "Four published Canon impressions for two of the three upstairs bedrooms.",
        "BEDROOM 3 12' x 13' | BEDROOM 4 11' x 12'",
        [
            ("zillow-23-bedroom-3-1.jpg", "Bedroom 3 - view 1"),
            ("zillow-24-bedroom-3-2.jpg", "Bedroom 3 - view 2"),
            ("zillow-25-bedroom-4-1.jpg", "Bedroom 4 - view 1"),
            ("zillow-26-bedroom-4-2.jpg", "Bedroom 4 - view 2"),
        ],
        "BEDROOM 3",
        "Upstairs bedroom arranged near the game room and shared Bath 3.",
        "BEDROOM 4",
        "Upstairs bedroom with a dedicated closet shown on the second-floor plan.",
    )
    gallery_page_four(
        c,
        10,
        "Bedroom 5 + game room",
        "The complete published impression set for Bedroom 5 and the upstairs game room.",
        "BEDROOM 5 14' x 11' | GAME ROOM 18' x 15'",
        [
            ("zillow-27-bedroom-5-1.jpg", "Bedroom 5 - view 1"),
            ("zillow-28-bedroom-5-2.jpg", "Bedroom 5 - view 2"),
            ("zillow-31-game-room-1.jpg", "Game room - view 1"),
            ("zillow-32-game-room-2.jpg", "Game room - view 2"),
        ],
        "BEDROOM 5",
        "The largest published secondary-bedroom footprint by listed dimensions.",
        "GAME ROOM",
        "A central upstairs flex space connecting Bedrooms 3-5 and Bath 3.",
    )
    gallery_page_three(c)
    page_inclusions(c)
    page_facts(c)
    page_energy(c)
    page_amenities(c)
    page_map(c)
    page_community(c)
    page_sources(c)
    c.save()


def h_image(file: str, alt: str, class_name: str = "photo") -> str:
    src = file if file.startswith("../") else f"assets/{file}"
    return f'<figure><img class="{class_name}" src="{html.escape(src)}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>'


def h_gallery(title: str, subtitle: str, detail: str, files: Sequence[tuple[str, str]], number: int, notes: str) -> str:
    figures = "".join(h_image(file, caption) for file, caption in files)
    return f"""
<section class="sheet gallery-page">
  <header><p class="eyebrow">2126 STARLIGHT STREET</p><h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p></header>
  <div class="rendering-banner"><strong>CANON PLAN ARTISTIC IMPRESSIONS</strong><span>{html.escape(detail)}</span></div>
  <div class="gallery grid-{len(files)}">{figures}</div>
  <aside class="note"><strong>Plan notes</strong><p>{html.escape(notes)}</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE {number:02d} / {PAGE_COUNT:02d}</b></footer>
</section>"""


def build_html() -> None:
    gallery_pages = [
        h_gallery(
            "Family room + open living",
            "Five published views of the connected family, dining, and kitchen zone.",
            "FAMILY ROOM 11' x 21'",
            [(f"zillow-{i:02d}-family-{i-4}.jpg", f"Family/open living view {i-4}") for i in range(5, 10)],
            5,
            "The plan places the family room beside dining and the island kitchen with access to the covered patio. Images are artistic impressions, not actual interiors.",
        ),
        h_gallery(
            "Dining + kitchen",
            "All six published dining and kitchen impressions.",
            "DINING 9' x 19' | KITCHEN SIZE NOT PUBLISHED",
            [
                ("zillow-10-dining-1.jpg", "Dining view 1"),
                ("zillow-11-dining-2.jpg", "Dining view 2"),
                ("zillow-12-dining-3.jpg", "Dining view 3"),
                ("zillow-13-kitchen-1.jpg", "Kitchen view 1"),
                ("zillow-14-kitchen-2.jpg", "Kitchen view 2"),
                ("zillow-15-kitchen-3.jpg", "Kitchen view 3"),
            ],
            6,
            "Current Canon standards list quartz counters, full-height backsplash, shaker cabinets, stainless gas range, built-in microwave, dishwasher, undermount sink, and pantry. Selections may differ.",
        ),
        h_gallery(
            "Owner's suite + bath",
            "Two suite views plus closet and bath impressions.",
            "OWNER'S SUITE 12' x 15' | FIRST FLOOR",
            [
                ("zillow-16-owner-suite-1.jpg", "Owner's suite view 1"),
                ("zillow-17-owner-suite-2.jpg", "Owner's suite view 2"),
                ("zillow-18-owner-closet.jpg", "Walk-in closet"),
                ("zillow-19-owner-bath-1.jpg", "Owner's bath shower"),
                ("zillow-20-owner-bath-2.jpg", "Owner's bath vanity"),
            ],
            7,
            "First-floor rear suite with en-suite bath and walk-in closet. HAR lists double sinks and a separate shower.",
        ),
        h_gallery(
            "Bedroom 2 + study",
            "The published first-floor secondary-bedroom and study set.",
            "BEDROOM 2 11' x 11' | STUDY 11' x 11'",
            [
                ("zillow-21-bedroom-2-1.jpg", "Bedroom 2 view 1"),
                ("zillow-22-bedroom-2-2.jpg", "Bedroom 2 view 2"),
                ("zillow-29-study-1.jpg", "Study view 1"),
                ("zillow-30-study-2.jpg", "Study view 2"),
            ],
            8,
            "Bedroom 2 sits near the foyer and Bath 2. The separate study is off the main living area.",
        ),
        h_gallery(
            "Bedrooms 3 + 4",
            "Four published impressions for two upstairs bedrooms.",
            "BEDROOM 3 12' x 13' | BEDROOM 4 11' x 12'",
            [
                ("zillow-23-bedroom-3-1.jpg", "Bedroom 3 view 1"),
                ("zillow-24-bedroom-3-2.jpg", "Bedroom 3 view 2"),
                ("zillow-25-bedroom-4-1.jpg", "Bedroom 4 view 1"),
                ("zillow-26-bedroom-4-2.jpg", "Bedroom 4 view 2"),
            ],
            9,
            "Both rooms are upstairs near the game room and shared Bath 3.",
        ),
        h_gallery(
            "Bedroom 5 + game room",
            "The published Bedroom 5 and game-room impression set.",
            "BEDROOM 5 14' x 11' | GAME ROOM 18' x 15'",
            [
                ("zillow-27-bedroom-5-1.jpg", "Bedroom 5 view 1"),
                ("zillow-28-bedroom-5-2.jpg", "Bedroom 5 view 2"),
                ("zillow-31-game-room-1.jpg", "Game room view 1"),
                ("zillow-32-game-room-2.jpg", "Game room view 2"),
            ],
            10,
            "Bedroom 5 and the game room complete the published upstairs room-gallery set.",
        ),
        h_gallery(
            "Laundry + secondary baths",
            "Utility room, first-floor Bath 2, and upstairs Bath 3.",
            "UTILITY + BATHS",
            [
                ("zillow-33-laundry.jpg", "Laundry"),
                ("zillow-34-bath-2.jpg", "Bath 2"),
                ("zillow-35-bath-3.jpg", "Bath 3"),
            ],
            11,
            "HAR lists washer connections and electric/gas dryer connections. Washer and dryer inclusion is builder-confirmed per owner-supplied information.",
        ),
    ]

    amenities = "".join(
        h_image(file, caption)
        for file, caption in [
            ("windrose-aerial.jpg", "Windrose Green aerial and lakes"),
            ("windrose-community-amenities.jpg", "Playground"),
            ("windrose-entry-sign.jpg", "Windrose Green entrance"),
            ("windrose-picnic-pavilion.jpg", "Covered pavilion"),
        ]
    )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2126 Starlight Street Property and Community Flyer</title>
<style>
:root {{--navy:#062f38;--deep:#041f26;--teal:#00a6a6;--teal-dark:#007c7c;--mint:#cff5ec;--pale:#eaf8f5;--cream:#f7f1e7;--coral:#ff6655;--gold:#f2c14e;--ink:#102a2e;--mid:#4e6468;--line:#bbdad4;}}
*{{box-sizing:border-box}} body{{margin:0;background:#d7e7e4;color:var(--ink);font-family:Arial,Helvetica,sans-serif}} .sheet{{width:8.5in;height:11in;margin:24px auto;padding:.42in .46in .32in;background:var(--cream);position:relative;overflow:hidden;box-shadow:0 12px 40px #1234;page-break-after:always}} header{{border-bottom:3px solid var(--teal);padding-bottom:12px;margin-bottom:14px}} .eyebrow{{color:var(--teal-dark);font-weight:800;font-size:10px;letter-spacing:1.5px;margin:0 0 8px}} h1,h2,h3,p{{margin-top:0}} h1{{font-size:44px;line-height:.94}} h2{{font-size:28px;margin-bottom:6px}} header p:last-child{{color:var(--mid);font-size:12px}} footer{{position:absolute;left:.46in;right:.46in;bottom:.18in;border-top:1px solid var(--line);padding-top:7px;font-size:7px;color:var(--mid)}} footer b{{float:right}} figure{{margin:0;background:white;border:1px solid var(--line);border-radius:10px;padding:5px;display:flex;flex-direction:column;min-height:0}} figure img{{width:100%;height:100%;min-height:0;object-fit:contain}} figcaption{{font-size:8px;font-weight:700;text-transform:uppercase;color:var(--mid);padding:5px 3px 1px}} .cover{{background:var(--navy);color:white}} .cover header{{border:0}} .cover h1 span{{display:block;color:var(--gold);font-size:72px}} .cover-grid{{display:grid;grid-template-columns:1.65fr 1fr;gap:14px;height:480px}} .cover-plans{{display:grid;gap:10px}} .cover .metrics{{background:var(--cream);color:var(--navy)}} .metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border-radius:12px;overflow:hidden;margin-top:14px}} .metric{{background:white;padding:14px;text-align:center}} .metric strong{{display:block;font-size:21px;color:var(--navy)}} .metric span{{font-size:8px;color:var(--mid);font-weight:800}} .split{{display:grid;grid-template-columns:1fr 1.65fr;gap:14px}} .at-glance-images{{display:grid;grid-template-columns:1fr 1.8fr;gap:12px;height:210px}} .cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:12px}} .card,.note{{background:white;border:1px solid var(--line);border-radius:12px;padding:14px}} .card strong,.note strong{{color:var(--teal-dark);text-transform:uppercase;font-size:11px}} .card p,.note p{{font-size:10px;line-height:1.35;margin:6px 0 0}} .floor-grid{{display:grid;grid-template-columns:1.7fr .9fr;gap:14px;height:720px}} .floor-grid figure{{height:100%}} .room-table{{width:100%;border-collapse:collapse;font-size:11px}} .room-table td{{padding:8px 2px;border-bottom:1px solid var(--line)}} .room-table td:last-child{{text-align:right;color:var(--teal-dark);font-weight:800}} .estimate{{font-size:32px;color:var(--navy);font-weight:900}} .rendering-banner{{display:flex;justify-content:space-between;align-items:center;background:var(--navy);color:white;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:9px}} .rendering-banner span{{color:var(--gold);font-weight:800}} .gallery{{display:grid;gap:9px;height:590px}} .grid-6{{grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(3,1fr)}} .grid-5{{grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(2,1fr)}} .grid-5 figure:nth-child(-n+2){{grid-column:span 3}} .grid-5 figure:nth-child(n+3){{grid-column:span 2}} .grid-4{{grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(2,1fr)}} .grid-3{{grid-template-columns:repeat(2,1fr);grid-template-rows:1.35fr 1fr}} .grid-3 figure:first-child{{grid-column:span 2}} .gallery-page .note{{margin-top:10px}} .dark{{background:var(--navy);color:white}} .dark header{{border-color:var(--gold)}} .dark .eyebrow{{color:var(--gold)}} .dark header p:last-child{{color:var(--mint)}} .inclusions{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .inclusion{{background:white;color:var(--navy);border:2px solid var(--teal);border-radius:12px;padding:15px}} .inclusion b{{display:block;font-size:17px}} .inclusion small{{color:var(--teal-dark);font-weight:800}} .columns-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}} .columns-2{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}} .amenity-gallery{{display:grid;grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(2,1fr);gap:10px;height:610px}} .source-list a{{color:var(--gold);font-weight:800}} .source-list li{{margin:0 0 14px;line-height:1.4}} .fine{{font-size:9px;line-height:1.4}} @page{{size:Letter;margin:0}} @media print{{body{{background:white}}.sheet{{margin:0;box-shadow:none}}}}
</style>
</head>
<body>
<section class="sheet cover">
  <header><p class="eyebrow">PROPERTY + COMMUNITY EDITION | {DATE_DISPLAY}</p><h1><span>2126</span>STARLIGHT STREET</h1><p>ANGLETON, TEXAS 77515 | {MLS}</p></header>
  <div class="cover-grid">
    {h_image("../preview.webp", "Actual supplied front photograph")}
    <div class="cover-plans">{h_image("../preview (2).webp", "First-floor plan")}{h_image("../preview (1).webp", "Second-floor plan")}</div>
  </div>
  <div class="metrics">{''.join(f'<div class="metric"><strong>{v}</strong><span>{n}</span></div>' for v,n in [("5","BEDROOMS"),("3","FULL BATHS"),("2,943","SQ FT"),("2","STORIES"),("2-CAR","GARAGE"),("6,182","SQ FT LOT - USER/BUILDER")])}</div>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 01 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">2126 STARLIGHT STREET</p><h2>The home at a glance</h2><p>Property-specific photography, builder rendering, and verified plan profile.</p></header>
  <div class="at-glance-images">{h_image("zillow-01-actual-front.jpg", "Property-specific front photograph")}{h_image("zillow-02-builder-exterior-rendering.jpg", "Builder exterior rendering")}</div>
  <div class="cards">
    <div class="card"><strong>2,943 sq ft</strong><p>Builder-sourced total living area.</p></div>
    <div class="card"><strong>6,182 sq ft lot</strong><p>User-supplied as builder-confirmed; verify by survey.</p></div>
    <div class="card"><strong>2026 construction</strong><p>Detached traditional home with brick exterior.</p></div>
    <div class="card"><strong>Lennar Canon 3550</strong><p>Bristol & Coastline Collections at Windrose Green.</p></div>
  </div>
  <aside class="note"><strong>Property description - paraphrased</strong><p>The Canon's first floor places the owner's suite at the rear, Bedroom 2 near the foyer, and a separate study beside an open family, dining, and kitchen zone with access to a covered patio. Upstairs, Bedrooms 3-5 surround a large game room and shared full bath. Estimated split: 1,848 sq ft down and 1,095 sq ft up; only the 2,943 sq ft total is builder-sourced.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 02 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">2126 STARLIGHT STREET</p><h2>First-floor plan</h2><p>Owner's suite, Bedroom 2, study, open living, laundry, two baths, garage, and patio.</p></header>
  <div class="floor-grid">{h_image("lennar-canon-first-floor.png", "Official Lennar first-floor plan")}<div class="card"><strong>Estimated floor area</strong><div class="estimate">1,848</div><p>sq ft; drawing-derived estimate</p><table class="room-table">{''.join(f'<tr><td>{r}</td><td>{s}</td></tr>' for r,s in [("Owner's suite","12' x 15'"),("Bedroom 2","11' x 11'"),("Study","11' x 11'"),("Family","11' x 21'"),("Dining","9' x 19'"),("Garage","18' x 20'"),("Patio","21' x 5'")])}</table></div></div>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 03 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">2126 STARLIGHT STREET</p><h2>Second-floor plan</h2><p>Three bedrooms, one full bath, and a central game room.</p></header>
  <div class="floor-grid">{h_image("lennar-canon-second-floor.png", "Official Lennar second-floor plan")}<div class="card"><strong>Estimated floor area</strong><div class="estimate">1,095</div><p>sq ft; drawing-derived estimate</p><table class="room-table">{''.join(f'<tr><td>{r}</td><td>{s}</td></tr>' for r,s in [("Bedroom 3","12' x 13'"),("Bedroom 4","11' x 12'"),("Bedroom 5","14' x 11'"),("Game room","18' x 15'")])}</table><p class="fine">No separate builder rendering was published for the foyer, garage, covered patio, or every closet.</p></div></div>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 04 / 18</b></footer>
</section>
{''.join(gallery_pages)}
<section class="sheet dark">
  <header><p class="eyebrow">BUILDER-CONFIRMED PER OWNER-SUPPLIED INFORMATION</p><h2>Included home package</h2><p>The purchase agreement or builder addendum is the source of record.</p></header>
  <div class="inclusions">{''.join(f'<div class="inclusion"><b>{name}</b><small>{note}</small><p>Included package; confirm final model/selection in contract.</p></div>' for name,note in [("Refrigerator / fridge","PLAN-LEVEL CORROBORATION"),("Dishwasher","ADDRESS-SPECIFIC CORROBORATION"),("Washer + dryer","OWNER/BUILDER CONFIRMATION"),("Built-in microwave","PLAN-LEVEL CORROBORATION"),("Blinds package","OWNER/BUILDER CONFIRMATION"),("Storm shutters","OWNER/BUILDER CONFIRMATION"),("Garage-door opener","PLAN-LEVEL CORROBORATION"),("Sprinkler system","PLAN-LEVEL CORROBORATION")])}</div>
  <aside class="note"><strong>Source note</strong><p>Public sources did not independently confirm washer/dryer, blinds, or storm shutters for this address. The user reports that the builder confirmed all eight items.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 12 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">2126 STARLIGHT STREET</p><h2>Facts, features + construction</h2><p>Address-specific facts are separated from current Canon plan standards.</p></header>
  {h_image("zillow-02-builder-exterior-rendering.jpg", "Builder exterior rendering - not an actual photo")}
  <div class="columns-3" style="margin-top:12px"><div class="card"><strong>Address-specific</strong><p>Detached single-family home; traditional style; 2026 new construction; brick exterior; slab foundation; composition roof; covered patio; fenced rear yard; no private pool.</p></div><div class="card"><strong>Interior + layout</strong><p>Carpet and vinyl listed by HAR. Open kitchen/family relationship. Owner's suite and Bedroom 2 down; Bedrooms 3-5 and game room up.</p></div><div class="card"><strong>Canon standards</strong><p>Quartz, full-height backsplash, shaker cabinets, stainless gas range, PEX plumbing, LED lighting, smart thermostat, finished garage, opener, sod, fence, and sprinklers.</p></div></div>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 13 / 18</b></footer>
</section>
<section class="sheet dark">
  <header><p class="eyebrow">HOME SYSTEMS + COMMUNITY INFRASTRUCTURE</p><h2>Utilities, energy + green features</h2><p>Solar claims are kept in their proper scope.</p></header>
  <div class="columns-2"><div class="card"><strong>Utilities</strong><p>Public water/sewer; electric provider choice through Texas Power to Choose; natural-gas infrastructure; community fiber; washer hookup plus electric and gas dryer connections.</p></div><div class="card"><strong>Canon energy standards</strong><p>Energy-efficient HVAC/water heating; Low-E windows; Polyseal; R-13/R-22/R-38 insulation in applicable assemblies; smart thermostat; LED lighting; water-saving toilets; third-party code inspection.</p></div></div>
  <aside class="note" style="margin-top:16px"><strong>Solar-powered community streetlights</strong><p>Windrose Green advertises solar-powered streetlights. No public source establishes solar panels, batteries, or other on-site generation at this house.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 14 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">WINDROSE GREEN</p><h2>Community amenities</h2><p>Official community photography and currently advertised amenities.</p></header>
  <div class="amenity-gallery">{amenities}</div>
  <aside class="note"><strong>Amenities</strong><p>Two lakes, splash pad, playground, covered pavilion, activity lawns, parks, walking trails, and hike/bike trails.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 15 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">WINDROSE GREEN</p><h2>Community map + surroundings</h2><p>Neighborhood orientation only; the subject homesite is not clearly marked.</p></header>
  {h_image("windrose-map.png", "Windrose Green site map - exact lot not marked")}
  <div class="columns-3" style="margin-top:12px"><div class="card"><strong>Road access</strong><p>Near Hwy 35 Bypass/FM 523 with access toward Hwy 288.</p></div><div class="card"><strong>Angleton ISD</strong><p>Confirm current attendance assignments directly with the district.</p></div><div class="card"><strong>Surroundings</strong><p>Community FAQ estimates: Lake Jackson ~20 min; Surfside ~25 min; Rosharon ~13 mi; Pearland ~30 mi; Houston under 50 mi.</p></div></div>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 16 / 18</b></footer>
</section>
<section class="sheet">
  <header><p class="eyebrow">WINDROSE GREEN</p><h2>Community + HOA profile</h2><p>Current public facts, with source conflicts disclosed.</p></header>
  {h_image("windrose-aerial.jpg", "Official Windrose Green aerial")}
  <div class="cards"><div class="card"><strong>154 acres</strong><p>Community scale stated by the current FAQ.</p></div><div class="card"><strong>~648 homesites</strong><p>Approximate build-out stated by the community.</p></div><div class="card"><strong>Mandatory HOA</strong><p>Windrose Green Community Association, Inc.</p></div><div class="card"><strong>Three builders</strong><p>CastleRock, Coventry, and Lennar currently listed.</p></div></div>
  <aside class="note"><strong>Due diligence</strong><p>The supplied July 2026 sheet and current FAQ name different HOA managers. School names also conflict across supplied sources. Confirm both directly; this flyer identifies Angleton ISD only.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 17 / 18</b></footer>
</section>
<section class="sheet dark source-list">
  <header><p class="eyebrow">RESEARCH DATE {DATE_DISPLAY}</p><h2>Sources + verification notes</h2><p>Financial and listing-market details were intentionally excluded.</p></header>
  <ul><li><a href="https://www.har.com/2126-starlight-st/sale_62207090">HAR property record</a> - MLS, room dimensions, construction, utilities, and address-specific facts.</li><li><a href="https://www.zillow.com/homedetails/2126-Starlight-St-Angleton-TX-77515/464083448_zpid/">Zillow property record</a> - syndicated description, front photo, plans, and illustrative gallery.</li><li><a href="https://www.lennar.com/new-homes/texas/houston/angleton/windrose-green/bristol-coastline-collections/canon">Lennar Canon plan</a> - plan identity, vector plans, and current standards.</li><li><a href="https://www.windrosegreen.com/amenities/">Windrose Green amenities</a> - recreation, infrastructure, streetlights, and official photos.</li><li><a href="https://www.windrosegreen.com/faq">Windrose Green FAQ</a> - scale, builders, HOA context, and surroundings.</li></ul>
  <aside class="note"><strong>Verification notes</strong><p>Lot size 6,182 sq ft is user-supplied as builder-confirmed; public portal fields do not verify it and the prior flyer says 5,400. Floor split is estimated. All 31 interior images are artistic impressions. One property-specific front photo was found. Confirm image rights and controlling documents before distribution. Public-source text was paraphrased.</p></aside>
  <footer>{ADDRESS} | {MLS} | PREPARED {DATE_DISPLAY}<b>PAGE 18 / 18</b></footer>
</section>
</body></html>"""
    HTML_OUT.write_text(html_text, encoding="utf-8")


def main() -> None:
    preprocess()
    build_pdf()
    build_html()
    print(f"Wrote {PDF_OUT}")
    print(f"Wrote {HTML_OUT}")


if __name__ == "__main__":
    main()
