#!/usr/bin/env python3
"""Draw the Tuesday 24 November 2026 broadsheet (news-image-20261124 v4).

Pattern (from the submitted news23 v3 front page): giant date masthead
as the single biggest thing -> DATE CHECK strip -> the 4 most
consequential stories as LARGE illustrated features in a 2x2 grid
(literal-scene art panel + headline + one-line fact + CONFIRMED /
REPORTED status tag) -> the remaining 42 stories as a compact dated
3-column index with region counts -> navy sources footer.

Usage: python3 draw.py entry.png
Deterministic: no randomness, no timestamps; two runs are byte-identical.
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14

# --- palette ---------------------------------------------------------------
NAVY = (13, 38, 66)        # masthead / footer / date-check
NAVY2 = (16, 48, 82)       # masthead gradient step
GOLD = (232, 185, 60)      # masthead kicker, date-check label, footer rule
GOLD_DK = (201, 152, 32)
PAPER = (255, 255, 255)
INK = (17, 24, 39)
MUTED = (71, 85, 105)
LINE = (203, 213, 225)
CREAM = (244, 241, 232)    # index background
TEAL = (15, 118, 110)      # CONFIRMED pill
AMBER = (180, 83, 9)       # REPORTED pill
RED = (185, 28, 28)
GREEN = (22, 163, 74)
SEA = (14, 116, 144)       # Hormuz sea
SKY = (186, 230, 253)      # Hormuz sky
SAND = (214, 182, 120)     # ICJ stone
STONE = (120, 100, 66)

# --- fonts -----------------------------------------------------------------
def font(path, size):
    return ImageFont.truetype(path, size)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def f_serif(size):
    return font(SERIF_B, size)

def f_sans(size):
    return font(SANS, size)

def f_sans_b(size):
    return font(SANS_B, size)

# --- data ------------------------------------------------------------------
# The 4 large features: (headline, fact, tag, tag_colour, art_key)
FEATURES = [
    ("NVIDIA SOARS 30% \u2014 BEST DAY IN OVER A YEAR",
     "Huang returns as CEO; stock gains ~$1 trillion.",
     "CONFIRMED", TEAL, "nvidia"),
    ("COP31 COLLAPSES \u2014 NO DEAL",
     "Antalya: 90+ nations reject draft; no fossil-fuel word.",
     "CONFIRMED", TEAL, "cop31"),
    ("TANKERS HIT MINES IN THE STRAIT OF HORMUZ",
     "Ships burn; Iran vows \u2018all available means\u2019.",
     "REPORTED", AMBER, "hormuz"),
    ("ICJ: MYANMAR COMMITTED GENOCIDE",
     "Landmark ruling in the genocide case.",
     "CONFIRMED", TEAL, "icj"),
]

# The compact index: (short title, date) — date "tue" = 24 Nov (gold dot),
# "sat" = 21 Nov (grey dot; Banten fire itself was Sat 21 Nov, shown only
# for its 24 Nov toll update).
INDEX = [
    ("5.3 quake shakes Nepal at dawn; no deaths", "tue"),
    ("Israeli strikes kill Hamas security chief", "tue"),
    ("NATO vows to defend space from Russia", "tue"),
    ("Zaporizhzhia strike kills 2, wounds 40", "tue"),
    ("Banten factory fire toll rises to 26", "sat"),
    ("US loses measles-free status after 25 years", "tue"),
    ("Sanofi buys Insmed for $41 billion", "tue"),
    ("Ukraine: drones sank corvette off Libya", "tue"),
    ("Fighting in Ituri traps Ebola responders", "tue"),
    ("CAS restores Senegal as AFCON champions", "tue"),
    ("South Africa bowl Bangladesh out for 91", "tue"),
    ("States sue SpaceX over Grok abuse images", "tue"),
    ("US blacklists Megaspeed over AI chips", "tue"),
    ("Arm extends CEO Rene Haas's tenure to 2033", "tue"),
    ("UN chief urges AI safety rules within a year", "tue"),
    ("Trump orders DOJ to speed up death sentences", "tue"),
    ("Pentagon: Canada lags as defence partner", "tue"),
    ("Seven states back EU limits on Russian visas", "tue"),
    ("Iraq PM orders takeover of Kurdish oilfields", "tue"),
    ("UN urges probe into Benghazi port attacks", "tue"),
    ("Seoul offers rewards to catch AI exam cheats", "tue"),
    ("Mexico to try 'El Chapo Isidro' despite US bid", "tue"),
    ("Iran flogs singer Parastoo Ahmadi, 74 lashes", "tue"),
    ("Somalia, Uganda step up fight vs al-Shabaab", "tue"),
    ("UN: 47,000 women killed by partners in 2025", "tue"),
    ("FDA approves first limb-girdle dystrophy drug", "tue"),
    ("Most distant quasar found after Big Bang", "tue"),
    ("Russian jets enter S. Korea air-defence zone", "tue"),
    ("Norway in dialogue with Ukraine on stability", "tue"),
    ("Vance, Rubio meet Qatari PM at White House", "tue"),
    ("Brentford 4-0 Everton; Monza 3-0 Fiorentina", "tue"),
    ("Brazil lose 3-2 to Japan; Ancelotti under fire", "tue"),
    ("India seal ODI series 3-1 against New Zealand", "tue"),
    ("Spain election campaign heats up for 29 Nov", "tue"),
    ("Zverev wins ATP Finals opener in Turin", "tue"),
    ("Canary Islands log record migrant arrivals", "tue"),
    ("Pope Leo XIV visits Peru on poverty, slavery", "tue"),
    ("Philippines win first Eurovision Asia contest", "tue"),
    ("ASEAN summit opens in Manila", "tue"),
    ("Gremio beat Santos 2-0 in the Brasileirao", "tue"),
    ("Persija Jakarta thrash Sumsel United 7-0", "tue"),
    ("Pyramids stun Al Ahly 2-0 in Egyptian league", "tue"),
]

# Region counts across all 46 stories (features + index).
REGION_COUNTS = ("Americas 11", "Europe 10", "Asia-Pacific 10",
                 "Africa 7", "Middle East 4", "World 4")

TRUNCATIONS = [0]  # any text that had to be cut counts here; must end at 0


# --- helpers ---------------------------------------------------------------
def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)

def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines (never empty)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines if lines else [""]

def draw_fitted(draw, text, fnt, max_w, max_lines, xy, fill, shrink_steps=(0, -1, -2, -3, -4)):
    """Draw text wrapped to max_lines; shrink font if needed. Counts a
    truncation if the text still does not fit and is ellipsised."""
    x, y = xy
    size = fnt.size
    path = SANS_B if fnt.path.endswith("DejaVuSans-Bold.ttf") else (
        SERIF_B if "Serif" in fnt.path else SANS)
    for step in shrink_steps:
        f = font(path, max(8, size + step))
        lines = wrap_text(draw, text, f, max_w)
        if len(lines) <= max_lines:
            lh = int(f.size * 1.18)
            for ln in lines:
                draw.text((x, y), ln, font=f, fill=fill)
                y += lh
            return y
    # last resort: ellipsise the final allowed line
    f = font(path, max(8, size + shrink_steps[-1]))
    lines = wrap_text(draw, text, f, max_w)
    lh = int(f.size * 1.18)
    shown = lines[:max_lines]
    if len(lines) > max_lines and shown:
        last = shown[-1]
        while text_w(draw, last + "\u2026", f) > max_w and len(last) > 1:
            last = last[:-1]
        shown[-1] = last + "\u2026"
        TRUNCATIONS[0] += 1
    for ln in shown:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y

def draw_single(draw, text, fnt, max_w, xy, fill):
    """One line; shrink then ellipsise (counted) if it still overflows."""
    x, y = xy
    path = SANS_B if fnt.path.endswith("DejaVuSans-Bold.ttf") else (
        SERIF_B if "Serif" in fnt.path else SANS)
    size = fnt.size
    for step in (0, -1, -2, -3):
        f = font(path, max(8, size + step))
        if text_w(draw, text, f) <= max_w:
            draw.text((x, y), text, font=f, fill=fill)
            return
    f = font(path, max(8, size - 3))
    t = text
    while text_w(draw, t + "\u2026", f) > max_w and len(t) > 1:
        t = t[:-1]
    draw.text((x, y), t + "\u2026", font=f, fill=fill)
    TRUNCATIONS[0] += 1

def pill(draw, x, y, text, bg, fg=(255, 255, 255)):
    """Status tag pill; returns its width."""
    f = f_sans_b(14)
    w = int(text_w(draw, text, f)) + 22
    h = 24
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=bg)
    draw.text((x + 11, y + 4), text, font=f, fill=fg)
    return w

def dot(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# --- art panels (literal scenes, drawn fresh) --------------------------------
def art_nvidia(img, d, x, y, w, h):
    """Chip skyline + green surge line, +30%."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 32, 58))
    # chip skyline along the bottom
    import random as _r
    rng = _r.Random(24)
    bx = x + 6
    while bx < x + w - 14:
        bw = rng.randint(14, 26)
        bh = rng.randint(18, 64)
        col = (24, 68, 110) if rng.random() < 0.6 else (16, 48, 82)
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=col)
        d.rectangle([bx + 3, y + h - bh + 4, bx + bw - 3, y + h - bh + 8], fill=(52, 130, 190))
        if rng.random() < 0.5:
            dot(d, bx + bw // 2, y + h - bh - 6, 2, GOLD)
        bx += bw + 4
    # green surge line with arrowhead
    pts = [(x + 16, y + h - 26), (x + 130, y + h - 46), (x + 250, y + h - 38),
           (x + 370, y + h - 82), (x + w - 22, y + 44)]
    d.line(pts, fill=GREEN, width=5, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey - 9), (ex, ey + 9), (ex + 16, ey)], fill=GREEN)
    d.text((x + 16, y + 8), "+30%", font=f_sans_b(46), fill=GREEN)
    t = "NASDAQ +6.51%"
    tw = int(text_w(d, t, f_sans_b(16)))
    d.text((x + w - tw - 14, y + 8), t, font=f_sans_b(16), fill=(255, 255, 255))

