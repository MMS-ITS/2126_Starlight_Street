#!/usr/bin/env python3
"""Build a one-page letter-size prospective-tenant flyer with fillable manager contact fields."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from PIL import Image

from build_flyer import (
    ADDRESS,
    ASSETS,
    CORAL,
    CREAM,
    DATE_DISPLAY,
    DEEP,
    FONT,
    FONT_BOLD,
    GOLD,
    INK,
    LINE,
    MID,
    MINT,
    MLS,
    NAVY,
    PALE,
    ROOT,
    TEAL,
    TEAL_DARK,
    UPLOADED_FRONT,
    WHITE,
    draw_image_contain,
    paragraph,
    rounded_card,
)

HERE = Path(__file__).resolve().parent
PDF_OUT = HERE / "2126-Starlight-Street-One-Page-Rental-Flyer.pdf"
HTML_OUT = HERE / "2126-Starlight-Street-One-Page-Rental-Flyer.html"
PAGE_W, PAGE_H = letter
FIRST_PLAN_TRIMMED = ASSETS / "lennar-canon-first-floor-compact.png"
SECOND_PLAN_TRIMMED = ASSETS / "lennar-canon-second-floor-compact.png"


def _expanded_bbox(bbox: tuple[int, int, int, int], size: tuple[int, int], padding: int = 18) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    width, height = size
    return max(0, left - padding), max(0, top - padding), min(width, right + padding), min(height, bottom + padding)


def create_compact_floor_plans() -> None:
    """Trim only transparent/light empty margins while retaining the original plans."""
    first_source = ASSETS / "lennar-canon-first-floor.png"
    second_source = ASSETS / "lennar-canon-second-floor.png"

    first = Image.open(first_source).convert("RGBA")
    first_bbox = first.getchannel("A").getbbox()
    if first_bbox:
        first.crop(_expanded_bbox(first_bbox, first.size)).save(FIRST_PLAN_TRIMMED)

    second = Image.open(second_source).convert("RGBA")
    white = Image.new("RGBA", second.size, "white")
    white.alpha_composite(second)
    dark_mask = white.convert("L").point(lambda value: 255 if value < 200 else 0)
    second_bbox = dark_mask.getbbox() or second.getchannel("A").getbbox()
    if second_bbox:
        second.crop(_expanded_bbox(second_bbox, second.size)).save(SECOND_PLAN_TRIMMED)


BODY = ParagraphStyle(
    "compact-body",
    fontName=FONT,
    fontSize=6.6,
    leading=8.35,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=0,
)
BODY_SMALL = ParagraphStyle(
    "compact-small",
    fontName=FONT,
    fontSize=6.0,
    leading=7.4,
    textColor=MID,
    alignment=TA_LEFT,
    spaceAfter=0,
)
BODY_WHITE = ParagraphStyle(
    "compact-white",
    fontName=FONT,
    fontSize=6.4,
    leading=8.15,
    textColor=WHITE,
    alignment=TA_LEFT,
    spaceAfter=0,
)
FOOTNOTE = ParagraphStyle(
    "footnote",
    fontName=FONT,
    fontSize=4.75,
    leading=5.9,
    textColor=MID,
    alignment=TA_LEFT,
    spaceAfter=0,
)


def compact_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    body: str,
    *,
    accent=TEAL,
    fill=WHITE,
    style: ParagraphStyle = BODY,
) -> None:
    rounded_card(c, x, y, width, height, fill=fill, stroke=LINE, radius=9, line_width=0.7)
    c.setFillColor(accent)
    c.roundRect(x, y + height - 23, width, 23, 9, fill=1, stroke=0)
    c.rect(x, y + height - 23, width, 11, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 7.5)
    c.drawString(x + 10, y + height - 15.5, title.upper())
    paragraph(c, body, x + 10, y + height - 31, width - 20, style, max_height=height - 37)


def metric_box(c: canvas.Canvas, x: float, y: float, width: float, value: str, label: str, *, accent=TEAL) -> None:
    rounded_card(c, x, y, width, 40, fill=WHITE, stroke=LINE, radius=7, line_width=0.6)
    c.setFillColor(accent)
    c.setFont(FONT_BOLD, 13)
    c.drawCentredString(x + width / 2, y + 20, value)
    c.setFillColor(MID)
    c.setFont(FONT_BOLD, 5.2)
    c.drawCentredString(x + width / 2, y + 8, label.upper())


def draw_manager_form(c: canvas.Canvas) -> None:
    c.setFillColor(DEEP)
    c.rect(0, 0, PAGE_W, 46, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 6.2)
    c.drawString(24, 34, "PROPERTY MANAGEMENT CONTACT")

    fields = [
        ("manager_name", "MANAGER / COMPANY", 24, 7, 214),
        ("manager_phone", "PHONE", 246, 7, 118),
        ("manager_email", "EMAIL", 372, 7, 216),
    ]
    for name, label, x, y, width in fields:
        c.setFillColor(MINT)
        c.setFont(FONT_BOLD, 4.8)
        c.drawString(x, y + 20, label)
        c.acroForm.textfield(
            name=name,
            tooltip=label.title(),
            x=x,
            y=y,
            width=width,
            height=17,
            borderStyle="solid",
            borderWidth=0.6,
            borderColor=TEAL,
            fillColor=WHITE,
            textColor=INK,
            forceBorder=True,
            fontName=FONT,
            fontSize=7,
        )


def build_pdf() -> None:
    c = canvas.Canvas(str(PDF_OUT), pagesize=letter, pageCompression=1)
    c.setTitle("2126 Starlight Street One-Page Prospective Tenant Flyer")
    c.setAuthor("Property management rental handout")
    c.setSubject("Compact home, community, school, public service, healthcare, and shopping overview")
    c.setKeywords("2126 Starlight Street, Angleton, rental, tenant, Windrose Green, MLS 62207090")

    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Header band
    c.setFillColor(TEAL)
    c.rect(0, 742, PAGE_W, 50, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 8)
    c.drawString(24, 770, "PROSPECTIVE TENANT PROPERTY HANDOUT")
    c.setFont(FONT, 6.4)
    c.drawString(24, 757, "Prepared for distribution by the property manager")
    c.setFont(FONT_BOLD, 6.5)
    c.drawRightString(588, 770, DATE_DISPLAY)
    c.drawRightString(588, 757, MLS)

    # Hero image and identity panel
    draw_image_contain(c, UPLOADED_FRONT, 24, 535, 248, 194, background=WHITE, stroke=TEAL, radius=10, inset=4)
    c.setFillColor(TEAL_DARK)
    c.roundRect(35, 545, 157, 17, 7, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 6.2)
    c.drawCentredString(113.5, 550.5, "ACTUAL SUPPLIED FRONT PHOTO")

    rounded_card(c, 284, 535, 304, 194, fill=PALE, stroke=TEAL, radius=11, line_width=1)
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 31)
    c.drawString(300, 690, "2126")
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 16)
    c.drawString(300, 668, "STARLIGHT STREET")
    c.setFillColor(MID)
    c.setFont(FONT_BOLD, 6.8)
    c.drawString(300, 654, "ANGLETON, TEXAS 77515  |  LENNAR CANON 3550")

    values = [
        ("5", "BEDROOMS", TEAL),
        ("3", "FULL BATHS", CORAL),
        ("2,943", "SQ FT LIVING", TEAL_DARK),
        ("2", "STORIES", TEAL_DARK),
        ("2-CAR", "ATTACHED GARAGE", CORAL),
        ("6,182", "SQ FT LOT*", TEAL),
    ]
    for index, (value, name, accent) in enumerate(values):
        col = index % 3
        row = index // 3
        metric_box(c, 300 + col * 92, 602 - row * 47, 84, value, name, accent=accent)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 6.1)
    c.drawString(300, 544, "2026 NEW CONSTRUCTION  |  BRICK  |  SLAB  |  COMPOSITION ROOF")

    # Three compact main-information columns
    compact_card(
        c,
        24,
        296,
        181,
        226,
        "Home + layout",
        "<b>Approx. floor split:</b> 1,848 sq ft down + 1,095 sq ft up.*<br/>"
        "<b>First:</b> owner's suite, Bedroom 2, study, open living, laundry, two baths, garage + patio. <b>Second:</b> Bedrooms 3-5, Bath 3 + game room.<br/>"
        "<b>Room guide:</b> family 11' x 21'; dining 9' x 19'; owner's 12' x 15'; game room 18' x 15'.<br/>"
        "Fenced rear yard &bull; covered patio &bull; walk-in closet &bull; double sinks + separate shower &bull; no private pool.",
        accent=TEAL_DARK,
    )
    draw_image_contain(c, FIRST_PLAN_TRIMMED, 34, 306, 76, 84, background=PALE, stroke=LINE, radius=5, inset=1)
    draw_image_contain(c, SECOND_PLAN_TRIMMED, 119, 306, 76, 84, background=PALE, stroke=LINE, radius=5, inset=1)
    for plan_label, plan_x, plan_color in (("1ST FLOOR", 39, TEAL_DARK), ("2ND FLOOR", 124, CORAL)):
        c.setFillColor(plan_color)
        c.roundRect(plan_x, 310, 66, 11, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 4.8)
        c.drawCentredString(plan_x + 33, 313.5, plan_label)

    compact_card(
        c,
        215,
        296,
        181,
        226,
        "Included + fittings",
        "<b>Builder-confirmed package:* </b><br/>"
        "Refrigerator/fridge &bull; dishwasher &bull; washer + dryer &bull; built-in microwave &bull; blinds package &bull; storm shutters &bull; garage-door opener &bull; sprinkler system.<br/>"
        "<b>Kitchen standards:</b> quartz counters, full-height backsplash, shaker cabinets, stainless gas range, undermount sink + pantry.<br/>"
        "<b>Comfort/efficiency:</b> Low-E windows, smart thermostat, LED lighting, energy-efficient HVAC/water heating, PEX plumbing + code-certified inspection.<br/>"
        "<b>Build/finish:</b> post-tension foundation, 30-year shingles, finished garage, water-saving toilets, vinyl/LVP in selected areas, carpet/tile by plan, sod + rear fence.",
        accent=CORAL,
    )
    compact_card(
        c,
        406,
        296,
        182,
        226,
        "Windrose Green + HOA",
        "<b>Mandatory HOA: $825/year.</b>* Tenant responsibility and amenity access depend on the lease and current HOA rules.<br/>"
        "HOA supports community standards, common-area landscaping, amenities, parks, trails, lakes and shared spaces.<br/>"
        "<b>Facilities:</b> two lakes, splash pad, playground, covered pavilion, hammock grove, activity lawns, recreation center, parks + paved walking/hike-bike trails.<br/>"
        "<b>Community:</b> 154 acres, approximately 648 homesites; current builders listed are CastleRock, Coventry + Lennar.<br/>"
        "<b>Infrastructure:</b> natural-gas lines, fiber connectivity + solar-powered community streetlights.<br/>"
        "Association: Windrose Green Community Association, Inc.; confirm current management before payments.",
        accent=GOLD,
    )

    # Tenant area services, four compact cards
    compact_card(
        c,
        24,
        198,
        276,
        86,
        "Schools listed by Windrose Green",
        "Rancho Isabella Elementary <b>Pre-K-5</b> - ~2.7 mi / 6 min<br/>"
        "Angleton Junior High <b>6-8</b> - ~1.8 mi / 6 min<br/>"
        "Angleton High School <b>9-12</b> - ~1.0 mi / 4 min<br/>"
        "<b>Angleton ISD:</b> verify current zoning before relying on an assignment.",
        accent=TEAL,
        style=BODY_SMALL,
    )
    compact_card(
        c,
        24,
        104,
        276,
        86,
        "Public + utility services",
        "City water/sewer: <b>979-849-4364</b> &bull; Police non-emergency: <b>979-849-2383</b><br/>"
        "Fire non-emergency: <b>979-849-1265</b> &bull; Waste Connections: <b>979-864-4600</b><br/>"
        "Electric provider choice: PowerToChoose.org &bull; community sources list Centric gas/fiber + AT&T fiber; verify address availability. <b>Call 911 for emergencies.</b>",
        accent=TEAL_DARK,
        style=BODY_SMALL,
    )
    compact_card(
        c,
        310,
        198,
        278,
        86,
        "Healthcare nearby",
        "UTMB Angleton Danbury Hospital + 24-hour ER - ~2.9 mi / 6 min<br/>"
        "Angleton ER, freestanding 24/7 ER - ~3.9 mi / 8 min<br/>"
        "UTMB Health Urgent Care - ~6.3 mi / 10 min<br/>"
        "H-E-B Pharmacy - ~3.7 mi / 8 min. Insurance networks and ER billing vary.",
        accent=CORAL,
        style=BODY_SMALL,
    )
    compact_card(
        c,
        310,
        104,
        278,
        86,
        "Shopping + access",
        "Angleton H-E-B - ~3.7 mi / 8 min<br/>"
        "Walmart Supercenter - ~3.8 mi / 8 min<br/>"
        "Brazos Mall, Lake Jackson - ~14.3 mi / 17 min<br/>"
        "Near Hwy 35 Bypass/FM 523 with access toward Hwy 288. Distances and times are approximate.",
        accent=GOLD,
        style=BODY_SMALL,
    )

    # Source/disclaimer strip
    rounded_card(c, 24, 54, 564, 39, fill=WHITE, stroke=LINE, radius=7, line_width=0.5)
    paragraph(
        c,
        "<b>*Verify before lease:</b> 6,182 sq ft lot and complete inclusion package are owner-supplied as builder-confirmed; floor split is estimated. Floor-plan miniatures use official Lennar plans with empty margins trimmed for space. Confirm appliance models, utilities, school zoning, HOA access/assessment responsibility, distances and all lease terms. Sources: HAR, Lennar, Windrose Green, Angleton ISD, City of Angleton, UTMB, H-E-B, Walmart and Brazos Mall; checked 25 Nov 2026. Public-source text was paraphrased.",
        32,
        85,
        548,
        FOOTNOTE,
        max_height=31,
    )
    c.setFillColor(MID)
    c.setFont(FONT_BOLD, 4.8)
    c.drawRightString(588, 96, "ONE-PAGE HANDOUT  |  PAGE 1 OF 1")

    draw_manager_form(c)
    c.save()
    print(f"Wrote {PDF_OUT}")


def build_html() -> None:
    text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>2126 Starlight Street One-Page Prospective Tenant Flyer</title>
<style>
:root{{--navy:#062f38;--deep:#041f26;--teal:#00a6a6;--teal-dark:#007c7c;--mint:#cff5ec;--pale:#eaf8f5;--cream:#f7f1e7;--coral:#ff6655;--gold:#f2c14e;--ink:#102a2e;--mid:#4e6468;--line:#bbdad4}}*{{box-sizing:border-box}}body{{margin:0;background:#dce9e7;font-family:Arial,sans-serif;color:var(--ink)}}.sheet{{width:8.5in;height:11in;margin:20px auto;background:var(--cream);position:relative;overflow:hidden;box-shadow:0 12px 34px #1235}}header{{height:.7in;background:var(--teal);color:white;padding:.17in .34in;display:flex;justify-content:space-between}}header b{{font-size:11px}}header small{{display:block;margin-top:4px}}.hero{{height:2.7in;display:grid;grid-template-columns:43% 57%;gap:12px;padding:.18in .34in}}figure{{margin:0;background:white;border:2px solid var(--teal);border-radius:12px;padding:5px}}figure img{{width:100%;height:100%;object-fit:contain}}.identity{{background:var(--pale);border:1px solid var(--teal);border-radius:12px;padding:14px}}h1{{margin:0;color:var(--gold);font-size:42px}}h2{{margin:0;color:var(--navy);font-size:22px}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}}.metric{{background:white;border:1px solid var(--line);border-radius:8px;text-align:center;padding:7px 3px}}.metric b{{display:block;color:var(--teal-dark);font-size:17px}}.metric small{{font-size:7px;font-weight:bold;color:var(--mid)}}.main{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:0 .34in;height:3.15in}}.mini-plans{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:4px 10px 8px;height:78px}}.mini-plans figure{{position:relative;background:var(--pale);border:1px solid var(--line);border-radius:6px;padding:1px}}.mini-plans img{{width:100%;height:100%;object-fit:contain}}.mini-plans span{{position:absolute;left:5px;right:5px;bottom:3px;background:var(--teal-dark);color:white;border-radius:5px;text-align:center;font-size:6px;font-weight:bold;padding:2px}}.mini-plans figure:last-child span{{background:var(--coral)}}.lower{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:8px 10px;padding:.12in .34in 0;height:2.65in}}.card{{background:white;border:1px solid var(--line);border-radius:10px;overflow:hidden}}.card h3{{margin:0;padding:7px 10px;background:var(--teal-dark);color:white;font-size:10px;text-transform:uppercase}}.card:nth-child(2) h3{{background:var(--coral)}}.card:nth-child(3) h3{{background:var(--gold)}}.card p{{font-size:8px;line-height:1.3;margin:8px 10px}}.lower .card p{{font-size:7.5px}}.notes{{margin:.1in .34in 0;border:1px solid var(--line);border-radius:7px;background:white;padding:7px;font-size:6px;line-height:1.25}}footer{{position:absolute;left:0;right:0;bottom:0;height:.64in;background:var(--deep);color:white;padding:7px .34in}}footer b{{display:block;color:var(--gold);font-size:7px;margin-bottom:5px}}.fields{{display:grid;grid-template-columns:1.5fr .8fr 1.4fr;gap:8px}}.field{{background:white;color:var(--mid);height:21px;border:1px solid var(--teal);padding:5px;font-size:7px}}@page{{size:Letter;margin:0}}@media print{{body{{background:white}}.sheet{{margin:0;box-shadow:none}}}}
</style></head><body><main class="sheet">
<header><div><b>PROSPECTIVE TENANT PROPERTY HANDOUT</b><small>Prepared for distribution by the property manager</small></div><div><b>{DATE_DISPLAY}</b><small>{MLS}</small></div></header>
<section class="hero"><figure><img src="../preview.webp" alt="Actual supplied front photograph"></figure><div class="identity"><h1>2126</h1><h2>STARLIGHT STREET</h2><p style="font-size:9px;font-weight:bold">ANGLETON, TEXAS 77515 | LENNAR CANON 3550</p><div class="metrics">{''.join(f'<div class="metric"><b>{v}</b><small>{n}</small></div>' for v,n in [("5","BEDROOMS"),("3","FULL BATHS"),("2,943","SQ FT"),("2","STORIES"),("2-CAR","GARAGE"),("6,182","SQ FT LOT*")])}</div><p style="font-size:8px;font-weight:bold">2026 NEW CONSTRUCTION | BRICK | SLAB | COMPOSITION ROOF</p></div></section>
<section class="main">
<div class="card"><h3>Home + layout</h3><p><b>Approx. floor split:</b> 1,848 sq ft down + 1,095 sq ft up.*<br><b>First:</b> owner's suite, Bedroom 2, study, open living, laundry, two baths, garage + patio. <b>Second:</b> Bedrooms 3–5, Bath 3 + game room.<br><b>Room guide:</b> family 11' × 21'; dining 9' × 19'; owner's 12' × 15'; game room 18' × 15'.<br>Fenced yard • covered patio • walk-in closet • double sinks + separate shower • no private pool.</p><div class="mini-plans"><figure><img src="assets/lennar-canon-first-floor-compact.png" alt="Compact first-floor plan"><span>1ST FLOOR</span></figure><figure><img src="assets/lennar-canon-second-floor-compact.png" alt="Compact second-floor plan"><span>2ND FLOOR</span></figure></div></div>
<div class="card"><h3>Included + fittings</h3><p><b>Builder-confirmed package:*</b> refrigerator/fridge, dishwasher, washer + dryer, built-in microwave, blinds, storm shutters, garage-door opener + sprinklers.<br><b>Kitchen:</b> quartz, full-height backsplash, shaker cabinets, stainless gas range, undermount sink + pantry.<br><b>Efficiency:</b> Low-E windows, smart thermostat, LED, efficient HVAC/water heating + PEX plumbing.<br><b>Build/finish:</b> post-tension foundation, 30-year shingles, finished garage, water-saving toilets, vinyl/LVP, carpet/tile by plan, sod + rear fence.</p></div>
<div class="card"><h3>Windrose Green + HOA</h3><p><b>Mandatory HOA: $825/year.</b>* Lease controls tenant responsibility and access.<br>HOA supports standards, landscaping, lakes, parks, trails, amenities and common areas.<br><b>Facilities:</b> two lakes, splash pad, playground, pavilion, hammock grove, activity lawns, recreation center, parks + paved walking/hike-bike trails.<br><b>Community:</b> 154 acres, approximately 648 homesites; CastleRock, Coventry + Lennar currently listed.<br><b>Infrastructure:</b> natural gas, fiber + solar-powered community streetlights.</p></div>
</section>
<section class="lower">
<div class="card"><h3>Schools listed by Windrose Green</h3><p>Rancho Isabella Elementary <b>Pre-K–5</b> — ~2.7 mi / 6 min<br>Angleton Junior High <b>6–8</b> — ~1.8 mi / 6 min<br>Angleton High <b>9–12</b> — ~1.0 mi / 4 min<br><b>Verify current Angleton ISD zoning.</b></p></div>
<div class="card"><h3>Healthcare nearby</h3><p>UTMB Angleton Danbury Hospital + 24-hour ER — ~2.9 mi / 6 min<br>Angleton ER, freestanding 24/7 ER — ~3.9 mi / 8 min<br>UTMB Urgent Care — ~6.3 mi / 10 min<br>H-E-B Pharmacy — ~3.7 mi / 8 min</p></div>
<div class="card"><h3>Public + utility services</h3><p>City water/sewer: <b>979-849-4364</b> | Police non-emergency: <b>979-849-2383</b><br>Fire: <b>979-849-1265</b> | Waste Connections: <b>979-864-4600</b><br>PowerToChoose.org; Centric gas/fiber + AT&T fiber listed by community. Verify availability. Call 911 for emergencies.</p></div>
<div class="card"><h3>Shopping + access</h3><p>Angleton H-E-B — ~3.7 mi / 8 min<br>Walmart Supercenter — ~3.8 mi / 8 min<br>Brazos Mall — ~14.3 mi / 17 min<br>Near Hwy 35 Bypass/FM 523 with access toward Hwy 288.</p></div>
</section>
<div class="notes"><b>*Verify before lease:</b> lot size and complete inclusion package are owner-supplied as builder-confirmed; floor split is estimated. Floor-plan miniatures use official Lennar plans with empty margins trimmed for space. Confirm appliance models, utilities, zoning, HOA access/fees, distances and lease terms. Sources checked 25 Nov 2026; public-source text was paraphrased.</div>
<footer><b>PROPERTY MANAGEMENT CONTACT</b><div class="fields"><div class="field">MANAGER / COMPANY</div><div class="field">PHONE</div><div class="field">EMAIL</div></div></footer>
</main></body></html>"""
    HTML_OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {HTML_OUT}")


def main() -> None:
    create_compact_floor_plans()
    build_pdf()
    build_html()


if __name__ == "__main__":
    main()
