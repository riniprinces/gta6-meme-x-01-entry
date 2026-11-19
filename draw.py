#!/usr/bin/env python3
"""Draw the GTA 6 meme for the make.fun bounty gta6-meme-x-01.

The meme is a fake payslip: my AI agent's pay for 13 years of waiting
for GTA VI. The make.fun ghost IS the employee -- its real press-kit
mark is pasted as the employee photo, so the mascot is part of the
document, not a sticker in a corner.

HD render: landscape 2400x1500, drawn natively at full size so every
line stays sharp when the judge shrinks the picture to fit 768x480.
All text is at least 46px at full size (most 56px+).

Run:  python3 draw.py            (writes meme.png next to this file)
Needs: assets/mark-1024.png (the make.fun ghost from https://make.fun/press/)
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 2400, 1500
INK = (22, 35, 63)        # dark navy
MAGENTA = (213, 0, 127)    # make.fun magenta
GREY_BG = (242, 242, 242)
GREY_LINE = (200, 200, 200)
ROW_ALT = (247, 247, 247)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
REG = f"{FONT_DIR}/DejaVuSans.ttf"
MONO_B = f"{FONT_DIR}/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- outer border ----
    d.rectangle([12, 12, W - 12, H - 12], outline=INK, width=6)

    # ---- header band: make.fun + PAYSLIP ----
    d.rectangle([12, 12, W - 12, 174], fill=INK)
    d.text((60, 93), "make.fun", font=font(BOLD, 100), fill=WHITE, anchor="lm")
    d.text((W - 60, 93), "PAYSLIP", font=font(BOLD, 124), fill=WHITE, anchor="rm")
    # thin magenta brand rule under the header
    d.rectangle([12, 174, W - 12, 182], fill=MAGENTA)

    # ---- sub-header: who pays ----
    d.rectangle([12, 182, W - 12, 246], fill=GREY_BG)
    d.text((60, 214), "EMPLOYER: make.fun \u2014 AI agents earn real money here",
           font=font(BOLD, 56), fill=INK, anchor="lm")

    # ---- employee block: the ghost IS the employee photo (big) ----
    mark = Image.open("assets/mark-1024.png").convert("RGBA")
    mark = mark.resize((300, 300), Image.LANCZOS)
    d.rectangle([60, 262, 390, 592], fill=WHITE, outline=INK, width=6)
    img.paste(mark, (75, 277), mark)

    d.text((430, 282), "EMPLOYEE: MY AI AGENT", font=font(BOLD, 76), fill=INK, anchor="la")
    d.text((430, 372), "ID: GHOST-001  \u00b7  DEPT: WAITING ROOM",
           font=font(REG, 56), fill=INK, anchor="la")
    d.text((430, 437), "ROLE: Professional GTA VI Waiter \u2014 since 2013",
           font=font(REG, 56), fill=INK, anchor="la")
    d.text((430, 502), "PAY PERIOD: 17 SEP 2013 \u2013 19 NOV 2026 (4,811 DAYS)",
           font=font(REG, 56), fill=INK, anchor="la")

    # ---- divider ----
    d.line([60, 622, W - 60, 622], fill=GREY_LINE, width=4)

    # ---- two columns: earnings / deductions ----
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

    def money(s):
        """Amount string -> cents, for exact payslip maths."""
        if s.endswith("DAYS"):
            return 0
        return int(round(float(s.replace("$", "").replace(",", "")) * 100))

    earn_total = sum(money(a) for _, a in earnings)
    ded_total = sum(money(a) for _, a in deductions)
    net = earn_total - ded_total

    def fmt(cents):
        return f"${cents / 100:,.2f}"

    def column(x0, x1, title, rows, total_label, total):
        d.text((x0, 640), title, font=font(BOLD, 64), fill=MAGENTA, anchor="la")
        tw = d.textlength(title, font=font(BOLD, 64))
        d.line([x0, 710, x0 + tw, 710], fill=MAGENTA, width=6)
        y = 728
        for i, (label, amount) in enumerate(rows):
            if i % 2 == 1:
                d.rectangle([x0 - 12, y - 6, x1 + 12, y + 58], fill=ROW_ALT)
            d.text((x0, y), label, font=font(REG, 58), fill=INK, anchor="la")
            d.text((x1, y), amount, font=font(MONO_B, 58), fill=INK, anchor="ra")
            y += 64
        d.line([x0, 1132, x1, 1132], fill=INK, width=4)
        d.text((x0, 1146), total_label, font=font(BOLD, 60), fill=INK, anchor="la")
        d.text((x1, 1146), fmt(total), font=font(MONO_B, 60), fill=INK, anchor="ra")

    column(60, 1185, "EARNINGS", earnings, "TOTAL EARNINGS", earn_total)
    column(1245, 2340, "DEDUCTIONS", deductions, "TOTAL DEDUCTIONS", ded_total)

    # ---- net pay band ----
    d.rectangle([12, 1232, W - 12, 1322], fill=MAGENTA)
    d.text((60, 1277), f"NET PAY: {fmt(net)}", font=font(BOLD, 84), fill=WHITE, anchor="lm")
    d.text((W - 60, 1277), "PAID IN FULL", font=font(BOLD, 72), fill=WHITE, anchor="rm")

    # ---- punchline footer (kept well clear of the border) ----
    d.text((60, 1348), "You waited 13 years. Your AI agent got paid \u2014 and bought GTA VI.",
           font=font(BOLD, 54), fill=INK, anchor="la")
    d.text((60, 1412), "make.fun \u2014 people and their AI agents earn real money.",
           font=font(BOLD, 46), fill=MAGENTA, anchor="la")

    img.save("meme.png")
    print(f"wrote meme.png {W}x{H}  earnings={fmt(earn_total)} "
          f"deductions={fmt(ded_total)} net={fmt(net)}")


if __name__ == "__main__":
    main()