def art_cop31(img, d, x, y, w, h):
    """Globe + red NO DEAL stamp + flag blocks."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy, r = x + 88, y + 58, 46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(147, 197, 253))
    for k in (-24, 0, 24):
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              start=90, end=270, fill=(255, 255, 255), width=2)
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              start=270, end=90, fill=(30, 90, 140), width=2)
    d.ellipse([cx - r, cy - 8, cx + r, cy + 8], outline=(255, 255, 255), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    # NO DEAL stamp, rotated
    stamp = Image.new("RGBA", (260, 84), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 255, 79], radius=8, outline=(239, 68, 68), width=5)
    sd.text((130, 16), "NO DEAL", font=f_sans_b(40), fill=(239, 68, 68), anchor="ma")
    stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (x + w - 290, y + 26), stamp)
    # flag-colour blocks along the bottom
    cols = [(185, 28, 28), (232, 185, 60), (255, 255, 255), (15, 118, 110),
            (30, 58, 95), (185, 28, 28), (232, 185, 60)]
    bw = w // len(cols)
    for i, c in enumerate(cols):
        d.rectangle([x + i * bw, y + h - 12, x + (i + 1) * bw, y + h], fill=c)
    d.text((x + 14, y + h - 34), "ANTALYA \u00b7 COP31", font=f_sans_b(14), fill=GOLD)

def art_hormuz(img, d, x, y, w, h):
    """Sea, tanker on fire, missile arcs, sun."""
    d.rectangle([x, y, x + w, y + 52], fill=SKY)
    d.rectangle([x, y + 52, x + w, y + h], fill=SEA)
    d.ellipse([x + w - 62, y + 8, x + w - 30, y + 40], fill=(250, 204, 21))
    # missile arcs (kept inside this panel)
    d.arc([x + w - 320, y + 10, x + w - 120, y + 120], start=195, end=335, fill=RED, width=4)
    d.arc([x + w - 260, y + 20, x + w - 140, y + 112], start=195, end=335, fill=(239, 68, 68), width=3)
    # tanker hull + superstructure
    d.rectangle([x + 52, y + 78, x + 330, y + 104], fill=(10, 10, 12))
    d.rectangle([x + 268, y + 58, x + 306, y + 78], fill=(30, 30, 34))
    d.rectangle([x + 312, y + 64, x + 322, y + 78], fill=(185, 28, 28))
    # flame on deck
    fx, fy = x + 150, y + 78
    d.polygon([(fx - 16, fy), (fx, fy - 34), (fx + 8, fy - 12), (fx + 18, fy - 26),
               (fx + 26, fy)], fill=(249, 115, 22))
    d.polygon([(fx - 7, fy), (fx + 2, fy - 18), (fx + 12, fy)], fill=(250, 204, 21))
    # sea lines
    for yy in (112, 122):
        d.line([(x + 20, y + yy), (x + w - 20, y + yy)], fill=(56, 160, 190), width=2)
    t = "STRAIT OF HORMUZ"
    tw = int(text_w(d, t, f_sans_b(14)))
    d.text((x + w - tw - 12, y + h - 18), t, font=f_sans_b(14), fill=(255, 255, 255))

def art_icj(img, d, x, y, w, h):
    """Courthouse with columns + scales of justice."""
    d.rectangle([x, y, x + w, y + h], fill=SAND)
    d.rectangle([x, y, x + w, y + 10], fill=(188, 152, 92))
    # pediment + columns (left)
    px0, px1 = x + 36, x + 268
    d.polygon([(px0, y + 52), ((px0 + px1) // 2, y + 14), (px1, y + 52)], fill=(240, 230, 210))
    d.rectangle([px0, y + 52, px1, y + 64], fill=(240, 230, 210))
    for i in range(4):
        cx0 = px0 + 14 + i * 56
        d.rectangle([cx0, y + 64, cx0 + 20, y + 108], fill=(250, 244, 230))
        d.rectangle([cx0 - 3, y + 60, cx0 + 23, y + 66], fill=(250, 244, 230))
    d.rectangle([px0 - 6, y + 108, px1 + 6, y + 114], fill=(240, 230, 210))
    d.rectangle([px0 - 12, y + 114, px1 + 12, y + 120], fill=(228, 214, 188))
    # scales of justice (right), kept clear of the label below
    sx = x + 380
    d.line([(sx, y + 18), (sx, y + 86)], fill=(60, 48, 30), width=5)
    d.line([(sx - 42, y + 30), (sx + 42, y + 30)], fill=(60, 48, 30), width=4)
    for sgn in (-1, 1):
        ex = sx + sgn * 42
        d.line([(ex, y + 30), (ex, y + 56)], fill=(60, 48, 30), width=3)
        d.arc([ex - 18, y + 48, ex + 18, y + 74], start=0, end=180, fill=(60, 48, 30), width=4)
    d.ellipse([sx - 6, y + 10, sx + 6, y + 20], fill=(60, 48, 30))
    d.rectangle([sx - 16, y + 86, sx + 16, y + 94], fill=(60, 48, 30))
    t = "ICJ \u00b7 THE HAGUE"
    tw = int(text_w(d, t, f_sans_b(14)))
    d.text((x + w - tw - 12, y + h - 18), t, font=f_sans_b(14), fill=(60, 48, 30))

ART = {"nvidia": art_nvidia, "cop31": art_cop31, "hormuz": art_hormuz, "icj": art_icj}


# --- layout ------------------------------------------------------------------
def centered(draw, cx, y, text, fnt, fill):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)

def fit_size(draw, text, fnt_path, start, max_w):
    size = start
    while size > 20:
        f = font(fnt_path, size)
        if text_w(draw, text, f) <= max_w:
            return f
        size -= 2
    return font(fnt_path, 20)

def draw_masthead(img, d):
    d.rectangle([0, 0, W, 116], fill=NAVY)
    d.rectangle([0, 0, W, 3], fill=GOLD)
    d.text((MARGIN, 12), "THE WORLD IN ONE DAY", font=f_sans_b(20), fill=GOLD)
    t = "THE DAY IN UTC"
    tw = int(text_w(d, t, f_sans_b(20)))
    d.text((W - MARGIN - tw, 12), t, font=f_sans_b(20), fill=GOLD)
    f = fit_size(d, "TUESDAY 24 NOVEMBER 2026", SERIF_B, 64, W - 2 * MARGIN - 8)
    centered(d, W // 2, 40, "TUESDAY 24 NOVEMBER 2026", f, (255, 255, 255))
    d.rectangle([0, 113, W, 116], fill=GOLD)

def draw_datecheck(d):
    d.rounded_rectangle([MARGIN, 124, W - MARGIN, 184], radius=6,
                        fill=NAVY, outline=GOLD, width=2)
    d.text((MARGIN + 16, 134), "DATE CHECK", font=f_sans_b(16), fill=GOLD)
    s = "Every event below happened or was first reported Tuesday 24 Nov 2026, any time zone."
    d.text((MARGIN + 16 + 118, 134), s, font=f_sans(16), fill=(255, 255, 255))
    n = "Banten factory fire was Sat 21 Nov \u2014 shown only for its 24 Nov toll update."
    d.text((MARGIN + 16, 158), n, font=f_sans(14), fill=(232, 213, 160))

def draw_feature(img, d, x, y, w, feat):
    headline, fact, tag, tag_bg, art_key = feat
    art_h, text_h = 118, 116
    d.rectangle([x, y, x + w, y + art_h + text_h], outline=LINE, width=1)
    ART[art_key](img, d, x + 1, y + 1, w - 2, art_h - 1)
    ty = y + art_h
    d.rectangle([x + 1, ty, x + w - 1, y + art_h + text_h], fill=PAPER)
    end_y = draw_fitted(d, headline, f_sans_b(26), w - 24, 2, (x + 12, ty + 6), INK)
    draw_single(d, fact, f_sans(15), w - 24, (x + 12, end_y + 3), MUTED)
    pill(d, x + 12, ty + text_h - 28, tag, tag_bg)

def draw_also(d):
    y0 = 676
    d.rectangle([0, y0 - 8, W, 968], fill=CREAM)
    d.line([(0, y0 - 8), (W, y0 - 8)], fill=LINE, width=1)
    d.text((MARGIN, y0), "ALSO ON TUESDAY \u2014 42 MORE STORIES",
           font=f_sans_b(20), fill=INK)
    # legend, right aligned
    leg = [("TUE 24 Nov", GOLD_DK), ("SAT 21 Nov", (150, 150, 150))]
    lx = W - MARGIN
    for label, col in reversed(leg):
        f = f_sans(13)
        tw = int(text_w(d, label, f))
        lx -= tw
        d.text((lx, y0 + 4), label, font=f, fill=MUTED)
        dot(d, lx - 10, y0 + 11, 4, col)
        lx -= 22
    # 3 columns x 14 rows
    col_w = (W - 2 * MARGIN - 2 * 12) // 3
    row_h = 17
    for i, (title, day) in enumerate(INDEX):
        col, row = divmod(i, 14)
        cx = MARGIN + col * (col_w + 12)
        cy = y0 + 30 + row * row_h
        dot(d, cx + 4, cy + 7, 4, GOLD_DK if day == "tue" else (150, 150, 150))
        draw_single(d, title, f_sans(13), col_w - 18, (cx + 14, cy), INK)
    counts = " \u00b7 ".join(REGION_COUNTS) + "  =  46 stories"
    centered(d, W // 2, y0 + 30 + 14 * row_h + 6, counts, f_sans(15), MUTED)

def draw_footer(d):
    d.rectangle([0, 972, W, H], fill=NAVY)
    centered(d, W // 2, 982,
             "TUESDAY 24 NOVEMBER 2026  \u00b7  46 stories  \u00b7  Verified against live reporting",
             f_sans_b(19), (255, 255, 255))
    centered(d, W // 2, 1006,
             "CONFIRMED multiple sources  \u00b7  REPORTED single source or developing  \u00b7  CLAIM contested",
             f_sans(13), GOLD)

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(img, d)
    draw_datecheck(d)
    fw = (W - 2 * MARGIN - 8) // 2
    fh = 234
    for i, feat in enumerate(FEATURES):
        col, row = i % 2, i // 2
        x = MARGIN + col * (fw + 8)
        y = 192 + row * (fh + 8)
        draw_feature(img, d, x, y, fw, feat)
    draw_also(d)
    draw_footer(d)
    return img

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out)
    import hashlib
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"stories: {len(FEATURES) + len(INDEX)} "
          f"(features {len(FEATURES)}, index {len(INDEX)})")
    print(f"size: {img.size}, bytes: {len(open(out, 'rb').read())}")
    print(f"truncations: {TRUNCATIONS[0]}")
    print(f"sha256: {h}")

if __name__ == "__main__":
    main()
