#!/usr/bin/env python3
"""draw_v5.py — overlay crisp GTA-style text onto the generated v5 base scene.

v5.1 (text fix): all text bigger, one display font (Liberation Sans Bold),
thicker clean black outlines, drop shadows on title + punchline, vivid
yellow/white title, floating "$" removed, board + cardboard text re-centred
on their measured quads, MAKEFUN plate restyled as a real plate, official
make.fun logo badge top-left.

Writes meme_v5.png (1920x1280) + a 768x512 judge-size preview.
All coordinates measured from the actual base image (grid crops + profiles).
Run: python3 draw_v5.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

REPO = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry"
BASE = f"{REPO}/v5-base.png"
MARK = f"{REPO}/assets/mark-1024.png"
OUT = f"{REPO}/meme_v5.png"
PREVIEW = "/tmp/meme_v5_judge.png"

# One display font for every overlay: Liberation Sans Bold (Arial-like poster
# face — narrower than DejaVu Bold, so everything can be set bigger).
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

WHITE = (255, 255, 255)
YELLOW = (255, 225, 0)          # vivid yellow (title / DELAYED)
GREEN = (60, 215, 80)           # vivid money green
BLACK = (0, 0, 0)
INK = (20, 20, 30)
RED = (230, 20, 30)
SHADOW = (12, 8, 20)            # drop-shadow colour
DARK_BROWN = (30, 20, 12)       # cardboard text
CARD_OUTLINE = (238, 222, 195)  # subtle light outline on cardboard
NAVY = (20, 40, 90)


def font(size):
    return ImageFont.truetype(BOLD, size)


def outlined(d, xy, text, f, fill, stroke=5):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLACK)


def shadowed(d, xy, text, f, fill, stroke=7, dx=5, dy=6):
    """Drop shadow + thick-outlined display text. Shadow first, then main."""
    x, y = xy
    d.text((x + dx, y + dy), text, font=f, fill=SHADOW)
    outlined(d, (x, y), text, f, fill, stroke=stroke)


def main():
    im = Image.open(BASE).convert("RGB")
    W, H = im.size
    assert (W, H) == (1920, 1280), (W, H)
    # subtle pop: a touch more colour and contrast
    im = ImageEnhance.Color(im).enhance(1.07)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    d = ImageDraw.Draw(im)

    # ---- 0. Official make.fun logo badge, top-left (mark is the real press
    # kit mark: white ghost on a magenta disc with a black ring). White
    # circular backing + soft shadow so it pops against the sunset palms.
    # v5.2: badge enlarged to Ø170 (was Ø124) — clearly bigger, still fits
    # the corner cleanly; title shifted right so nothing collides.
    mark = Image.open(MARK).convert("RGBA")
    bcx, bcy, br = 96, 92, 85
    d.ellipse([bcx - br - 5, bcy - br - 2, bcx + br + 5, bcy + br + 8],
              fill=(20, 12, 25))
    d.ellipse([bcx - br, bcy - br, bcx + br, bcy + br],
              fill=WHITE, outline=(30, 20, 40), width=4)
    m = mark.resize((150, 150), Image.LANCZOS)
    im.paste(m, (bcx - 75, bcy - 75), m)
    print("logo badge: centre", (bcx, bcy), "radius", br, "diameter", br * 2)

    # ---- 1. Top title, one clean line after the badge. Bigger (70), thick
    # outline, drop shadow, vivid yellow on "GTA...". v5.2: shifted right to
    # x=200 so the enlarged Ø170 badge clears it (title ends ~1294, still
    # clear of the helicopter).
    title_a = "13 YEARS STILL PLAYING "
    title_b = "GTA..."
    f = font(70)
    w_a = d.textlength(title_a, font=f)
    w_b = d.textlength(title_b, font=f)
    tx, ty = 200, 12
    print("title width:", round(w_a + w_b), "ends at x:", round(tx + w_a + w_b))
    shadowed(d, (tx, ty), title_a, f, WHITE, stroke=7)
    shadowed(d, (tx + w_a, ty), title_b, f, YELLOW, stroke=7)

    # ---- 2. Ghost's black board: "13 YEARS" / "4,811 DAYS".
    # Measured board quad: a parallelogram tilted ~15 deg CCW, face centre
    # ~(475, 305), top-edge length ~360. Text block condensed 0.9x so the
    # wide line fits with real margins, rotated +15 to sit on the board.
    layer = Image.new("RGBA", (420, 180), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f1, f2 = font(68), font(68)
    block_h = f1.size + 14 + f2.size
    y = (180 - block_h) // 2
    for txt, ff in (("13 YEARS", f1), ("4,811 DAYS", f2)):
        w = ld.textlength(txt, font=ff)
        ld.text(((420 - w) / 2, y), txt, font=ff, fill=WHITE,
                stroke_width=5, stroke_fill=BLACK)
        y += ff.size + 14
    layer = layer.resize((378, 180), Image.LANCZOS)  # 0.9x horizontal squeeze
    rot = layer.rotate(15, expand=True, resample=Image.BICUBIC)
    im.paste(rot, (475 - rot.width // 2, 305 - rot.height // 2), rot)
    print("board fonts:", f1.size, f2.size, "rotated layer:", rot.size)

    # ---- 3. Dog's cardboard: "DELAYED" / "AGAIN..." (English only).
    # True cardboard quad measured from v5-base.png (tan ~(170,108,69)
    # profile): x 1468-1740, y 876-1044, centre (1604, 960). Old paste
    # centre x=1590 put the 271px-wide 68px text 14px too far left — the
    # "D" overflowed the left edge by ~14px. KOREKSI user: font TETAP 68,
    # hanya geser +14px ke kanan ke centre sebenarnya (1604) supaya margin
    # kiri-kanan seimbang. Dark text with a subtle light outline.
    clay = Image.new("RGBA", (400, 150), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clay)
    f3 = font(68)
    y = (150 - (f3.size + 6 + f3.size)) // 2
    for txt in ("DELAYED", "AGAIN..."):
        w = cd.textlength(txt, font=f3)
        cd.text(((400 - w) / 2, y), txt, font=f3, fill=DARK_BROWN,
                stroke_width=2, stroke_fill=CARD_OUTLINE)
        y += f3.size + 6
    clay = clay.resize((340, 150), Image.LANCZOS)  # 0.85x horizontal squeeze
    im.paste(clay, (1604 - clay.width // 2, 957 - clay.height // 2), clay)
    print("cardboard font:", f3.size, "squeezed width:", clay.width,
          "paste centre x: 1604")

    # ---- 4. Desk calendar: "SICK DAY" / "26 MAY" with red circle.
    # Measured page centre x ~335 (old code used 280 — too far left).
    # Printed look: plain ink, no outline, just bigger than before.
    cal_cx = 335
    f4 = font(52)
    w = d.textlength("SICK DAY", font=f4)
    d.text((cal_cx - w / 2, 920), "SICK DAY", font=f4, fill=INK)
    f5 = font(72)
    w = d.textlength("26 MAY", font=f5)
    top5 = 990
    d.text((cal_cx - w / 2, top5), "26 MAY", font=f5, fill=INK)
    d.ellipse([cal_cx - w / 2 - 18, top5 - 8, cal_cx + w / 2 + 18,
               top5 + f5.size + 14], outline=RED, width=7)
    print("calendar fonts:", f4.size, f5.size)

    # ---- 5. Bottom punchline, centred on the car hood, with drop shadows.
    # Bigger: "...AND STILL" 100, "DELAYED" 136, emoji 110. Centred at x=930
    # so the big DELAYED clears the calendar (right edge ~520).
    px = 930
    f6 = font(100)
    w = d.textlength("...AND STILL", font=f6)
    shadowed(d, (px - w / 2, 1018), "...AND STILL", f6, WHITE, stroke=7)
    f7 = font(136)
    w = d.textlength("DELAYED", font=f7)
    ey = 1128
    ex = px - (w + 20 + 110) / 2
    shadowed(d, (ex, ey), "DELAYED", f7, YELLOW, stroke=7)
    ef = ImageFont.truetype(EMOJI, 109)  # NotoColorEmoji only loads at 109
    d.text((ex + w + 20, ey + 8), "\U0001F602", font=ef, embedded_color=True)
    print("punchline fonts:", f6.size, f7.size, "DELAYED spans",
          round(ex), "to", round(ex + w))

    # ---- 6. GTA minimap, bottom-right corner (unchanged)
    mx, my, r = 1835, 1175, 56
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(10, 22, 38),
              outline=WHITE, width=3)
    for (x1, y1, x2, y2) in [
        (mx - 44, my - 18, mx + 44, my - 26),
        (mx - 40, my + 14, mx + 46, my + 6),
        (mx - 12, my - 48, mx - 20, my + 48),
        (mx + 22, my - 44, mx + 16, my + 46),
    ]:
        d.line([(x1, y1), (x2, y2)], fill=(90, 130, 170), width=3)
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(255, 60, 170))
    d.ellipse([mx + 24 - 5, my - 30 - 5, mx + 24 + 5, my - 30 + 5],
              fill=(255, 210, 0))
    nf = font(16)
    d.text((mx - 6, my - r + 4), "N", font=nf, fill=WHITE)

    # ---- 7. GTA money pickup: "+$1,340.00" cleanly above the coin.
    # The two floating "$" are REMOVED (they looked like mistakes).
    # Coin centre ~(1250, 590); text centred at (1330, 448) clears the
    # ghost's jaw (right edge ~1121) and the dog's beanie (top ~525).
    f8 = font(72)
    w = d.textlength("+$1,340.00", font=f8)
    outlined(d, (1330 - w / 2, 448), "+$1,340.00", f8, GREEN, stroke=5)
    print("money pickup font:", f8.size, "spans",
          round(1330 - w / 2), "to", round(1330 + w / 2))

    # ---- 8. License plate "MAKEFUN", restyled as a real plate: trapezoid
    # with perspective, dark border + inner border, corner bolts, bold navy
    # letters. Bigger than the first attempt (the text overflowed the plate);
    # placed low on the bumper so it never touches the punchline.
    plate = [(1412, 1218), (1688, 1218), (1700, 1270), (1400, 1270)]
    d.polygon(plate, fill=(245, 245, 240), outline=(25, 25, 40), width=4)
    inner = [(1422, 1226), (1680, 1226), (1690, 1262), (1410, 1262)]
    d.line(inner + [inner[0]], fill=(25, 25, 40), width=2)
    for bx, by in ((1435, 1244), (1665, 1244)):
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(60, 60, 70))
    f10 = font(36)
    w = d.textlength("MAKEFUN", font=f10)
    d.text(((1412 + 1688 - w) / 2, 1228), "MAKEFUN", font=f10, fill=NAVY)
    print("plate font:", f10.size, "text width:", round(w))

    im.save(OUT)
    im.resize((768, 512), Image.LANCZOS).save(PREVIEW)
    print("saved", OUT, im.size)
    print("saved", PREVIEW)


if __name__ == "__main__":
    main()
