#!/usr/bin/env python3
"""draw_v5.py — overlay crisp GTA-style text onto the generated v5 base scene.

Writes meme_v5.png (1920x1280) + a 768x512 judge-size preview.
All coordinates measured from the actual base image via a grid overlay.
Run: python3 draw_v5.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

REPO = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry"
BASE = f"{REPO}/v5-base.png"
OUT = f"{REPO}/meme_v5.png"
PREVIEW = "/tmp/meme_v5_judge.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
BLACK = (0, 0, 0)
DARK_BROWN = (46, 32, 24)
INK = (20, 20, 30)
RED = (230, 20, 30)


def font(size):
    return ImageFont.truetype(BOLD, size)


def fit(draw, text, max_w, start, step=2, min_size=20):
    """Largest bold font size whose rendered width fits max_w."""
    size = start
    while size > min_size:
        f = font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= step
    return font(min_size)


def outlined(d, xy, text, f, fill, stroke=4):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLACK)


def main():
    im = Image.open(BASE).convert("RGB")
    W, H = im.size
    assert (W, H) == (1920, 1280), (W, H)
    # subtle pop: a touch more colour and contrast
    im = ImageEnhance.Color(im).enhance(1.07)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    d = ImageDraw.Draw(im)

    # ---- 1. Top title (single line, top sky strip, clears the board + helicopter)
    title_a = "13 YEARS STILL PLAYING "
    title_b = "GTA..."
    f = fit(d, title_a + title_b, 960, 62)
    w_a = d.textlength(title_a, font=f)
    tx, ty = 125, 14
    outlined(d, (tx, ty), title_a, f, WHITE, stroke=4)
    outlined(d, (tx + w_a, ty), title_b, f, YELLOW, stroke=4)
    print("title font size:", f.size, "width:", d.textlength(title_a + title_b, font=f))

    # ---- 2. Ghost's black board: "13 YEARS" / "4,811 DAYS", rotated to board tilt (+5 deg)
    layer = Image.new("RGBA", (760, 420), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f1 = fit(ld, "13 YEARS", 320, 60)
    f2 = fit(ld, "4,811 DAYS", 320, 52)
    # centre the two-line block vertically in the layer so it lands mid-board
    block_h = f1.size + 18 + f2.size
    y = (420 - block_h) // 2
    for txt, ff in (("13 YEARS", f1), ("4,811 DAYS", f2)):
        w = ld.textlength(txt, font=ff)
        ld.text(((760 - w) / 2, y), txt, font=ff, fill=WHITE)
        y += ff.size + 18
    print("board fonts:", f1.size, f2.size)
    rot = layer.rotate(5, expand=True, resample=Image.BICUBIC)
    im.paste(rot, (400 - rot.width // 2, 300 - rot.height // 2), rot)

    # ---- 3. Dog's cardboard: "DELAYED" / "AGAIN..." (ALL text in English per user rule)
    cx, cy = 1500, 975
    f3 = fit(d, "DELAYED", 300, 62)
    lh = f3.size + 8
    total_h = 2 * lh
    y = cy - total_h // 2
    for txt in ("DELAYED", "AGAIN..."):
        w = d.textlength(txt, font=f3)
        d.text((cx - w / 2, y), txt, font=f3, fill=DARK_BROWN)
        y += lh
    print("cardboard font size:", f3.size)

    # ---- 4. Desk calendar: "SICK DAY" / "26 MAY" with red circle around 26 MAY
    cal_cx = 280
    f4 = fit(d, "SICK DAY", 320, 44)
    w = d.textlength("SICK DAY", font=f4)
    d.text((cal_cx - w / 2, 895), "SICK DAY", font=f4, fill=INK)
    f5 = fit(d, "26 MAY", 320, 60)
    w = d.textlength("26 MAY", font=f5)
    top5 = 950
    d.text((cal_cx - w / 2, top5), "26 MAY", font=f5, fill=INK)
    # red ellipse circled around "26 MAY"
    d.ellipse([cal_cx - w / 2 - 18, top5 - 8, cal_cx + w / 2 + 18, top5 + f5.size + 14],
              outline=RED, width=7)
    print("calendar fonts:", f4.size, f5.size)

    # ---- 5. Bottom punchline, centred on the car hood
    px = 885
    f6 = fit(d, "...AND STILL", 780, 92)
    w = d.textlength("...AND STILL", font=f6)
    outlined(d, (px - w / 2, 1040), "...AND STILL", f6, WHITE, stroke=5)
    f7 = fit(d, "DELAYED", 560, 120)
    w = d.textlength("DELAYED", font=f7)
    ey = 1138
    ex = px - (w + 20 + 109) / 2
    outlined(d, (ex, ey), "DELAYED", f7, YELLOW, stroke=6)
    ef = ImageFont.truetype(EMOJI, 109)  # NotoColorEmoji only loads at size 109 here
    d.text((ex + w + 20, ey + 8), "\U0001F602", font=ef, embedded_color=True)
    print("punchline fonts:", f6.size, f7.size)

    # ---- 6. GTA minimap, bottom-right corner
    mx, my, r = 1835, 1175, 56
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(10, 22, 38), outline=WHITE, width=3)
    # street grid inside the circle (clipped by drawing only short segments)
    for (x1, y1, x2, y2) in [
        (mx - 44, my - 18, mx + 44, my - 26),
        (mx - 40, my + 14, mx + 46, my + 6),
        (mx - 12, my - 48, mx - 20, my + 48),
        (mx + 22, my - 44, mx + 16, my + 46),
    ]:
        d.line([(x1, y1), (x2, y2)], fill=(90, 130, 170), width=3)
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(255, 60, 170))  # player dot
    d.ellipse([mx + 24 - 5, my - 30 - 5, mx + 24 + 5, my - 30 + 5], fill=(255, 210, 0))  # objective
    nf = font(16)
    d.text((mx - 6, my - r + 4), "N", font=nf, fill=WHITE)

    # ---- 7. GTA money pickup: "+$1,340.00" floating above the ghost's coin hand,
    # plus two small floating "$" — the cash the agent earned on make.fun
    GREEN = (70, 220, 90)
    f8 = fit(d, "+$1,340.00", 430, 62)
    outlined(d, (1180, 520), "+$1,340.00", f8, GREEN, stroke=5)
    f9 = font(40)
    outlined(d, (1085, 560), "$", f9, GREEN, stroke=4)
    outlined(d, (1310, 480), "$", f9, GREEN, stroke=4)
    print("money pickup font size:", f8.size)

    # ---- 8. License plate "MAKEFUN" on the front edge of the hood
    plate = [1305, 1212, 1535, 1270]
    d.rounded_rectangle(plate, radius=8, fill=(245, 245, 240), outline=(20, 20, 30), width=4)
    f10 = fit(d, "MAKEFUN", 210, 46)
    w = d.textlength("MAKEFUN", font=f10)
    d.text(((plate[0] + plate[2] - w) / 2, plate[1] + 6), "MAKEFUN",
           font=f10, fill=(20, 40, 90))
    print("plate font size:", f10.size)

    im.save(OUT)
    im.resize((768, 512), Image.LANCZOS).save(PREVIEW)
    print("saved", OUT, im.size)
    print("saved", PREVIEW)


if __name__ == "__main__":
    main()
