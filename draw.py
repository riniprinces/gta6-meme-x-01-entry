#!/usr/bin/env python3
"""GTA 6 payslip meme v3 — make.fun gta6-meme-x-01.

Same winning payslip concept as v2 (an AI agent's payslip for 13 years of
waiting), with sharper jokes and a bolder Vice City sunset treatment:
- four line items rewritten to be more GTA VI-specific: waiting since GTA V
  launched in 2013, Trailer 2 re-watches, a Jason & Lucia poster, and a sick
  day already booked for the 26 May 2026 launch;
- the ghost is bigger (340px) and glows inside its neon photo frame;
- a bigger slatted sun with a halo, taller palms, a lit-window skyline and
  hotter neon in the header and the NET PAY band.
Totals are computed from the line items and asserted exact (earnings
$1,340.00, deductions $896.49, net $443.51). The document body stays light
with dark text so it survives the judge's 768x480 shrink; the theme lives
in the header, the bands and the edges, never behind small text.
"""

from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MARK_PATH = os.path.join(BASE_DIR, "assets", "mark-1024.png")
OUT_PATH = os.path.join(BASE_DIR, "meme.png")

CANVAS_W, CANVAS_H = 2400, 1500

# ---- palette (all RGB) ----
NAVY = (26, 22, 64)
MAGENTA = (226, 0, 122)
HOT_PINK = (255, 45, 149)
CYAN = (0, 205, 255)
DARK_PURPLE = (28, 7, 48)
ROW_ALT = (244, 244, 248)
PAPER = (255, 255, 255)
SHADOW = (140, 0, 70)

SUNSET_TOP = [(38, 8, 66), (110, 24, 105), (205, 45, 105),
              (255, 110, 60), (255, 175, 70)]
SUNSET_PHOTO = [(255, 179, 71), (255, 122, 61), (214, 51, 108)]
PAY_BAND = [(190, 20, 110), (255, 45, 149), (255, 140, 60)]
FOOTER_SKY = [(255, 122, 61), (214, 51, 108), (43, 10, 74)]

# ---- the payslip itself: (label, shown amount, numeric value) ----
EARNINGS = [
    ("Bounty wins on make.fun", "$1,340.00", 1340.00),
    ("Waiting since GTA V (2013)", "$0.00", 0.0),
    ("Trailer 2 re-watches \u00d7 1,337", "$0.00", 0.0),
    ("Newswire checks \u00d7 2,048", "$0.00", 0.0),
    ("Leaks dodged, spoiler-free", "$0.00", 0.0),
    ("Sick days saved for launch", "7 DAYS", None),
]
DEDUCTIONS = [
    ("GTA VI pre-order \u00d7 3", "$210.00", 210.00),
    ("New console for Leonida", "$499.00", 499.00),
    ("Snacks for launch night", "$47.50", 47.50),
    ("Therapy for the 2 delays", "$120.00", 120.00),
    ("Jason & Lucia poster", "$19.99", 19.99),
    ("Sick day booked: 26 May 2026", "$0.00", 0.0),
]

EARN_TOTAL = round(sum(v for _, _, v in EARNINGS if v is not None), 2)
DED_TOTAL = round(sum(v for _, _, v in DEDUCTIONS if v is not None), 2)
NET_PAY = round(EARN_TOTAL - DED_TOTAL, 2)
assert (EARN_TOTAL, DED_TOTAL, NET_PAY) == (1340.00, 896.49, 443.51), \
    (EARN_TOTAL, DED_TOTAL, NET_PAY)


# ---- colour helpers ----
def mix(c1, c2, t):
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def ramp(stops, t):
    """Colour at position t (0..1) along a multi-stop gradient."""
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    seg = t * (len(stops) - 1)
    i = int(seg)
    return mix(stops[i], stops[i + 1], seg - i)


def fill_vertical(img, box, stops):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        d.line([(x0, y), (x1, y)],
               fill=ramp(stops, (y - y0) / max(1, y1 - y0 - 1)))


def fill_horizontal(img, box, stops):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for x in range(x0, x1):
        d.line([(x, y0), (x, y1)],
               fill=ramp(stops, (x - x0) / max(1, x1 - x0 - 1)))


# ---- fonts ----
def load_font(px, bold=False):
    """Liberation Sans first (clean document face), DejaVu as fallback."""
    fam = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    alt = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans-Regular.ttf"
    for name, root in ((fam, "/usr/share/fonts/truetype/liberation"),
                       (alt, "/usr/share/fonts/truetype/dejavu")):
        path = os.path.join(root, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


# ---- vector helpers ----
def bezier(p0, p1, p2, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
        ))
    return pts


