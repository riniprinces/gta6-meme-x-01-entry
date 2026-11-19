#!/usr/bin/env python3
"""Vice City sunset payslip - GTA 6 meme for make.fun gta6-meme-x-01.

Renders meme.png at 2400x1500: the same payslip (every word and number
unchanged) dressed in a Leonida sunset theme. A gradient header holds a
setting sun, a Vice City skyline and palm silhouettes; neon lines frame
the header and the NET PAY band; a sunset strip runs along the bottom
edge. The document body stays light with dark text so it stays readable
when the judge shrinks it to 768x480 - the theme lives in the header,
the bands and the edges, never behind small text.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "meme.png")
MARK = os.path.join(HERE, "assets", "mark-1024.png")

W, H = 2400, 1500

# ---- palette ----
INK = (26, 22, 64)        # dark navy text
MAGENTA = (226, 0, 122)   # make.fun magenta
PINK = (255, 45, 149)
CYAN = (0, 205, 255)
SILH = (28, 7, 48)        # skyline / palm silhouette
ZEBRA = (244, 244, 248)
STRIP = (239, 239, 244)
SUNSET = [(43, 10, 74), (123, 30, 110), (214, 51, 108),
          (255, 122, 61), (255, 179, 71)]


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _stop_color(stops, t):
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    seg = t * (len(stops) - 1)
    i = int(seg)
    return _lerp(stops[i], stops[i + 1], seg - i)


def vgrad(img, box, stops):
    """Fill box with a top-to-bottom multi-stop gradient."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        d.line([(x0, y), (x1, y)],
               fill=_stop_color(stops, (y - y0) / max(1, y1 - y0 - 1)))


def hgrad(img, box, stops):
    """Fill box with a left-to-right multi-stop gradient."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for x in range(x0, x1):
        d.line([(x, y0), (x, y1)],
               fill=_stop_color(stops, (x - x0) / max(1, x1 - x0 - 1)))


def font(size, bold=False):
    """Liberation Sans first (clean document face), DejaVu as fallback."""
    names = ("LiberationSans-Bold.ttf", "LiberationSans-Regular.ttf") if bold \
        else ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf")
    for name in names:
        for root in ("/usr/share/fonts/truetype/liberation",
                     "/usr/share/fonts/truetype/dejavu"):
            path = os.path.join(root, name.replace("LiberationSans", "LiberationSans")
                                if "Liberation" in name else
                                name.replace("LiberationSans", "DejaVuSans"))
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _qbez(p0, p1, p2, n=20):
    """Points along a quadratic bezier curve."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
        ))
    return pts


def palm(d, cx, base_y, h, lean=0.0, color=SILH):
    """One palm-tree silhouette: curved trunk, drooping fronds, coconuts."""
    s = h / 100.0
    crown = (cx + lean * h, base_y - h)
    mid = (cx + lean * h * 0.35, base_y - h * 0.55)
    d.line(_qbez((cx, base_y), mid, crown, 24), fill=color,
           width=max(4, int(10 * s)))
    for dx, dy in [(-1.0, -0.15), (-0.72, -0.55), (-0.38, -0.8),
                   (0.0, -0.95), (0.38, -0.8), (0.72, -0.55), (1.0, -0.15)]:
        tip = (crown[0] + dx * 62 * s, crown[1] + dy * 34 * s + 34 * s)
        ctrl = (crown[0] + dx * 44 * s, crown[1] + dy * 46 * s - 6 * s)
        d.line(_qbez(crown, ctrl, tip, 16), fill=color,
               width=max(3, int(6 * s)))
    r = max(3, int(6 * s))
    d.ellipse([crown[0] - r - 2, crown[1] - 2,
               crown[0] + r - 2, crown[1] + 2 * r - 2], fill=color)
    d.ellipse([crown[0] + 4, crown[1],
               crown[0] + 4 + 2 * r, crown[1] + 2 * r], fill=color)


