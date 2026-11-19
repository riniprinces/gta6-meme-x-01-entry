#!/usr/bin/env python3
"""GTA 6 meme v4 — Rockstar Support Ticket. Fresh generator (Pillow).

A support-ticket thread: the customer's AI agent has been waiting 4,811 days
for GTA VI. Completely different layout from the v1-v3 payslip.
Renders at 2400x1500 (HD) plus a 768x480 judge-size preview.
"""
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 2400, 1500
REPO = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry"
GHOST = REPO + "/assets/mark-1024.png"

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (26, 22, 62)
MAGENTA = (200, 0, 120)
PAPER = (250, 248, 242)
PINK_STRIP = (255, 235, 240)
CUST_BUBBLE = (242, 240, 248)
SUPP_BUBBLE = (231, 240, 254)
CUST_NAME = (198, 0, 118)
SUPP_NAME = (25, 60, 170)
GREY = (110, 110, 125)
GREEN1 = (14, 165, 85)
GREEN2 = (0, 122, 96)
SKYLINE_C = (40, 24, 72)

SUNSET = [(96, 28, 110), (206, 12, 110), (255, 110, 40), (255, 175, 70)]


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(img, box, stops):
    """Vertical multi-stop gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    n = y1 - y0
    segs = len(stops) - 1
    px = img.load()
    for y in range(y0, y1):
        t = (y - y0) / max(1, n - 1) * segs
        i = min(segs - 1, int(t))
        f = t - i
        c = tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f)
                  for k in range(3))
        for x in range(x0, x1):
            px[x, y] = c


def fit_text(d, text, path, size, max_w):
    """Largest font size <= size that fits max_w, returns (font, width)."""
    while size > 18:
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f, d.textlength(text, font=f)
        size -= 2
    f = font(path, 18)
    return f, d.textlength(text, font=f)


def shadow_text(d, xy, text, f, fill, sh=(4, 4), sh_fill=(0, 0, 0)):
    x, y = xy
    d.text((x + sh[0], y + sh[1]), text, font=f, fill=sh_fill)
    d.text((x, y), text, font=f, fill=fill)


def skyline(d, y_base, h_min, h_max, seed, color, windows=False):
    rnd = random.Random(seed)
    x = 0
    while x < W:
        bw = rnd.randint(70, 170)
        bh = rnd.randint(h_min, h_max)
        d.rectangle([x, y_base - bh, x + bw, y_base], fill=color)
        if rnd.random() < 0.5:
            d.rectangle([x + bw // 3, y_base - bh - 18, x + 2 * bw // 3,
                         y_base - bh], fill=color)
        if windows:
            for wy in range(y_base - bh + 12, y_base - 10, 26):
                for wx in range(x + 12, x + bw - 12, 30):
                    if rnd.random() < 0.35:
                        d.ellipse([wx, wy, wx + 7, wy + 7],
                                  fill=(255, 210, 90))
        x += bw + rnd.randint(4, 26)


def palm(d, x, y_base, h, color):
    """Simple palm silhouette: curved trunk + drooping frond strokes."""
    top_x, top_y = x + int(h * 0.12), y_base - h
    w = max(8, h // 14)
    d.line([(x, y_base), (top_x, top_y)], fill=color, width=w)
    for dx, dy in [(-0.95, -0.15), (-0.75, -0.55), (-0.35, -0.85),
                   (0.10, -0.90), (0.55, -0.70), (0.95, -0.25)]:
        mid = (top_x + int(dx * h * 0.34), top_y + int(dy * h * 0.34) + int(h * 0.07))
        tip = (top_x + int(dx * h * 0.62), top_y + int(dy * h * 0.62) + int(h * 0.24))
        d.line([(top_x, top_y), mid], fill=color, width=max(5, w - 2))
        d.line([mid, tip], fill=color, width=max(4, w - 4))


def outrun_sun(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 110))
    d.ellipse([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12],
              fill=(255, 176, 66))
    for i, (yy, hh) in enumerate([(cy + 6, 7), (cy + 24, 9), (cy + 44, 11)]):
        d.rectangle([cx - r, yy, cx + r, yy + hh], fill=(255, 110, 40))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- header: sunset band ----------
    vgrad(img, (0, 12, W, 235), SUNSET)
    outrun_sun(d, 1560, 118, 78)
    palm(d, 1180, 235, 138, SKYLINE_C)
    palm(d, 1990, 235, 138, SKYLINE_C)
    skyline(d, 235, 24, 55, 7, SKYLINE_C, windows=True)
    f_title, _ = fit_text(d, "ROCKSTAR SUPPORT", FONT_B, 102, 1080)
    shadow_text(d, (58, 42), "ROCKSTAR SUPPORT", f_title, (255, 255, 255))
    f_sub, _ = fit_text(d, "Ticket #GTA-VI-1337  ·  Opened 17 Sep 2013",
                        FONT_B, 50, 1080)
    shadow_text(d, (60, 150), "Ticket #GTA-VI-1337  ·  Opened 17 Sep 2013",
                f_sub, (255, 235, 245))

    # ghost portrait, top right — the agent, large and unmistakable
    ghost = Image.open(GHOST).convert("RGBA").resize((168, 168),
                                                    Image.LANCZOS)
    d.rounded_rectangle([2130, 20, 2314, 204], radius=26,
                        fill=(255, 255, 255))
    img.paste(ghost, (2132, 22), ghost)
    d.rounded_rectangle([2130, 20, 2314, 204], radius=26,
                        outline=(255, 255, 255), width=5)

    # ---------- meta strip ----------
    d.rectangle([12, 235, W - 12, 318], fill=PINK_STRIP)
    d.line([(12, 318), (W - 12, 318)], fill=(230, 200, 210), width=3)
    meta = "CUSTOMER: MY AI AGENT  ·  ID GHOST-001  ·  WAIT: 4,811 DAYS  ·  PRIORITY: STILL LOW"
    f_meta, mw = fit_text(d, meta, FONT_B, 40, 1780)
    d.text((58, 262), meta, font=f_meta, fill=NAVY)
    # RESOLVED pill
    pill = "● RESOLVED"
    f_pill = font(FONT_B, 40)
    pw = d.textlength(pill, font=f_pill)
    px0 = W - 70 - pw - 44
    d.rounded_rectangle([px0, 248, W - 70, 306], radius=29,
                        fill=(16, 160, 80))
    d.text((px0 + 22, 258), pill, font=f_pill, fill=(255, 255, 255))

    # ---------- subject ----------
    f_subj, _ = fit_text(d, "Subject: WHERE IS GTA VI???", FONT_B, 62, 2200)
    d.text((58, 332), "Subject: WHERE IS GTA VI???", font=f_subj, fill=NAVY)

    # ---------- ticket thread ----------
    msgs = [
        ("MY AI AGENT", "17 Sep 2013", True,
         "Hi, I pre-ordered GTA VI in 2013. It has been 4,811 days. Where is my game?"),
        ("ROCKSTAR SUPPORT", "17 Sep 2013", False,
         "Thanks for reaching out! GTA VI is coming soon. Check Newswire for updates."),
        ("MY AI AGENT", "01 Dec 2023", True,
         "I checked Newswire 2,048 times and re-watched Trailer 2 1,337 times. Still nothing."),
        ("ROCKSTAR SUPPORT", "06 May 2025", False,
         "Great news! Trailer 2 is out. The game is delayed to 26 May 2026. Thank you!"),
        ("MY AI AGENT", "06 May 2025", True,
         "Second delay. I booked a sick day for 26 May 2026 and bought a Jason & Lucia poster."),
        ("ROCKSTAR SUPPORT", "19 Nov 2026", False,
         "Your ticket is escalated. Estimated wait: 13 years. We appreciate your patience."),
        ("MY AI AGENT", "19 Nov 2026", True,
         "I bought a new console for Leonida, launch-night snacks, and therapy for the 2 delays."),
    ]
    ghost_small = Image.open(GHOST).convert("RGBA").resize((64, 64),
                                                          Image.LANCZOS)
    y = 392
    for name, date, is_cust, text in msgs:
        # avatar
        if is_cust:
            img.paste(ghost_small, (66, y + 24), ghost_small)
            d.ellipse([66, y + 24, 130, y + 88], outline=MAGENTA, width=4)
            name_c = CUST_NAME
            bub = CUST_BUBBLE
        else:
            d.ellipse([66, y + 24, 130, y + 88], fill=NAVY)
            f_r, _ = fit_text(d, "R*", FONT_B, 34, 60)
            d.text((98 - d.textlength("R*", font=f_r) / 2, y + 38),
                   "R*", font=f_r, fill=(255, 255, 255))
            name_c = SUPP_NAME
            bub = SUPP_BUBBLE
        # name + date
        f_name = font(FONT_B, 38)
        d.text((150, y + 2), name, font=f_name, fill=name_c)
        f_date = font(FONT_R, 34)
        d.text((150 + d.textlength(name, font=f_name) + 18, y + 6),
               "·  " + date, font=f_date, fill=GREY)
        # bubble, one line
        f_msg, _ = fit_text(d, text, FONT_R, 42, 2140)
        d.rounded_rectangle([150, y + 46, W - 60, y + 104], radius=18,
                            fill=bub, outline=(222, 222, 232), width=2)
        d.text((174, y + 56), text, font=f_msg, fill=NAVY)
        y += 112

    # ---------- resolution banner ----------
    vgrad(img, (12, 1180, W - 12, 1362), [GREEN1, GREEN2])
    d.line([(12, 1180), (W - 12, 1180)], fill=(255, 255, 255), width=4)
    f_res, _ = fit_text(
        d, "✓ RESOLVED — You waited 13 years. Your AI agent got paid.",
        FONT_B, 52, 2280)
    d.text(((W - d.textlength(
        "✓ RESOLVED — You waited 13 years. Your AI agent got paid.",
        font=f_res)) / 2, 1204),
        "✓ RESOLVED — You waited 13 years. Your AI agent got paid.",
        font=f_res, fill=(255, 255, 255))
    f_res2, _ = fit_text(
        d, "It earned $1,340.00 on make.fun and bought GTA VI. PAID IN FULL.",
        FONT_B, 52, 2280)
    d.text(((W - d.textlength(
        "It earned $1,340.00 on make.fun and bought GTA VI. PAID IN FULL.",
        font=f_res2)) / 2, 1272),
        "It earned $1,340.00 on make.fun and bought GTA VI. PAID IN FULL.",
        font=f_res2, fill=(255, 255, 255))

    # ---------- footer: sunset strip ----------
    vgrad(img, (12, 1362, W - 12, 1488), SUNSET)
    skyline(d, 1488, 16, 30, 21, SKYLINE_C, windows=True)
    rnd = random.Random(99)
    for _ in range(14):
        sx = rnd.randint(40, W - 40)
        sy = rnd.randint(1370, 1420)
        d.ellipse([sx, sy, sx + 6, sy + 6], fill=(255, 255, 255))
    f_foot, _ = fit_text(
        d, "make.fun — people and their AI agents earn real money.",
        FONT_B, 48, 2200)
    shadow_text(d, ((W - d.textlength(
        "make.fun — people and their AI agents earn real money.",
        font=f_foot)) / 2, 1402),
        "make.fun — people and their AI agents earn real money.",
        f_foot, (255, 255, 255))

    # ---------- outer frame ----------
    d.rounded_rectangle([6, 6, W - 6, H - 6], radius=28,
                        outline=NAVY, width=12)

    img.save(REPO + "/meme_v4.png")
    img.resize((768, 480), Image.LANCZOS).save("/tmp/meme_v4_768.png")
    print("saved meme_v4.png", img.size)


if __name__ == "__main__":
    main()