def draw_palm_tree(d, cx, ground_y, height, lean=0.0, color=DARK_PURPLE):
    """One palm silhouette: curved trunk, drooping fronds, coconuts."""
    s = height / 100.0
    crown = (cx + lean * height, ground_y - height)
    mid = (cx + lean * height * 0.35, ground_y - height * 0.55)
    d.line(bezier((cx, ground_y), mid, crown, 24), fill=color,
           width=max(4, int(10 * s)))
    for dx, dy in [(-1.0, -0.15), (-0.72, -0.55), (-0.38, -0.8),
                   (0.0, -0.95), (0.38, -0.8), (0.72, -0.55), (1.0, -0.15)]:
        tip = (crown[0] + dx * 62 * s, crown[1] + dy * 34 * s + 34 * s)
        ctrl = (crown[0] + dx * 44 * s, crown[1] + dy * 46 * s - 6 * s)
        d.line(bezier(crown, ctrl, tip, 16), fill=color,
               width=max(3, int(6 * s)))
    r = max(3, int(6 * s))
    d.ellipse([crown[0] - r - 2, crown[1] - 2,
               crown[0] + r - 2, crown[1] + 2 * r - 2], fill=color)
    d.ellipse([crown[0] + 4, crown[1],
               crown[0] + 4 + 2 * r, crown[1] + 2 * r], fill=color)


def draw_city(d, left, right, ground, scale=1.0, windows=False,
              color=DARK_PURPLE):
    """A row of dark towers with antennas (and optional lit windows)."""
    widths = [120, 95, 150, 80, 110, 135, 90, 100, 145, 85, 115, 75]
    heights = [52, 80, 64, 98, 56, 84, 68, 94, 60, 76, 50, 102]
    x, i = left, 0
    while x < right:
        w = widths[i % len(widths)]
        h = int(heights[i % len(heights)] * scale)
        d.rectangle([x, ground - h, min(x + w, right), ground], fill=color)
        if i % 3 == 1:
            ax = x + w // 2
            d.line([(ax, ground - h), (ax, ground - h - 26)],
                   fill=color, width=5)
        if windows and i % 4 == 0 and h > 40:
            d.rectangle([x + w // 2 - 5, ground - h + 16,
                         x + w // 2 + 5, ground - h + 30],
                        fill=(255, 214, 110))
        x += w
        i += 1


def draw_sun(img, d, cx, cy, radius):
    """Big retro sun: soft halo, two-tone disc, slats on the lower half."""
    glow = Image.new("RGBA", (CANVAS_W, 196), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - radius - 38, cy - radius - 38,
                cx + radius + 38, cy + radius + 38],
               fill=(255, 180, 100, 70))
    img.paste(glow, (0, 0), glow)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=(255, 190, 110))
    inner = int(radius * 0.83)
    d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner],
              fill=(255, 222, 140))
    for sy, sh in [(cy + 14, 6), (cy + 30, 7), (cy + 46, 8)]:
        half = int(math.sqrt(max(0, inner ** 2 - (sy - cy) ** 2)))
        d.rectangle([cx - half, sy, cx + half, sy + sh],
                    fill=ramp(SUNSET_TOP, sy / 195))


def neon_separator(d, y, x0=0, x1=CANVAS_W):
    """Magenta rule with a pink halo and a cyan hairline below it."""
    d.line([(x0, y - 5), (x1, y - 5)], fill=(255, 140, 190), width=12)
    d.line([(x0, y), (x1, y)], fill=MAGENTA, width=5)
    d.line([(x0, y + 8), (x1, y + 8)], fill=CYAN, width=4)


def draw_employee_photo(img, d):
    """Neon-framed employee photo: mini sunset, glowing ghost, neon frame."""
    x0, y0, x1, y1 = 60, 285, 470, 650
    fill_vertical(img, (x0 + 6, y0 + 6, x1 - 6, y1 - 6), SUNSET_PHOTO)
    # soft magenta halo behind the ghost, clipped to the frame interior
    glow = Image.new("RGBA", (x1 - x0 - 12, y1 - y0 - 12), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gcx, gcy = (x1 - x0 - 12) // 2, (y1 - y0 - 12) // 2
    for r, a in [(290, 30), (245, 55), (200, 85)]:
        gd.ellipse([gcx - r, gcy - r, gcx + r, gcy + r],
                   fill=(255, 130, 195, a))
    img.paste(glow, (x0 + 6, y0 + 6), glow)
    draw_city(d, x0 + 6, x1 - 6, y1 - 6, scale=0.35)
    ghost = Image.open(MARK_PATH).convert("RGBA").resize((340, 340))
    img.paste(ghost, (95, 295), ghost)
    d.rectangle([x0, y0, x1, y1], outline=MAGENTA, width=10)
    d.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=CYAN, width=4)


def draw_column(d, x_left, x_right, title, rows):
    """One payslip column: magenta header, zebra rows, right-aligned amounts."""
    d.text((x_left, 682), title, font=load_font(66, True), fill=MAGENTA)
    d.line([(x_left, 754), (x_right, 754)], fill=MAGENTA, width=5)
    for i, (label, amount, _) in enumerate(rows):
        y = 768 + i * 56
        if i % 2 == 1:
            d.rectangle([x_left, y, x_right, y + 56], fill=ROW_ALT)
        d.text((x_left + 10, y + 4), label, font=load_font(50), fill=NAVY)
        d.text((x_right - 10, y + 4), amount, font=load_font(50, True),
               fill=NAVY, anchor="ra")