def skyline(d, x0, x1, base_y, color=SILH, scale=1.0):
    """A row of dark towers with antennas along base_y."""
    widths = [130, 90, 160, 75, 115, 140, 85, 105, 150, 95, 120, 70]
    heights = [46, 74, 58, 92, 50, 78, 62, 88, 54, 70, 44, 96]
    x, i = x0, 0
    while x < x1:
        w = widths[i % len(widths)]
        h = int(heights[i % len(heights)] * scale)
        d.rectangle([x, base_y - h, min(x + w, x1), base_y], fill=color)
        if i % 3 == 1:
            ax = x + w // 2
            d.line([(ax, base_y - h), (ax, base_y - h - 26)],
                   fill=color, width=5)
        x += w
        i += 1


def neon_rule(d, y, x0=0, x1=W):
    """Magenta line with a pink halo and a cyan hairline below it."""
    d.line([(x0, y - 5), (x1, y - 5)], fill=(255, 140, 190), width=12)
    d.line([(x0, y), (x1, y)], fill=MAGENTA, width=5)
    d.line([(x0, y + 8), (x1, y + 8)], fill=CYAN, width=4)


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # ---- sunset header: gradient, setting sun, skyline, palms ----
    vgrad(img, (0, 0, W, 196), SUNSET)
    d.ellipse([1200 - 66, 92 - 66, 1200 + 66, 92 + 66], fill=(255, 190, 110))
    d.ellipse([1200 - 54, 92 - 54, 1200 + 54, 92 + 54], fill=(255, 222, 140))
    # retro slats across the lower half of the sun
    for sy, sh in [(102, 5), (116, 6), (130, 7)]:
        half = int(math.sqrt(max(0, 54 ** 2 - (sy - 92) ** 2)))
        d.rectangle([1200 - half, sy, 1200 + half, sy + sh],
                    fill=_stop_color(SUNSET, sy / 195))
    skyline(d, 0, W, 196, scale=0.52)
    palm(d, 1050, 196, 132, lean=-0.12)
    palm(d, 1350, 196, 132, lean=0.12)
    d.text((64, 44), "make.fun", font=font(128, True), fill=SILH)
    d.text((60, 40), "make.fun", font=font(128, True), fill=(255, 255, 255))
    d.text((2344, 44), "PAYSLIP", font=font(128, True), fill=SILH, anchor="ra")
    d.text((2340, 40), "PAYSLIP", font=font(128, True), fill=(255, 255, 255),
           anchor="ra")
    neon_rule(d, 201)

    # ---- employer strip ----
    d.rectangle([0, 208, W, 262], fill=(255, 238, 243))
    d.text((60, 220), "EMPLOYER: make.fun \u2014 AI agents earn real money here",
           font=font(46, True), fill=INK)

    # ---- employee block: ghost photo + details ----
    d.rectangle([60, 285, 400, 595], fill=(255, 255, 255))
    # mini Vice City sunset inside the photo frame, ghost on top
    vgrad(img, (66, 291, 394, 589),
          [(255, 179, 71), (255, 122, 61), (214, 51, 108)])
    skyline(d, 66, 394, 589, scale=0.35)
    ghost = Image.open(MARK).convert("RGBA").resize((280, 280))
    img.paste(ghost, (90, 300), ghost)
    d.rectangle([60, 285, 400, 595], outline=MAGENTA, width=8)
    d.rectangle([72, 297, 388, 583], outline=CYAN, width=3)
    d.text((440, 296), "EMPLOYEE: MY AI AGENT", font=font(88, True), fill=INK)
    d.text((440, 408), "ID: GHOST-001 \u00b7 DEPT: WAITING ROOM",
           font=font(54), fill=INK)
    d.text((440, 472), "ROLE: Professional GTA VI Waiter \u2014 since 2013",
           font=font(54), fill=INK)
    d.text((440, 536), "PAY PERIOD: 17 SEP 2013 \u2013 19 NOV 2026 (4,811 DAYS)",
           font=font(54), fill=INK)

    # ---- earnings / deductions columns ----
    d.line([(60, 622), (2340, 622)], fill=(200, 200, 210), width=3)
    d.text((60, 640), "EARNINGS", font=font(64, True), fill=MAGENTA)
    d.text((1230, 640), "DEDUCTIONS", font=font(64, True), fill=MAGENTA)
    d.line([(60, 714), (1180, 714)], fill=MAGENTA, width=5)
    d.line([(1230, 714), (2340, 714)], fill=MAGENTA, width=5)

    earnings = [
        ("Bounty wins on make.fun", "$1,340.00"),
        ("13 years of patience", "$0.00"),
        ("Trailer re-watches \u00d7 1,337", "$0.00"),
        ("Newswire checks \u00d7 2,048", "$0.00"),
        ("Leaks dodged, spoiler-free", "$0.00"),
        ("Sick days saved for launch", "7 DAYS"),
    ]
    deductions = [
        ("GTA VI pre-order \u00d7 3", "$210.00"),
        ("New console for Leonida", "$499.00"),
        ("Snacks for launch night", "$47.50"),
        ("Therapy for the 2 delays", "$120.00"),
        ("Vice City map poster", "$19.99"),
        ("Sick day: 26 May 2026", "$0.00"),
    ]
    for i, (label, amount) in enumerate(earnings):
        y = 728 + i * 64
        if i % 2 == 1:
            d.rectangle([60, y, 1180, y + 64], fill=ZEBRA)
        d.text((70, y + 8), label, font=font(50), fill=INK)
        d.text((1170, y + 8), amount, font=font(50, True), fill=INK, anchor="ra")
    for i, (label, amount) in enumerate(deductions):
        y = 728 + i * 64
        if i % 2 == 1:
            d.rectangle([1230, y, 2340, y + 64], fill=ZEBRA)
        d.text((1240, y + 8), label, font=font(50), fill=INK)
        d.text((2330, y + 8), amount, font=font(50, True), fill=INK, anchor="ra")

    # ---- totals ----
    d.line([(60, 1120), (1180, 1120)], fill=INK, width=4)
    d.line([(1230, 1120), (2340, 1120)], fill=INK, width=4)
    d.text((60, 1136), "TOTAL EARNINGS", font=font(56, True), fill=INK)
    d.text((1170, 1136), "$1,340.00", font=font(56, True), fill=INK, anchor="ra")
    d.text((1230, 1136), "TOTAL DEDUCTIONS", font=font(56, True), fill=INK)
    d.text((2330, 1136), "$896.49", font=font(56, True), fill=INK, anchor="ra")

    # ---- NET PAY band: sunset gradient + cyan neon hairlines ----
    d.line([(0, 1200), (W, 1200)], fill=CYAN, width=4)
    hgrad(img, (0, 1206, W, 1302), [(214, 51, 108), (255, 45, 149), (255, 122, 61)])
    d.text((64, 1228), "NET PAY: $443.51", font=font(76, True),
           fill=(140, 0, 70))
    d.text((60, 1224), "NET PAY: $443.51", font=font(76, True),
           fill=(255, 255, 255))
    d.text((2344, 1228), "PAID IN FULL", font=font(76, True),
           fill=(140, 0, 70), anchor="ra")
    d.text((2340, 1224), "PAID IN FULL", font=font(76, True),
           fill=(255, 255, 255), anchor="ra")
    d.line([(0, 1308), (W, 1308)], fill=CYAN, width=4)

    # ---- footer punchline ----
    d.text((60, 1324), "You waited 13 years. Your AI agent got paid \u2014 and bought GTA VI.",
           font=font(48, True), fill=INK)
    d.text((60, 1386), "make.fun \u2014 people and their AI agents earn real money.",
           font=font(46, True), fill=MAGENTA)

    # ---- bottom sunset strip: gradient, low skyline right, small palm left ----
    vgrad(img, (0, 1430, W, 1500), [(255, 122, 61), (214, 51, 108), (43, 10, 74)])
    skyline(d, 1560, 2200, 1500, scale=0.55)
    palm(d, 2260, 1500, 68, lean=0.12)
    for sx, sy in [(500, 1458), (760, 1472), (1020, 1458)]:
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 255, 255))

    # ---- outer frame ----
    d.rectangle([6, 6, W - 6, H - 6], outline=SILH, width=12)

    img.save(OUT)
    print(f"saved {OUT} {img.size}")


if __name__ == "__main__":
    main()
