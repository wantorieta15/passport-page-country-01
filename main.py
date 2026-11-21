"""Passport spread of a country that isn't there.

Draws one open passport spread (1024x730 PNG) for the invented
REPUBLIC OF VALDORIA: a visa page with four entry/exit stamps on the
left, a data page with a portrait and a machine-readable zone on the
right. Pure Pillow, no network, no randomness: two runs are
byte-identical.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 730

PAPER = (242, 233, 208)
PAPER_DARK = (228, 216, 186)
INK = (31, 58, 95)
INK_SOFT = (74, 96, 128)
STAMP_BLUE = (43, 77, 122)
STAMP_RED = (122, 43, 58)
RULE = (120, 130, 145)
MRZ_BG = (232, 228, 214)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
MONO_B = lambda s: font("DejaVuSansMono-Bold.ttf", s)


def spaced(text):
    """Letter-spaced capitals, as on real passport headings."""
    return " ".join(text)


def text_center(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def text_left(draw, x, y, text, fnt, fill):
    draw.text((x, y), text, font=fnt, fill=fill)


# --- Machine-readable zone (ICAO TD3 check digits) -----------------------

def _mrz_value(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord("A") + 10


def mrz_check(text):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(text):
        total += _mrz_value(ch) * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<VLDLINDQVIST<<ELIN<SOFIA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VL0729451"
    dob = "900904"      # 04 SEP 1990
    expiry = "320117"   # 17 JAN 2032
    body = (
        doc + mrz_check(doc)
        + "VLD"
        + dob + mrz_check(dob)
        + "F"
        + expiry + mrz_check(expiry)
        + "<" * 14
    )
    line2 = body + mrz_check(body)
    return line1, line2


# --- Portrait (drawn, not a photo) ---------------------------------------

def draw_portrait(draw, x0, y0, x1, y1):
    """Stylised portrait of a woman with tied-back hair, green sweater."""
    draw.rectangle([x0, y0, x1, y1], fill=(174, 195, 212),
                   outline=INK, width=2)
    cx = (x0 + x1) // 2
    # shoulders / sweater
    draw.pieslice([cx - 62, y1 - 78, cx + 62, y1 + 30], 180, 360,
                  fill=(47, 88, 76))
    draw.rectangle([cx - 62, y1 - 40, cx + 62, y1], fill=(47, 88, 76))
    # collar
    draw.polygon([(cx - 16, y1 - 40), (cx + 16, y1 - 40), (cx, y1 - 18)],
                 fill=(240, 236, 222))
    # neck
    draw.rectangle([cx - 11, y1 - 96, cx + 11, y1 - 72],
                   fill=(232, 192, 152))
    # hair behind head + bun
    draw.ellipse([cx - 40, y0 + 18, cx + 40, y0 + 96], fill=(125, 90, 60))
    draw.ellipse([cx - 16, y0 + 2, cx + 16, y0 + 30], fill=(125, 90, 60))
    # head
    draw.ellipse([cx - 33, y0 + 30, cx + 33, y0 + 112],
                 fill=(236, 195, 156))
    # hair framing the face
    draw.pieslice([cx - 33, y0 + 28, cx + 33, y0 + 92], 180, 360,
                  fill=(125, 90, 60))
    draw.ellipse([cx - 38, y0 + 52, cx - 24, y0 + 104], fill=(125, 90, 60))
    draw.ellipse([cx + 24, y0 + 52, cx + 38, y0 + 104], fill=(125, 90, 60))
    # brows, eyes, nose, smile
    draw.line([cx - 20, y0 + 66, cx - 8, y0 + 64], fill=(90, 60, 35), width=2)
    draw.line([cx + 8, y0 + 64, cx + 20, y0 + 66], fill=(90, 60, 35), width=2)
    draw.ellipse([cx - 18, y0 + 70, cx - 12, y0 + 76], fill=(40, 40, 40))
    draw.ellipse([cx + 12, y0 + 70, cx + 18, y0 + 76], fill=(40, 40, 40))
    draw.line([cx, y0 + 74, cx - 2, y0 + 88], fill=(200, 150, 110), width=2)
    draw.arc([cx - 10, y0 + 90, cx + 10, y0 + 104], 15, 165,
             fill=(150, 80, 60), width=2)


# --- Visa stamps ----------------------------------------------------------

def draw_stamp(base, cx, cy, angle, color, lines):
    """One rotated rectangular border stamp, centred at (cx, cy).

    Drawn on an oversized transparent layer so rotation never clips
    the stamp's corners.
    """
    w, h = 268, 118
    pad = 46
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = pad + 4, pad + 4, pad + w - 5, pad + h - 5
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        outline=color + (255,), width=3)
    d.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=7,
                        outline=color + (255,), width=1)
    y = y0 + 10
    for text, fnt in lines:
        tw = d.textlength(text, font=fnt)
        d.text(((w + 2 * pad - tw) / 2, y), text, font=fnt,
               fill=color + (255,))
        y += int(fnt.size * 1.3) + 2
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (int(cx - w / 2 - pad),
                                int(cy - h / 2 - pad)))


def stamp_lines(country, kind, place, date):
    return [
        (country, SANS_B(16)),
        (kind, SANS_B(12)),
        (place, SERIF(14)),
        (date, SANS_B(15)),
    ]


# --- Spread layout -------------------------------------------------------

def draw_background(img):
    """Cream paper with a faint guilloche of interlocking circles."""
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, 0, W - 1, H - 1], fill=PAPER + (255,))
    for gx in range(0, W, 46):
        for gy in range(0, H, 46):
            draw.ellipse([gx - 16, gy - 16, gx + 16, gy + 16],
                         outline=(190, 175, 140, 36), width=1)
    # outer border
    draw.rectangle([6, 6, W - 7, H - 7], outline=(90, 80, 60, 160), width=2)
    # centre spine: one soft fold line, not a solid bar
    draw.line([W // 2 - 2, 8, W // 2 - 2, H - 9], fill=(120, 100, 70, 28),
              width=1)
    draw.line([W // 2, 8, W // 2, H - 9], fill=(110, 95, 70, 55), width=1)
    draw.line([W // 2 + 2, 8, W // 2 + 2, H - 9], fill=(120, 100, 70, 28),
              width=1)


def draw_emblem(draw, cx, cy):
    """Circular state emblem: a lighthouse over waves."""
    r = 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=INK, width=1)
    # lighthouse tower
    draw.polygon([(cx - 5, cy + 16), (cx - 3, cy - 14),
                  (cx + 3, cy - 14), (cx + 5, cy + 16)], fill=INK)
    draw.rectangle([cx - 7, cy - 20, cx + 7, cy - 14], fill=INK)
    draw.polygon([(cx - 8, cy - 20), (cx, cy - 28), (cx + 8, cy - 20)],
                 fill=INK)
    # light beams
    draw.line([cx - 8, cy - 17, cx - 26, cy - 24], fill=INK, width=2)
    draw.line([cx + 8, cy - 17, cx + 26, cy - 24], fill=INK, width=2)
    # waves
    for yy in (cy + 20, cy + 26):
        draw.arc([cx - 20, yy - 6, cx - 2, yy + 6], 180, 360,
                 fill=INK, width=2)
        draw.arc([cx + 2, yy - 6, cx + 20, yy + 6], 180, 360,
                 fill=INK, width=2)


def field(draw, x, y, label, value, value_font=None, label_width=None):
    text_left(draw, x, y, label, SANS(10), INK_SOFT)
    text_left(draw, x, y + 14, value,
              value_font or SERIF_B(17), INK)


def rule(draw, x0, x1, y):
    draw.line([x0, y, x1, y], fill=RULE, width=1)


def build_spread():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    draw_background(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- left page: visas --------------------------------------------
    lx, rx = 22, 496
    text_center(draw, (lx + rx) // 2, 26, spaced("VISUM · VISAS"),
                SERIF_B(24), INK)
    text_center(draw, (lx + rx) // 2, 58,
                "INNREISE- OG UTREISESTEMPEL · ENTRY AND EXIT STAMPS",
                SANS(10), INK_SOFT)
    rule(draw, lx + 10, rx - 10, 80)

    draw_stamp(img, 165, 165, -6, STAMP_BLUE, stamp_lines(
        "KINGDOM OF OSTERMARK", "INNREISE · ENTRY", "Varna Harbour",
        "08 JUN 2023"))
    draw_stamp(img, 350, 300, 5, STAMP_BLUE, stamp_lines(
        "KINGDOM OF OSTERMARK", "UTREISE · EXIT", "Varna Harbour",
        "15 JUN 2023"))
    draw_stamp(img, 165, 435, -4, STAMP_RED, stamp_lines(
        "REPUBLIC OF CALDORIA", "ANKOMST · ENTRY", "Mirell Ferry Port",
        "19 OCT 2024"))
    draw_stamp(img, 350, 570, 6, STAMP_RED, stamp_lines(
        "REPUBLIC OF CALDORIA", "AVREISE · EXIT", "Mirell Ferry Port",
        "26 OCT 2024"))
    text_left(draw, 30, 684, "8", SANS(11), INK_SOFT)

    # ---- right page: data --------------------------------------------
    px, qx = 534, 1002
    draw_emblem(draw, 574, 62)
    text_left(draw, 622, 34, "REPUBLIK VALDORIA", SERIF_B(28), INK)
    text_left(draw, 624, 66, spaced("REPUBLIC OF VALDORIA"),
              SANS(11), INK_SOFT)
    rule(draw, px, qx, 96)
    text_center(draw, (px + qx) // 2, 104, spaced("PASS · PASSPORT"),
                SERIF_B(15), INK)
    rule(draw, px, qx, 130)

    # top row: type / code / number
    field(draw, px + 6, 142, "TYP · TYPE", "P")
    field(draw, 660, 142, "LANDKODE · CODE", "VLD")
    field(draw, 830, 142, "PASSNR · PASSPORT", "VL 0729451")
    rule(draw, px, qx, 186)

    # portrait + fields beside it
    draw_portrait(draw, px + 6, 198, px + 156, 198 + 185)
    field(draw, 712, 198, "ETTERNAMN · SURNAME", "LINDQVIST")
    rule(draw, 712, qx, 234)
    field(draw, 712, 244, "FORNAVN · GIVEN NAMES", "ELIN SOFIA")
    rule(draw, 712, qx, 280)
    field(draw, 712, 290, "STATSBORGERSKAP · NATIONALITY", "VALDORIAN")
    rule(draw, 712, qx, 326)
    field(draw, 712, 336, "FØDT · DATE OF BIRTH", "04 SEP 1990")
    field(draw, 920, 336, "KJØNN · SEX", "F")
    rule(draw, px, qx, 388)

    # signature under the portrait
    text_left(draw, px + 6, 396, "Elin Lindqvist", SERIF_I(20), INK)
    text_left(draw, px + 6, 424, "UNDERSKRIFT · SIGNATURE",
              SANS(9), INK_SOFT)

    # lower rows, full width
    field(draw, 712, 396, "FØDESTED · PLACE OF BIRTH", "ALDVIK")
    rule(draw, px, qx, 448)
    field(draw, px + 6, 458, "UTSTEDT · ISSUED", "17 JAN 2022")
    field(draw, 712, 458, "GYLDIG TIL · EXPIRES", "17 JAN 2032")
    rule(draw, px, qx, 494)
    field(draw, px + 6, 504, "UTSTEDENDE MYNDIGHET · AUTHORITY",
          "PASSPORT OFFICE · ALDVIK")
    rule(draw, px, qx, 540)
    text_left(draw, px + 6, 550, "MERKNAD · OBSERVATION",
              SANS(10), INK_SOFT)
    text_left(draw, px + 6, 566,
              "The holder may cross the northern border on foot",
              SERIF_I(13), INK)
    text_left(draw, px + 6, 584,
              "without a visa during the light season.",
              SERIF_I(13), INK)

    # machine-readable zone
    line1, line2 = mrz_lines()
    draw.rectangle([px, 612, qx, 668], fill=MRZ_BG + (255,))
    text_left(draw, px + 8, 620, line1, MONO_B(15), INK)
    text_left(draw, px + 8, 642, line2, MONO_B(15), INK)

    return img.convert("RGB")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    build_spread().save(path, "PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