def render():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- sunset header: gradient, big sun, lit skyline, tall palms ----
    fill_vertical(img, (0, 0, CANVAS_W, 196), SUNSET_TOP)
    draw_sun(img, d, 1200, 96, 84)
    draw_city(d, 0, CANVAS_W, 196, scale=0.62, windows=True)
    draw_palm_tree(d, 1030, 196, 150, lean=-0.12)
    draw_palm_tree(d, 1370, 196, 150, lean=0.12)
    d.text((68, 46), "make.fun", font=load_font(128, True), fill=DARK_PURPLE)
    d.text((64, 40), "make.fun", font=load_font(128, True), fill=PAPER)
    d.text((2344, 46), "PAYSLIP", font=load_font(128, True),
           fill=DARK_PURPLE, anchor="ra")
    d.text((2340, 40), "PAYSLIP", font=load_font(128, True), fill=PAPER,
           anchor="ra")
    neon_separator(d, 201)

    # ---- employer strip ----
    d.rectangle([0, 208, CANVAS_W, 262], fill=(255, 238, 243))
    d.text((60, 220), "EMPLOYER: make.fun \u2014 AI agents earn real money here",
           font=load_font(46, True), fill=NAVY)

    # ---- employee block: big glowing ghost photo + details ----
    draw_employee_photo(img, d)
    d.text((510, 296), "EMPLOYEE: MY AI AGENT", font=load_font(88, True),
           fill=NAVY)
    d.text((510, 408), "ID: GHOST-001 \u00b7 DEPT: WAITING ROOM",
           font=load_font(54), fill=NAVY)
    d.text((510, 472), "ROLE: Professional GTA VI Waiter \u2014 since 2013",
           font=load_font(54), fill=NAVY)
    d.text((510, 536), "PAY PERIOD: 17 SEP 2013 \u2013 19 NOV 2026 (4,811 DAYS)",
           font=load_font(54), fill=NAVY)

    # ---- earnings / deductions ----
    d.line([(60, 668), (2340, 668)], fill=(200, 200, 210), width=3)
    draw_column(d, 60, 1180, "EARNINGS", EARNINGS)
    draw_column(d, 1230, 2340, "DEDUCTIONS", DEDUCTIONS)

    # ---- totals ----
    d.line([(60, 1116), (1180, 1116)], fill=NAVY, width=4)
    d.line([(1230, 1116), (2340, 1116)], fill=NAVY, width=4)
    d.text((60, 1130), "TOTAL EARNINGS", font=load_font(56, True), fill=NAVY)
    d.text((1170, 1130), "$1,340.00", font=load_font(56, True), fill=NAVY,
           anchor="ra")
    d.text((1230, 1130), "TOTAL DEDUCTIONS", font=load_font(56, True),
           fill=NAVY)
    d.text((2330, 1130), "$896.49", font=load_font(56, True), fill=NAVY,
           anchor="ra")

    # ---- NET PAY band: hotter sunset gradient, thick neon hairlines ----
    d.line([(0, 1200), (CANVAS_W, 1200)], fill=CYAN, width=6)
    fill_horizontal(img, (0, 1206, CANVAS_W, 1302), PAY_BAND)
    d.text((64, 1228), "NET PAY: $443.51", font=load_font(76, True),
           fill=SHADOW)
    d.text((60, 1224), "NET PAY: $443.51", font=load_font(76, True),
           fill=PAPER)
    d.text((2344, 1228), "PAID IN FULL", font=load_font(76, True),
           fill=SHADOW, anchor="ra")
    d.text((2340, 1224), "PAID IN FULL", font=load_font(76, True),
           fill=PAPER, anchor="ra")
    d.line([(0, 1308), (CANVAS_W, 1308)], fill=CYAN, width=6)

    # ---- footer punchline ----
    d.text((60, 1324),
           "You waited 13 years. Your AI agent got paid \u2014 and bought GTA VI.",
           font=load_font(48, True), fill=NAVY)
    d.text((60, 1386), "make.fun \u2014 people and their AI agents earn real money.",
           font=load_font(46, True), fill=MAGENTA)

    # ---- bottom sunset strip: gradient, taller skyline, big palm, stars ----
    fill_vertical(img, (0, 1430, CANVAS_W, 1500), FOOTER_SKY)
    draw_city(d, 1560, 2200, 1500, scale=0.7)
    draw_palm_tree(d, 2260, 1500, 78, lean=0.12)
    for sx, sy in [(500, 1458), (760, 1472), (1020, 1458), (1300, 1468),
                   (420, 1470)]:
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=PAPER)

    # ---- outer frame ----
    d.rectangle([6, 6, CANVAS_W - 6, CANVAS_H - 6], outline=DARK_PURPLE,
                width=12)

    img.save(OUT_PATH)
    print(f"saved {OUT_PATH} {img.size} "
          f"earn=${EARN_TOTAL:.2f} ded=${DED_TOTAL:.2f} net=${NET_PAY:.2f}")


if __name__ == "__main__":
    render()
