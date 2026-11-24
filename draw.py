#!/usr/bin/env python3
"""Draw the Tuesday 24 November 2026 broadsheet (news-image-20261124 v4).

Pattern: the attached reference front page ("THE WORLD IN ONE DAY",
35 stories), top to bottom — thin top strip; huge tracked title; red
date line; ticker of top headlines; THE DAY IN NUMBERS (6 figures);
coloured region bar with counts; THE DAY IN UTC timeline with pins;
3 LARGE illustrated features; 12 smaller illustrated cards (3x4);
WHERE IT HAPPENED dotted world map with numbered pins beside the
ALSO - IN BRIEF numbered list; red-bordered DATE CHECK box; footer
with the CONFIRMED / REPORTED / CLAIM legend and sources.

35 stories: 3 features + 12 cards + 20 brief items, picked as the most
consequential of the 46 verified for the day. Only Nepal has a reported
clock time (07:02 local = 01:17 UTC); other timeline pins carry no
invented time. Region count is 6 (no Oceania story in the set).

Usage: python3 draw.py entry.png
Deterministic: no randomness, no timestamps; two runs are byte-identical.
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14

# --- palette (light broadsheet, red accents, like the reference) ------------
PAPER = (247, 243, 234)
INK = (17, 17, 17)
MUTED = (85, 85, 85)
LINE = (17, 17, 17)
RED = (185, 28, 28)
RED_DK = (153, 27, 27)
GOLD = (232, 185, 60)
TEAL = (15, 118, 110)      # CONFIRMED
AMBER = (180, 83, 9)       # REPORTED
CREAM = (255, 255, 255)
TAN = (178, 158, 118)      # map dots
NAVY = (13, 38, 66)
SEA = (14, 116, 144)
SKY = (186, 230, 253)
SAND = (214, 182, 120)
GREEN = (22, 163, 74)

# --- fonts -----------------------------------------------------------------
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def f_sans(size):
    return font(SANS, size)

def f_sans_b(size):
    return font(SANS_B, size)

def f_serif_b(size):
    return font(SERIF_B, size)

# --- data ------------------------------------------------------------------
# 3 LARGE features: (num, region, headline, fact, tag, tag_bg, source, art)
FEATURES = [
    (1, "N. AMERICA",
     "NVIDIA SOARS 30% \u2014 BEST DAY IN OVER A YEAR",
     "HUANG RETURNS AS CEO; STOCK GAINS ~$1 TRILLION; NASDAQ +6.51%.",
     "CONFIRMED", TEAL, "REUTERS \u00b7 AP", "nvidia"),
    (2, "WORLD",
     "COP31 COLLAPSES: NO DEAL, NO PACT",
     "90+ NATIONS REJECT DRAFT; NO FOSSIL-FUEL WORD AFTER ~50 HOURS OVERTIME.",
     "CONFIRMED", TEAL, "REUTERS \u00b7 AP", "cop31"),
    (3, "MIDDLE EAST",
     "TANKERS HIT MINES IN THE STRAIT OF HORMUZ",
     "THREE SHIPS BURN; IRAN VOWS \u2018ALL AVAILABLE MEANS\u2019 VS US BLOCKADE.",
     "REPORTED", AMBER, "REUTERS \u00b7 AP", "hormuz"),
]

# 12 cards: (num, region, headline, tag, tag_bg, source, art)
CARDS = [
    (4, "ASIA", "NEPAL 5.3 QUAKE AT DAWN; NO DEATHS",
     "CONFIRMED", TEAL, "EMSC", "quake"),
    (5, "ASIA", "ICJ: MYANMAR COMMITTED GENOCIDE",
     "CONFIRMED", TEAL, "ICJ", "icj"),
    (6, "MID EAST", "ISRAELI STRIKES KILL HAMAS SECURITY CHIEF",
     "REPORTED", AMBER, "REUTERS", "gaza"),
    (7, "EUROPE", "NATO VOWS TO DEFEND SPACE FROM RUSSIA",
     "REPORTED", AMBER, "REUTERS", "space"),
    (8, "EUROPE", "ZAPORIZHZHIA STRIKE KILLS 2, WOUNDS 40",
     "REPORTED", AMBER, "REUTERS", "zaporizhzhia"),
    (9, "ASIA", "BANTEN FIRE TOLL RISES TO 26",
     "CONFIRMED", TEAL, "REUTERS", "banten"),
    (10, "N. AMERICA", "US LOSES MEASLES-FREE STATUS",
     "CONFIRMED", TEAL, "FDA", "measles"),
    (11, "EUROPE", "SANOFI BUYS INSMED FOR $41 BILLION",
     "CONFIRMED", TEAL, "REUTERS", "sanofi"),
    (12, "ASIA", "SEOUL OFFERS REWARDS TO CATCH AI EXAM CHEATS",
     "REPORTED", AMBER, "REUTERS", "seoul"),
    (13, "LATIN AMERICA", "MEXICO TO TRY \u2018EL CHAPO ISIDRO\u2019",
     "REPORTED", AMBER, "REUTERS", "mexico"),
    (14, "WORLD", "47,000 WOMEN KILLED BY PARTNERS IN 2025",
     "CONFIRMED", TEAL, "UN", "unwomen"),
    (15, "ASIA", "INDIA SEAL ODI SERIES 3\u20131 VS NEW ZEALAND",
     "CONFIRMED", TEAL, "REUTERS", "india"),
]

# 20 brief items: (num, title) — uppercase, one line each
BRIEF = [
    (16, "OREGON, VIRGINIA SUE SPACEX OVER GROK IMAGES"),
    (17, "US BLACKLISTS MEGASPEED OVER AI CHIPS"),
    (18, "GUTERRES URGES AI SAFETY RULES IN A YEAR"),
    (19, "TRUMP ORDERS DOJ TO SPEED UP DEATH SENTENCES"),
    (20, "PENTAGON: CANADA LAGS AS DEFENCE PARTNER"),
    (21, "EU LIMITS ON RUSSIAN VISAS BACKED BY 7 STATES"),
    (22, "IRAQ PM TAKES OVER KURDISH OILFIELDS"),
    (23, "UN URGES PROBE INTO BENGHAZI PORT ATTACKS"),
    (24, "IRAN FLOGS SINGER PARASTOO AHMADI, 74 LASHES"),
    (25, "SOMALIA, UGANDA STEP UP VS AL-SHABAAB"),
    (26, "FDA APPROVES LIMB-GIRDLE DYSTROPHY DRUG"),
    (27, "RUSSIAN JETS ENTER S. KOREA DEFENCE ZONE"),
    (28, "NORWAY IN DIALOGUE WITH UKRAINE"),
    (29, "VANCE, RUBIO MEET QATARI PM AT WHITE HOUSE"),
    (30, "SPAIN ELECTION CAMPAIGN HEATS UP FOR 29 NOV"),
    (31, "ZVEREV WINS ATP FINALS OPENER IN TURIN"),
    (32, "CANARY ISLANDS LOG RECORD MIGRANT ARRIVALS"),
    (33, "POPE LEO XIV VISITS PERU ON POVERTY"),
    (34, "PHILIPPINES WIN FIRST EUROVISION ASIA"),
    (35, "ASEAN SUMMIT OPENS IN MANILA"),
]

# THE DAY IN NUMBERS: (big figure, caption)
NUMBERS = [
    ("30%", "NVIDIA SOARS; NASDAQ +6.51%"),
    ("50", "HOURS OF COP31 OVERTIME"),
    ("3", "TANKERS HIT MINES IN HORMUZ"),
    ("5.3", "NEPAL QUAKE AT DAWN"),
    ("26", "BANTEN FIRE TOLL RISES TO"),
    ("$41B", "SANOFI BUYS INSMED"),
]

# THE DAY IN UTC: (time or None, event) — only Nepal has a reported time
TIMELINE = [
    ("01:17", "NEPAL 5.3 QUAKE"),
    (None, "NVIDIA SOARS 30%"),
    (None, "COP31 COLLAPSES"),
    (None, "HORMUZ TANKERS HIT"),
    (None, "ICJ MYANMAR VERDICT"),
    (None, "BANTEN TOLL 26"),
]

# Region bar: (label, count, colour) — 6 regions with stories in the 35
REGIONS = [
    ("EUROPE", 8, (37, 99, 235)),
    ("ASIA-PAC", 9, (13, 148, 136)),
    ("AMERICAS", 9, (220, 38, 38)),
    ("AFRICA", 2, (234, 88, 12)),
    ("MID EAST", 4, (147, 51, 234)),
    ("WORLD", 3, (75, 85, 99)),
]

# Dotted world map: land spans per row (54 cols x 18 rows, lon -180..180,
# lat ~72..-54). Each span is (col_start, col_end) inclusive.
MAP_SPANS = [
    [(0, 4), (6, 18), (19, 23), (27, 29), (31, 53)],
    [(0, 3), (5, 18), (19, 22), (26, 30), (31, 53)],
    [(5, 17), (25, 32), (31, 53)],
    [(7, 17), (25, 52)],
    [(8, 16), (25, 50)],
    [(9, 15), (24, 35), (38, 47)],
    [(9, 14), (24, 34), (38, 46)],
    [(15, 21), (24, 34), (38, 45)],
    [(15, 20), (25, 33), (41, 43)],
    [(16, 20), (25, 32), (41, 47)],
    [(16, 20), (26, 31), (42, 47)],
    [(17, 20), (26, 30), (41, 50)],
    [(17, 19), (27, 29), (44, 50)],
    [(17, 19), (27, 28), (45, 49), (52, 53)],
    [(18, 19), (45, 48)],
    [(18, 18), (52, 53)],
    [(18, 18)],
    [(18, 18)],
]

# Numbered map pins: (story num, lon, lat) — nudged where two pins collide
PINS = [
    (1, -122, 37), (2, 26, 40), (3, 56.5, 26.5), (4, 87, 27),
    (5, 4.3, 52.1), (6, 37, 29), (8, 38, 49), (9, 106.1, -6.2),
    (10, -77, 40.5), (12, 127, 37.5), (13, -107, 25), (15, 72, 22),
]

TRUNCATIONS = [0]  # any text that had to be cut counts here; must end at 0


# --- helpers ---------------------------------------------------------------
def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)

def wrap_text(draw, text, fnt, max_w):
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

def _font_path_for(fnt):
    p = getattr(fnt, "path", "") or ""
    if p.endswith("DejaVuSans-Bold.ttf"):
        return SANS_B
    if "Serif" in p:
        return SERIF_B
    return SANS

def draw_fitted(draw, text, fnt, max_w, max_lines, xy, fill, shrink=(0, -1, -2, -3, -4)):
    """Wrapped text, max_lines; shrink font if needed; ellipsise (counted)
    only as a last resort."""
    x, y = xy
    path = _font_path_for(fnt)
    size = fnt.size
    for step in shrink:
        f = font(path, max(8, size + step))
        lines = wrap_text(draw, text, f, max_w)
        if len(lines) <= max_lines:
            lh = int(f.size * 1.18)
            for ln in lines:
                draw.text((x, y), ln, font=f, fill=fill)
                y += lh
            return y
    f = font(path, max(8, size + shrink[-1]))
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
    path = _font_path_for(fnt)
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

def centered(draw, cx, y, text, fnt, fill):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)

def tracked_width(draw, text, fnt, tracking):
    total = 0
    for ch in text:
        total += draw.textlength(ch, font=fnt) + tracking
    return total - tracking if text else 0

def draw_tracked(draw, cx, y, text, fnt, fill, max_w, tracking=16):
    """Centred text with wide letter tracking (reference title style);
    tracking shrinks until it fits max_w."""
    tr = tracking
    while tr > 0 and tracked_width(draw, text, fnt, tr) > max_w:
        tr -= 1
    total = tracked_width(draw, text, fnt, tr)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tr

def pill(draw, x, y, text, bg, fg=(255, 255, 255), size=11):
    f = f_sans_b(size)
    w = int(text_w(draw, text, f)) + 12
    h = size + 7
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + 6, y + 3), text, font=f, fill=fg)
    return w


# --- feature art (large, literal scenes) --------------------------------------
def art_nvidia(img, d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 32, 58))
    import random as _r
    rng = _r.Random(24)
    bx = x + 6
    while bx < x + w - 14:
        bw = rng.randint(14, 26)
        bh = rng.randint(18, 62)
        col = (24, 68, 110) if rng.random() < 0.6 else (16, 48, 82)
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=col)
        d.rectangle([bx + 3, y + h - bh + 4, bx + bw - 3, y + h - bh + 8], fill=(52, 130, 190))
        if rng.random() < 0.5:
            d.ellipse([bx + bw // 2 - 2, y + h - bh - 8, bx + bw // 2 + 2, y + h - bh - 4], fill=GOLD)
        bx += bw + 4
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
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy, r = x + 78, y + 58, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(147, 197, 253))
    for k in (-22, 0, 22):
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              start=90, end=270, fill=(255, 255, 255), width=2)
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              start=270, end=90, fill=(30, 90, 140), width=2)
    d.ellipse([cx - r, cy - 7, cx + r, cy + 7], outline=(255, 255, 255), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    stamp = Image.new("RGBA", (200, 64), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 195, 59], radius=8, outline=(239, 68, 68), width=4)
    sd.text((100, 12), "NO DEAL", font=f_sans_b(30), fill=(239, 68, 68), anchor="ma")
    stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (x + w - 225, y + 40), stamp)
    cols = [(185, 28, 28), (232, 185, 60), (255, 255, 255), (15, 118, 110),
            (30, 58, 95), (185, 28, 28), (232, 185, 60)]
    bw = w // len(cols)
    for i, c in enumerate(cols):
        d.rectangle([x + i * bw, y + h - 12, x + (i + 1) * bw, y + h], fill=c)

def art_hormuz(img, d, x, y, w, h):
    d.rectangle([x, y, x + w, y + 52], fill=SKY)
    d.rectangle([x, y + 52, x + w, y + h], fill=SEA)
    d.ellipse([x + w - 62, y + 8, x + w - 30, y + 40], fill=(250, 204, 21))
    d.arc([x + w - 320, y + 10, x + w - 120, y + 120], start=195, end=335, fill=RED, width=4)
    d.arc([x + w - 260, y + 20, x + w - 140, y + 112], start=195, end=335, fill=(239, 68, 68), width=3)
    d.rectangle([x + 52, y + 78, x + 300, y + 104], fill=(10, 10, 12))
    d.rectangle([x + 240, y + 58, x + 272, y + 78], fill=(30, 30, 34))
    d.rectangle([x + 278, y + 64, x + 286, y + 78], fill=(185, 28, 28))
    fx, fy = x + 140, y + 78
    d.polygon([(fx - 16, fy), (fx, fy - 34), (fx + 8, fy - 12), (fx + 18, fy - 26),
               (fx + 26, fy)], fill=(249, 115, 22))
    d.polygon([(fx - 7, fy), (fx + 2, fy - 18), (fx + 12, fy)], fill=(250, 204, 21))
    for yy in (112, 122):
        d.line([(x + 20, y + yy), (x + w - 20, y + yy)], fill=(56, 160, 190), width=2)
    t = "STRAIT OF HORMUZ"
    tw = int(text_w(d, t, f_sans_b(14)))
    d.text((x + w - tw - 12, y + h - 18), t, font=f_sans_b(14), fill=(255, 255, 255))

FEATURE_ART = {"nvidia": art_nvidia, "cop31": art_cop31, "hormuz": art_hormuz}

# --- card art (small scenes, ~26px tall strips) ------------------------------
def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 59))
    pts = [(x + 8, y + h // 2), (x + 60, y + h // 2), (x + 80, y + 4),
           (x + 100, y + h - 4), (x + 120, y + 6), (x + 140, y + h // 2),
           (x + w - 8, y + h // 2)]
    d.line(pts, fill=(250, 204, 21), width=2)
    d.text((x + w - 52, y + 5), "M5.3", font=f_sans_b(13), fill=(255, 255, 255))

def scene_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SAND)
    cx = x + w // 2
    d.polygon([(cx - 26, y + 9), (cx, y + 2), (cx + 26, y + 9)], fill=(240, 230, 210))
    for i in (-1, 0, 1):
        d.rectangle([cx + i * 14 - 3, y + 10, cx + i * 14 + 3, y + h - 3], fill=(250, 244, 230))
    d.rectangle([cx - 30, y + h - 3, cx + 30, y + h], fill=(228, 214, 188))

def scene_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(41, 37, 36))
    d.rectangle([x + 20, y + 8, x + 90, y + h], fill=(87, 83, 78))
    d.rectangle([x + 110, y + 12, x + 160, y + h], fill=(68, 64, 60))
    for wx in (30, 48, 66, 120, 138):
        d.rectangle([x + wx, y + 12, x + wx + 8, y + 20], fill=(250, 204, 21))
    fx = x + 200
    d.polygon([(fx - 8, y + h), (fx, y + 4), (fx + 4, y + 14), (fx + 9, y + 6),
               (fx + 13, y + h)], fill=(249, 115, 22))

def scene_space(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 20, 40))
    import random as _r
    rng = _r.Random(7)
    for _ in range(26):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(3, h - 3)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    cx = x + w // 2
    d.rectangle([cx - 26, y + 8, cx - 8, y + 18], fill=(59, 130, 246))
    d.rectangle([cx - 6, y + 9, cx + 6, y + 17], fill=(226, 232, 240))
    d.rectangle([cx + 8, y + 8, cx + 26, y + 18], fill=(59, 130, 246))
    d.line([(cx, y + 9), (cx, y + 3)], fill=(255, 255, 255), width=2)

def scene_zaporizhzhia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 113, 108))
    d.rectangle([x + 30, y + 4, x + 120, y + h], fill=(168, 162, 158))
    for r in range(3):
        for c in range(4):
            d.rectangle([x + 38 + c * 20, y + 8 + r * 8, x + 48 + c * 20, y + 14 + r * 8],
                        fill=(250, 204, 21))
    d.line([(x + 95, y + 4), (x + 85, y + 12), (x + 98, y + 18), (x + 88, y + h)],
           fill=(30, 27, 25), width=2)
    d.polygon([(x + 150, y + h), (x + 158, y + 10), (x + 166, y + h)], fill=(249, 115, 22))

def scene_banten(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 25, 23))
    d.rectangle([x + 30, y + 10, x + 130, y + h], fill=(87, 83, 78))
    d.polygon([(x + 30, y + 10), (x + 45, y + 2), (x + 60, y + 10),
               (x + 75, y + 2), (x + 90, y + 10), (x + 105, y + 2),
               (x + 120, y + 10), (x + 130, y + 10)], fill=(120, 113, 108))
    d.rectangle([x + 140, y + 2, x + 148, y + h], fill=(120, 113, 108))
    fx = x + 180
    d.polygon([(fx - 10, y + h), (fx, y + 2), (fx + 5, y + 12), (fx + 11, y + 4),
               (fx + 15, y + h)], fill=(249, 115, 22))

def scene_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    cx = x + w // 2
    d.rectangle([cx - 4, y + 4, cx + 4, y + h - 4], fill=(185, 28, 28))
    d.rectangle([cx - 11, y + h // 2 - 4, cx + 11, y + h // 2 + 4], fill=(185, 28, 28))
    for sx, sy in ((30, 6), (60, 18), (w - 40, 8), (w - 70, 18)):
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(185, 28, 28))

def scene_sanofi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(219, 234, 254))
    cx = x + w // 2
    d.rounded_rectangle([cx - 34, y + 8, cx + 34, y + h - 8], radius=8,
                        fill=(185, 28, 28))
    d.rounded_rectangle([cx, y + 8, cx + 34, y + h - 8], radius=8, fill=(255, 255, 255))
    d.ellipse([x + 30, y + 8, x + 44, y + h - 8], fill=(255, 255, 255))
    d.ellipse([x + w - 44, y + 8, x + w - 30, y + h - 8], fill=(185, 28, 28))

def scene_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(254, 243, 199))
    cx = x + w // 2
    d.rectangle([cx - 20, y + 3, cx + 20, y + h - 3], fill=(255, 255, 255),
                outline=(120, 113, 108))
    for i in range(3):
        d.line([(cx - 14, y + 8 + i * 5), (cx + 14, y + 8 + i * 5)], fill=(150, 150, 150), width=1)
    d.ellipse([cx + 30, y + 4, cx + 52, y + h - 4], outline=(22, 163, 74), width=3)
    d.line([(cx + 35, y + h // 2), (cx + 41, y + h - 8), (cx + 49, y + 7)],
           fill=(22, 163, 74), width=3)

def scene_mexico(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(254, 243, 199))
    cx = x + w // 2
    d.ellipse([cx - 34, y + 6, cx - 12, y + h - 6], outline=(60, 60, 60), width=3)
    d.ellipse([cx + 12, y + 6, cx + 34, y + h - 6], outline=(60, 60, 60), width=3)
    d.line([(cx - 12, y + h // 2), (cx + 12, y + h // 2)], fill=(60, 60, 60), width=3)
    d.ellipse([x + w - 30, y + 4, x + w - 14, y + 20], fill=(185, 28, 28))
    d.ellipse([x + w - 25, y + 9, x + w - 19, y + 15], fill=(255, 255, 255))

def scene_unwomen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 27, 75))
    cx = x + w // 2
    d.rectangle([cx - 5, y + 10, cx + 5, y + h - 3], fill=(250, 244, 230))
    d.polygon([(cx - 4, y + 10), (cx, y), (cx + 4, y + 10)], fill=(250, 204, 21))
    d.ellipse([cx - 8, y + h - 3, cx + 8, y + h], fill=(250, 244, 230))

def scene_india(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 83, 45))
    cx = x + w // 2
    d.line([(cx - 20, y + h - 4), (cx + 14, y + 4)], fill=(210, 180, 140), width=7)
    d.ellipse([cx + 18, y + 6, cx + 30, y + 18], fill=(185, 28, 28))
    d.line([(cx - 40, y + h - 6), (cx + 40, y + h - 6)], fill=(255, 255, 255), width=2)

CARD_ART = {"quake": scene_quake, "icj": scene_icj, "gaza": scene_gaza,
            "space": scene_space, "zaporizhzhia": scene_zaporizhzhia,
            "banten": scene_banten, "measles": scene_measles,
            "sanofi": scene_sanofi, "seoul": scene_seoul,
            "mexico": scene_mexico, "unwomen": scene_unwomen,
            "india": scene_india}


# --- dotted world map ----------------------------------------------------------
def draw_map(d, x0, y0):
    dx, dy = 6.8, 6.22
    for r, spans in enumerate(MAP_SPANS):
        for (c0, c1) in spans:
            for c in range(c0, c1 + 1):
                cx = x0 + c * dx + dx / 2
                cy = y0 + r * dy + dy / 2
                d.ellipse([cx - 1.8, cy - 1.8, cx + 1.8, cy + 1.8], fill=TAN)
    map_w, map_h = 54 * dx, 18 * dy
    for num, lon, lat in PINS:
        px = x0 + (lon + 180) / 360 * map_w
        py = y0 + (72 - lat) / 126 * map_h
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=(255, 255, 255), width=1)
        t = str(num)
        tw = text_w(d, t, f_sans_b(8))
        d.text((px - tw / 2, py - 5), t, font=f_sans_b(8), fill=(255, 255, 255))

# --- sections ------------------------------------------------------------------
def draw_top_strip(d):
    centered(d, W // 2, 3,
             "35 STORIES  \u00b7  6 REGIONS  \u00b7  ALL FROM TUESDAY 24 NOVEMBER 2026",
             f_sans_b(11), INK)

def draw_title(d):
    draw_tracked(d, W // 2, 14, "THE WORLD IN ONE DAY", f_sans_b(48), INK, 950, tracking=20)
    draw_tracked(d, W // 2, 54, "TUESDAY 24 NOVEMBER 2026", f_sans_b(20), RED, 700, tracking=4)
    centered(d, W // 2, 78,
             "NVIDIA SOARS 30%  \u2014  COP31 COLLAPSES  \u2014  TANKERS HIT IN HORMUZ  \u2014  ICJ: MYANMAR GENOCIDE",
             f_sans_b(12), RED)

def draw_numbers(d):
    d.line([(MARGIN, 96), (W - MARGIN, 96)], fill=LINE, width=2)
    d.text((MARGIN, 100), "THE DAY IN NUMBERS", font=f_sans_b(11), fill=RED)
    col_w = (W - 2 * MARGIN) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = MARGIN + col_w * i + col_w // 2
        if i:
            d.line([(MARGIN + col_w * i, 104), (MARGIN + col_w * i, 158)], fill=(200, 200, 200), width=1)
        centered(d, cx, 112, num, f_sans_b(30), INK)
        lines = wrap_text(d, cap, f_sans(9), col_w - 12)
        ly = 146
        for ln in lines[:2]:
            centered(d, cx, ly, ln, f_sans(9), MUTED)
            ly += 11
    d.line([(MARGIN, 168), (W - MARGIN, 168)], fill=LINE, width=1)

def draw_regions(d):
    total = sum(c for _, c, _ in REGIONS)
    bar_w = W - 2 * MARGIN
    x = MARGIN
    for _, count, col in REGIONS:
        w = bar_w * count // total
        d.rectangle([x, 172, x + w, 182], fill=col)
        x += w
    counts = "  \u00b7  ".join(f"{label} {count}" for label, count, _ in REGIONS)
    centered(d, W // 2, 184, counts, f_sans_b(11), INK)

def draw_timeline(d):
    d.text((MARGIN, 200), "THE DAY IN UTC", font=f_sans_b(11), fill=RED)
    d.line([(40, 226), (984, 226)], fill=LINE, width=2)
    xs = [150, 310, 470, 630, 790, 950]
    for (tm, ev), px in zip(TIMELINE, xs):
        d.ellipse([px - 5, 221, px + 5, 231], fill=RED)
        if tm:
            centered(d, px, 206, tm, f_sans_b(11), INK)
        centered(d, px, 232, ev, f_sans_b(10), INK)

def draw_feature(img, d, x, y, w, feat):
    num, region, headline, fact, tag, tag_bg, source, art_key = feat
    art_h, text_h = 132, 112
    d.rectangle([x, y, x + w, y + art_h + text_h], outline=LINE, width=1)
    FEATURE_ART[art_key](img, d, x + 1, y + 1, w - 2, art_h - 1)
    ty = y + art_h
    d.rectangle([x + 1, ty, x + w - 1, y + art_h + text_h], fill=CREAM)
    end_y = draw_fitted(d, headline, f_sans_b(19), w - 20, 2, (x + 10, ty + 6), INK)
    draw_fitted(d, fact, f_sans(12), w - 20, 2, (x + 10, end_y + 2), MUTED)
    tag_y = ty + text_h - 24
    tx = x + 10
    label = f"{num} \u00b7 {region}"
    d.text((tx, tag_y + 3), label, font=f_sans_b(11), fill=INK)
    tw = int(text_w(d, label, f_sans_b(11)))
    pill(d, tx + tw + 8, tag_y, tag, tag_bg, size=11)
    sw = int(text_w(d, source, f_sans(9)))
    d.text((x + w - 10 - sw, tag_y + 4), source, font=f_sans(9), fill=MUTED)

def draw_card(d, x, y, w, card):
    num, region, headline, tag, tag_bg, source, art_key = card
    art_h = 26
    d.rectangle([x, y, x + w, y + 74], outline=LINE, width=1)
    CARD_ART[art_key](d, x + 1, y + 1, w - 2, art_h - 1)
    d.rectangle([x + 1, y + art_h, x + w - 1, y + 73], fill=CREAM)
    draw_fitted(d, headline, f_sans_b(11), w - 16, 2, (x + 8, y + 30), INK)
    tag_y = y + 57
    label = f"{num} \u00b7 {region}"
    d.text((x + 8, tag_y + 2), label, font=f_sans_b(10), fill=INK)
    tw = int(text_w(d, label, f_sans_b(10)))
    pill(d, x + 8 + tw + 6, tag_y, tag, tag_bg, size=9)
    sw = int(text_w(d, source, f_sans(8)))
    d.text((x + w - 8 - sw, tag_y + 3), source, font=f_sans(8), fill=MUTED)

def draw_map_brief(d):
    d.text((MARGIN, 804), "WHERE IT HAPPENED", font=f_sans_b(13), fill=INK)
    d.text((410, 804), "ALSO \u2014 IN BRIEF", font=f_sans_b(13), fill=INK)
    draw_map(d, 20, 820)
    for i, (num, title) in enumerate(BRIEF):
        col, row = divmod(i, 10)
        cx = 410 + col * 300
        cy = 820 + row * 11.2
        draw_single(d, f"{num}. {title}", f_sans_b(9), 286, (cx, cy), INK)

def draw_datecheck(d):
    d.rectangle([MARGIN, 938, W - MARGIN, 988], outline=RED, width=2)
    body = ("WIRES READ TO 22:00 UTC. EVERY STORY HERE WAS REPORTED ON TUESDAY "
            "24 NOVEMBER IN AT LEAST ONE ZONE. LEFT OUT ON PURPOSE: BANTEN FIRE "
            "ITSELF (SAT 21 NOV \u2014 SHOWN ONLY FOR ITS 24 NOV TOLL UPDATE). "
            "NOT YET: SPAIN VOTES 29 NOV. CUT FOR SPACE (11): LIBYA CORVETTE \u00b7 "
            "ITURI EBOLA \u00b7 SENEGAL AFCON \u00b7 SA CRICKET \u00b7 ARM HAAS \u00b7 "
            "QUASAR FIND \u00b7 BRENTFORD\u2013MONZA \u00b7 BRAZIL\u2013JAPAN \u00b7 "
            "GREMIO\u2013SANTOS \u00b7 PERSIJA 7\u20130 \u00b7 PYRAMIDS\u2013AL AHLY.")
    lead = "DATE CHECK \u2014 "
    lf, bf = f_sans_b(10), f_sans(10)
    lw = int(text_w(d, lead, lf))
    inner_w = W - 2 * MARGIN - 20
    lines = wrap_text(d, body, bf, inner_w)
    # first line shares its row with the red lead-in
    first_w = inner_w - lw
    first = wrap_text(d, body, bf, first_w)
    rest = body
    # re-wrap: take words that fit on line 1 after the lead, then the rest
    words = body.split()
    line1, used = [], 0
    i = 0
    while i < len(words):
        trial = " ".join(line1 + [words[i]])
        if text_w(d, trial, bf) <= first_w:
            line1.append(words[i])
            i += 1
        else:
            break
    rest = " ".join(words[i:])
    rest_lines = wrap_text(d, rest, bf, inner_w) if rest else []
    all_lines = [" ".join(line1)] + rest_lines
    yy = 946
    d.text((MARGIN + 10, yy), lead, font=lf, fill=RED)
    d.text((MARGIN + 10 + lw, yy), all_lines[0], font=bf, fill=INK)
    yy += 12
    for ln in all_lines[1:4]:
        d.text((MARGIN + 10, yy), ln, font=bf, fill=INK)
        yy += 12
    if len(all_lines) > 4:
        TRUNCATIONS[0] += 1

def draw_footer(d):
    centered(d, W // 2, 992,
             "CONFIRMED = NAMED SOURCE REPORTS IT  \u00b7  REPORTED = WIRE-REPORTED, NOT YET CONFIRMED  \u00b7  CLAIM = ONE SIDE\u2019S ACCOUNT, CONTESTED",
             f_sans_b(10), INK)
    centered(d, W // 2, 1003,
             "SOURCES: REUTERS \u00b7 AP \u00b7 JUST SECURITY \u00b7 THE DAILY EDITION \u00b7 PRINCIPIA \u00b7 HORIZON \u00b7 EMSC \u00b7 XINHUA \u00b7 CAS \u00b7 UN \u00b7 WHO \u00b7 ICJ \u00b7 FDA",
             f_sans(9), MUTED)
    centered(d, W // 2, 1014,
             "SCENES ARE DRAWN ILLUSTRATIONS OF REPORTED EVENTS, NOT PHOTOGRAPHS",
             f_sans(9), MUTED)

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top_strip(d)
    draw_title(d)
    draw_numbers(d)
    draw_regions(d)
    draw_timeline(d)
    fw = (W - 2 * MARGIN - 2 * 8) // 3
    for i, feat in enumerate(FEATURES):
        x = MARGIN + i * (fw + 8)
        draw_feature(img, d, x, 248, fw, feat)
    for i, card in enumerate(CARDS):
        col, row = i % 3, i // 3
        x = MARGIN + col * (fw + 8)
        y = 500 + row * 74
        draw_card(d, x, y, fw, card)
    draw_map_brief(d)
    draw_datecheck(d)
    draw_footer(d)
    return img

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out)
    import hashlib
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"stories: {len(FEATURES) + len(CARDS) + len(BRIEF)} "
          f"(features {len(FEATURES)}, cards {len(CARDS)}, brief {len(BRIEF)})")
    print(f"size: {img.size}, bytes: {len(open(out, 'rb').read())}")
    print(f"truncations: {TRUNCATIONS[0]}")
    print(f"sha256: {h}")

if __name__ == "__main__":
    main()
