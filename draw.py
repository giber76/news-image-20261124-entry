# news-image-20261124 — fresh broadsheet renderer, written from scratch.
# Renders "Tuesday 24 November 2026" (44 verified stories) as a 1024x1024
# PNG broadsheet: masthead + DATE CHECK, THE DAY IN UTC strip, 4 leads
# with literal-scene art, 10 features, dotted world map with 12 numbered
# pins, and an ALSO TODAY panel with the remaining 30 stories.
# Python stdlib + PIL only, no network, deterministic.
# Usage: python3 draw.py [output.png]   (default: entry.png beside this file)

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 235)
INK = (26, 26, 26)
RED = (176, 30, 36)
BLUE = (31, 78, 121)
GREY = (107, 107, 107)
RULE = (201, 194, 178)
FAINT = (222, 216, 202)
GREEN = (46, 125, 50)
AMBER = (166, 110, 0)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BLOCKS = []  # every text block, for the wrap checker


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(text, path, size, max_w, max_lines, min_size=8, line_h=None):
    """Wrap text, shrinking the font until it fits max_lines. Records the
    block for the checker. Ellipsizes only if it still cannot fit."""
    s = size
    while s > min_size:
        f = font(path, s)
        if len(wrap_text(text, f, max_w)) <= max_lines:
            break
        s -= 1
    f = font(path, s)
    lines = wrap_text(text, f, max_w)
    ellipsis = False
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and f.getlength(lines[-1] + "…") > max_w and len(lines[-1]) > 1:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
        ellipsis = True
    lh = line_h if line_h else int(s * 1.28)
    BLOCKS.append({"text": text, "font": path, "size": s, "w": max_w,
                   "max_lines": max_lines, "lines": len(lines), "lh": lh,
                   "h": max_lines * lh, "ellipsis": ellipsis})
    return f, lines, ellipsis


def draw_block(d, x, y, lines, fnt, fill, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=fnt, fill=fill)


def put_text(d, x, y, s, fnt, fill):
    """Single line of text; records it for the checker."""
    d.text((x, y), s, font=fnt, fill=fill)
    BLOCKS.append({"text": s, "font": fnt.path, "size": fnt.size,
                   "w": fnt.getlength(s), "max_lines": 1, "lines": 1,
                   "lh": fnt.size, "h": fnt.size, "ellipsis": False})


# ---------------------------------------------------------------- data

LEADS = [
    {"kicker": "WORLD", "headline": "HUANG IS BACK AT NVIDIA",
     "deck": "Board reinstates Jensen Huang 11 days after he stepped down; "
             "shares jump ~30%, adding almost $1tn. Trump urged the board; "
             "VP Vance pressed it too.",
     "status": "CONFIRMED", "day": "MON", "scene": "chip"},
    {"kicker": "EUROPE", "headline": "COP31 ENDS IN FAILURE",
     "deck": "Antalya summit closes without a final text, the first failure "
             "since 2009; the EU refused a deal silent on fossil fuels.",
     "status": "CONFIRMED", "day": "SUN", "scene": "summit"},
    {"kicker": "ASIA-PACIFIC", "headline": "FACTORY FIRE KILLS 24",
     "deck": "Candy factory blaze in Banten, Indonesia; 24 dead, dozens "
             "missing, search ongoing.",
     "status": "CONFIRMED", "day": "MON", "scene": "fire"},
    {"kicker": "MIDDLE EAST", "headline": "THREE TANKERS HIT MINES IN HORMUZ",
     "deck": "Tankers catch fire in the Strait of Hormuz; Iran vows to end "
             "the US naval blockade.",
     "status": "REPORTED", "day": "MON", "scene": "tanker"},
]

FEATURES = [
    {"headline": "Ukraine sinks Russian warship off Libya",
     "deck": "Seven drones sank the corvette Merkury; Zelensky claimed it.",
     "status": "REPORTED", "day": "MON", "icon": "drone"},
    {"headline": "Meta drops its 2030 net-zero goal",
     "deck": "Meta abandoned the target in its latest sustainability report.",
     "status": "CONFIRMED", "day": "TUE", "icon": "target"},
    {"headline": "CrowdStrike to buy Zscaler for $44bn",
     "deck": "Cybersecurity mega-deal announced 24 Nov.",
     "status": "CONFIRMED", "day": "TUE", "icon": "chart"},
    {"headline": "Trump made $15m on Nvidia shares",
     "deck": "FT: the president profited after Huang's return.",
     "status": "REPORTED", "day": "TUE", "icon": "chart"},
    {"headline": "Russian jet enters Korean airspace",
     "deck": "Seoul briefly issued an evacuation warning.",
     "status": "REPORTED", "day": "TUE", "icon": "jet"},
    {"headline": "US blacklists Megaspeed over Nvidia chips",
     "deck": "Singaporean firm accused of funnelling AI chips to China.",
     "status": "CONFIRMED", "day": "TUE", "icon": "shield"},
    {"headline": "Modi opens AI centre at IIT Patna",
     "deck": "Rs 400-crore research park inaugurated.",
     "status": "CONFIRMED", "day": "MON", "icon": "building"},
    {"headline": "Russian strikes hit Kyiv region",
     "deck": "Drone and missile attacks hit a residential block in Dymer.",
     "status": "REPORTED", "day": "MON", "icon": "burst"},
    {"headline": "World Chess Championship opens",
     "deck": "Gukesh defends his crown against Sindarov in Geneva.",
     "status": "CONFIRMED", "day": "TUE", "icon": "chess"},
    {"headline": "O'Hare ground stop in Thanksgiving rush",
     "deck": "Brief staffing halt at Chicago airport.",
     "status": "CONFIRMED", "day": "MON", "icon": "plane"},
]

# (number, one line, day tag is part of the text)
ALSO = [
    (15, "Trump blasts Newsom in DOJ speech (TUE)"),
    (16, "Trump blames Democrats for $1tn sell-off (TUE)"),
    (17, "Lutnick faces 'hard questions' on Nvidia (TUE)"),
    (18, "Alice Huang 'in contact' with spy agency (TUE)"),
    (19, "Amazon drone crashes into house (TUE)"),
    (20, "ConocoPhillips exits Norway, $4.4bn (TUE)"),
    (21, "Saudis condemn UN building attack (TUE)"),
    (22, "Iran army says it downed US drone (TUE)"),
    (23, "School bomb threats in Germany, Denmark (TUE)"),
    (24, "Dutch activist dies by euthanasia, 28 (TUE)"),
    (25, "Supermoon meets the Pleiades (TUE)"),
    (26, "Manchester concert evacuated (TUE)"),
    (27, "'Not US backyard', ex-presidents say (TUE)"),
    (28, "EU faults Tajikistan for hosting Putin (TUE)"),
    (29, "Armenia starts work on Trump Route (TUE)"),
    (30, "Central Europe queries EU budget (TUE)"),
    (31, "2031 Cup: US, Mexico, Costa Rica, Jamaica (MON)"),
    (32, "Lahore tops pollution ranking, AQI 500+ (MON)"),
    (33, "Catherine: 'Life is not infinite' (MON)"),
    (34, "Charles called Meghan after father's arrest (MON)"),
    (35, "Vienna Swift plot foiled by Mossad tip (MON)"),
    (36, "Russia: no new grain deal, tells UN (MON)"),
    (37, "India-China talks in Arunachal (MON)"),
    (38, "India-Nepal sign 8 MoUs, Rs 15,000-crore (MON)"),
    (39, "India-NZ Test ends in a draw (MON)"),
    (40, "Alcaraz wins maiden ATP Finals (SUN)"),
    (41, "UN weapons talks end, no pact (MON)"),
    (42, "UK sanctions Myanmar generals (MON)"),
    (43, "US sanctions 20+ Iranian exchanges (MON)"),
    (44, "Moscow: Estonia acts 'near open war' (MON)"),
]

# (number, place, lon, lat, label offset dx, dy)
PINS = [
    (1, "Antalya", 30.7, 36.9, 0, 0),
    (2, "Banten", 106.1, -6.1, -16, 10),
    (3, "Hormuz", 56.5, 26.6, 0, 0),
    (4, "Tripoli", 13.2, 32.9, 0, 0),
    (5, "Seoul", 127.0, 37.5, 0, 0),
    (6, "Washington", -77.0, 38.9, 12, -12),
    (7, "Geneva", 6.1, 46.2, 0, 0),
    (8, "Patna", 85.1, 25.6, 0, 0),
    (9, "Kyiv", 30.5, 50.5, 0, 0),
    (10, "Chicago", -87.6, 41.9, -12, 10),
    (11, "Singapore", 103.8, 1.35, 14, -10),
    (12, "Khartoum", 32.5, 15.6, 0, 0),
]

LAND = [
    [(-168, 66), (-156, 71), (-140, 70), (-128, 71), (-115, 73), (-100, 72),
     (-92, 74), (-85, 72), (-80, 73), (-76, 69), (-70, 62), (-65, 60),
     (-60, 55), (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39),
     (-76, 35), (-80, 32), (-81, 26), (-84, 24), (-87, 21), (-90, 15),
     (-92, 15), (-95, 16), (-97, 19), (-101, 21), (-105, 22), (-109, 24),
     (-112, 28), (-115, 31), (-118, 34), (-121, 37), (-124, 42), (-124, 48),
     (-128, 52), (-135, 58), (-145, 60), (-155, 58), (-162, 58), (-168, 66)],
    [(-58, 64), (-52, 60), (-44, 60), (-38, 64), (-30, 68), (-22, 70),
     (-20, 74), (-28, 76), (-40, 78), (-55, 77), (-58, 72)],
    [(-80, 9), (-77, 12), (-72, 12), (-64, 11), (-59, 8), (-52, 5),
     (-50, 0), (-44, -3), (-35, -8), (-38, -15), (-40, -21), (-47, -25),
     (-52, -32), (-58, -36), (-63, -41), (-66, -47), (-69, -52), (-71, -54),
     (-74, -50), (-73, -42), (-72, -32), (-71, -22), (-75, -15), (-79, -8),
     (-81, -3), (-80, 3), (-80, 9)],
    [(-17, 15), (-15, 22), (-10, 30), (-6, 35), (0, 36), (9, 37), (15, 32),
     (20, 32), (25, 31), (30, 31), (34, 28), (37, 22), (40, 16), (44, 11),
     (48, 11), (51, 10), (46, 5), (42, -2), (40, -8), (37, -14), (35, -20),
     (33, -26), (28, -32), (20, -35), (16, -33), (14, -27), (12, -18),
     (11, -8), (9, -1), (9, 4), (0, 6), (-8, 5), (-13, 8), (-16, 12)],
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (0, 50), (3, 52),
     (7, 55), (8, 57), (10, 59), (13, 56), (18, 56), (21, 55), (23, 58),
     (26, 59), (28, 61), (30, 62), (33, 64), (36, 66), (40, 67), (44, 68),
     (48, 69), (54, 69), (60, 70), (66, 71), (72, 72), (78, 72), (84, 74),
     (90, 75), (96, 76), (102, 76), (108, 74), (114, 73), (120, 73),
     (126, 72), (132, 72), (138, 72), (144, 71), (150, 70), (156, 70),
     (162, 69), (168, 67), (174, 66), (178, 65), (176, 62), (170, 60),
     (164, 60), (160, 56), (158, 52), (156, 55), (150, 59), (144, 58),
     (141, 52), (140, 46), (138, 43), (134, 43), (130, 41), (127, 38),
     (125, 35), (122, 32), (120, 28), (117, 24), (113, 22), (109, 18),
     (107, 12), (104, 9), (101, 6), (98, 8), (96, 12), (94, 16), (92, 20),
     (89, 22), (86, 20), (82, 16), (80, 13), (77, 8), (75, 11), (73, 17),
     (70, 21), (67, 23), (63, 25), (59, 25), (55, 26), (52, 27), (49, 29),
     (46, 29), (42, 30), (39, 31), (36, 35), (33, 36), (30, 36), (27, 37),
     (24, 38), (21, 38), (18, 40), (14, 43), (11, 44), (8, 44), (5, 43),
     (2, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    [(-5, 50), (-4, 52), (-3, 54), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50)],
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38),
     (141, 41), (142, 44), (144, 44), (142, 40), (140, 37), (137, 34),
     (134, 33), (131, 32)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (122, -34), (126, -32),
     (130, -32), (134, -34), (137, -35), (140, -38), (145, -38), (149, -37),
     (152, -33), (153, -28), (151, -24), (148, -20), (145, -17), (142, -14),
     (142, -11), (138, -12), (136, -14), (133, -12), (131, -12), (127, -14),
     (124, -16), (121, -19), (117, -21), (113, -22)],
    [(167, -45), (169, -42), (172, -41), (175, -39), (178, -38), (176, -37),
     (174, -39), (172, -42), (169, -44), (167, -46)],
    [(95, 5), (98, 3), (101, 0), (104, -3), (107, -6), (110, -7), (114, -8),
     (118, -9), (121, -10), (125, -9), (128, -7), (131, -4), (134, -4),
     (137, -3), (140, -5), (138, -8), (134, -6), (131, -2), (128, 0),
     (125, 2), (122, 1), (119, 0), (116, 1), (113, 2), (110, 3), (107, 2),
     (104, 1), (101, 3), (98, 5)],
    [(120, 18), (121, 17), (122, 15), (123, 12), (122, 10), (121, 12),
     (120, 15)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21)],
    [(-22, 64), (-18, 63), (-14, 64), (-15, 66), (-19, 66), (-22, 65)],
]


def in_poly(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xin:
                inside = not inside
    return inside


def on_land(lon, lat):
    return any(in_poly(lon, lat, p) for p in LAND)


# ---------------------------------------------------------------- scenes

def scene_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 59, 46))
    # chip
    d.rectangle([x + 22, y + 68, x + 88, y + 134], fill=(18, 42, 34),
                outline=(212, 175, 55), width=2)
    for i in range(5):
        d.rectangle([x + 30 + i * 12, y + 58, x + 36 + i * 12, y + 68],
                    fill=(212, 175, 55))
        d.rectangle([x + 30 + i * 12, y + 134, x + 36 + i * 12, y + 144],
                    fill=(212, 175, 55))
    d.rectangle([x + 38, y + 88, x + 72, y + 114], fill=(53, 208, 127))
    # rising arrow
    d.line([(x + 96, y + 122), (x + 112, y + 98), (x + 122, y + 106),
            (x + 140, y + 72)], fill=(53, 208, 127), width=5)
    d.polygon([(x + 140, y + 72), (x + 128, y + 74), (x + 138, y + 86)],
              fill=(53, 208, 127))
    put_text(d, x + 14, y + 12, "+30%", font(SANS_B, 26), (255, 255, 255))
    put_text(d, x + 14, y + 42, "NVIDIA", font(SANS_B, 11), (140, 200, 170))


def scene_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(191, 217, 232))
    # globe
    d.ellipse([x + 38, y + 10, x + 112, y + 84], fill=(74, 144, 194))
    d.ellipse([x + 52, y + 22, x + 78, y + 44], fill=(127, 176, 105))
    d.ellipse([x + 78, y + 48, x + 102, y + 70], fill=(127, 176, 105))
    d.ellipse([x + 48, y + 56, x + 66, y + 76], fill=(127, 176, 105))
    # empty chairs + table
    for cx in (x + 28, x + 66, x + 104):
        d.rectangle([cx, y + 96, cx + 18, y + 112], fill=(90, 60, 40))
        d.rectangle([cx + 2, y + 88, cx + 16, y + 96], fill=(90, 60, 40))
    d.rectangle([x + 12, y + 112, x + 138, y + 122], fill=(120, 82, 52))
    d.rectangle([x, y + 128, x + w, y + h], fill=RED)
    put_text(d, x + 40, y + 130, "NO DEAL", font(SANS_B, 15),
             (255, 255, 255))


def scene_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 43, 51))
    # glow behind flames
    d.ellipse([x + 30, y + 18, x + 120, y + 92], fill=(120, 50, 20))
    # factory
    d.rectangle([x + 16, y + 84, x + 76, y + 138], fill=(110, 110, 118))
    d.rectangle([x + 84, y + 96, x + 128, y + 138], fill=(90, 90, 98))
    d.rectangle([x + 96, y + 44, x + 110, y + 96], fill=(110, 110, 118))
    for wx in (x + 26, x + 44, x + 62):
        d.rectangle([wx, y + 96, wx + 10, y + 108], fill=(255, 210, 90))
    # flames
    d.polygon([(x + 30, y + 84), (x + 40, y + 52), (x + 48, y + 70),
               (x + 56, y + 44), (x + 64, y + 68), (x + 74, y + 52),
               (x + 78, y + 84)], fill=(255, 140, 0))
    d.polygon([(x + 42, y + 84), (x + 48, y + 62), (x + 56, y + 72),
               (x + 62, y + 60), (x + 68, y + 84)], fill=(255, 210, 0))
    # smoke
    for cx, cy, r in ((x + 100, y + 30, 9), (x + 112, y + 16, 7),
                      (x + 90, y + 12, 6)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 155))


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + 58], fill=(156, 195, 222))
    d.rectangle([x, y + 58, x + w, y + h], fill=(46, 110, 158))
    d.ellipse([x + 112, y + 12, x + 136, y + 36], fill=(255, 220, 120))
    # three tankers, middle one burning
    ships = [(x + 8, y + 74, 52, False), (x + 52, y + 96, 62, True),
             (x + 100, y + 118, 44, False)]
    for sx, sy, sw, burning in ships:
        d.rectangle([sx, sy, sx + sw, sy + 12], fill=(30, 30, 34))
        d.rectangle([sx + sw - 16, sy - 12, sx + sw - 6, sy], fill=(30, 30, 34))
        d.rectangle([sx + 6, sy - 8, sx + 18, sy], fill=(200, 200, 200))
        if burning:
            d.polygon([(sx + 18, sy), (sx + 26, sy - 22), (sx + 32, sy - 8),
                       (sx + 38, sy - 20), (sx + 44, sy)],
                      fill=(255, 140, 0))
    for wy in (y + 92, y + 114, y + 136):
        d.arc([x + 6, wy, x + 60, wy + 12], 180, 360, fill=(220, 235, 245),
              width=2)
        d.arc([x + 80, wy, x + 144, wy + 12], 180, 360, fill=(220, 235, 245),
              width=2)


SCENES = {"chip": scene_chip, "summit": scene_summit, "fire": scene_fire,
          "tanker": scene_tanker}


# ---------------------------------------------------------------- icons

def icon(d, kind, x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=6, fill=(232, 236, 240))
    c = BLUE
    if kind == "drone":
        for dx, dy in ((6, 6), (s - 6, 6), (6, s - 6), (s - 6, s - 6)):
            d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3], fill=c)
        d.line([(x + 6, y + 6), (x + s - 6, y + s - 6)], fill=c, width=2)
        d.line([(x + s - 6, y + 6), (x + 6, y + s - 6)], fill=c, width=2)
        d.ellipse([x + s // 2 - 4, y + s // 2 - 4, x + s // 2 + 4,
                   y + s // 2 + 4], fill=RED)
    elif kind == "target":
        cx, cy = x + s // 2, y + s // 2
        for r in (11, 7, 3):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    elif kind == "chart":
        for i, bh in enumerate((8, 14, 20)):
            bx = x + 7 + i * 9
            d.rectangle([bx, y + s - 6 - bh, bx + 6, y + s - 6], fill=c)
        d.line([(x + 6, y + s - 8), (x + s - 6, y + s - 8)], fill=INK, width=1)
    elif kind == "jet":
        d.polygon([(x + s - 6, y + s // 2), (x + 8, y + 8), (x + 12, y + s // 2),
                   (x + 8, y + s - 8)], fill=c)
        d.polygon([(x + 14, y + s // 2 - 3), (x + 24, y + s // 2),
                   (x + 14, y + s // 2 + 3)], fill=RED)
    elif kind == "shield":
        d.polygon([(x + s // 2, y + 5), (x + s - 6, y + 10), (x + s - 6, y + 20),
                   (x + s // 2, y + s - 5), (x + 6, y + 20), (x + 6, y + 10)],
                  outline=c, width=2)
        d.line([(x + 12, y + 17), (x + 16, y + 22), (x + 24, y + 12)], fill=GREEN,
               width=2)
    elif kind == "building":
        d.rectangle([x + 7, y + 10, x + s - 7, y + s - 6], outline=c, width=2)
        d.polygon([(x + 5, y + 10), (x + s // 2, y + 4), (x + s - 5, y + 10)],
                  fill=c)
        for wx in (x + 11, x + 19):
            for wy in (y + 15, y + 21):
                d.rectangle([wx, wy, wx + 4, wy + 4], fill=c)
    elif kind == "burst":
        cx, cy = x + s // 2, y + s // 2
        pts = []
        for i in range(16):
            ang = math.pi * i / 8
            r = 12 if i % 2 == 0 else 5
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=(255, 170, 0))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    elif kind == "chess":
        d.ellipse([x + 10, y + 7, x + 24, y + 21], fill=c)
        d.polygon([(x + 8, y + 20), (x + 26, y + 20), (x + 28, y + 28),
                   (x + 6, y + 28)], fill=c)
        d.rectangle([x + 6, y + 28, x + 28, y + 30], fill=INK)
    elif kind == "plane":
        d.polygon([(x + s - 5, y + s // 2), (x + 8, y + 8), (x + 13, y + s // 2),
                   (x + 8, y + s - 8)], fill=c)
        d.line([(x + 10, y + 6), (x + 16, y + 2)], fill=c, width=2)
        d.line([(x + 10, y + s - 6), (x + 16, y + s - 2)], fill=c, width=2)


# ---------------------------------------------------------------- render

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 22
    X1, X2 = M, W - M

    # ---- masthead
    put_text(d, X1, 24, "THE DAY IN ONE PAGE", font(SERIF_B, 40), INK)
    d.rectangle([786, 22, 1002, 88], outline=INK, width=2)
    put_text(d, 798, 28, "DATE CHECK", font(SANS_B, 11), RED)
    put_text(d, 798, 50, "TUE 22 · MON 20 · SUN 2", font(SANS_B, 14), INK)
    put_text(d, 798, 68, "All stories 22–24 Nov 2026", font(SANS, 10), GREY)
    put_text(d, X1, 100, "TUESDAY 24 NOVEMBER 2026", font(SANS_B, 17), INK)
    tag = ("Europe 16 · Middle East 4 · Americas 11 · Asia-Pacific 7 · "
           "Africa 1 · Oceania 1 · World 4")
    tf = font(SANS, 12)
    put_text(d, X2 - tf.getlength(tag), 103, tag, tf, GREY)
    d.line([(X1, 126), (X2, 126)], fill=INK, width=2)

    # ---- THE DAY IN UTC strip
    d.rectangle([X1, 132, X2, 164], fill=INK)
    put_text(d, 34, 141, "THE DAY IN UTC", font(SANS_B, 12), (255, 255, 255))
    segs = ["ASIA · Banten fire · Modi AI centre",
            "EUROPE · COP31 fails · Kyiv strikes",
            "AMERICAS · Nvidia +30% · Meta drops goal",
            "WORLD · Chess opens · Alcaraz wins"]
    for i, seg in enumerate(segs):
        sx = 172 + i * 206
        if i:
            d.line([(sx - 8, 138), (sx - 8, 158)], fill=(90, 90, 90), width=1)
        f, lines, _ = fit_block(seg, SANS, 11, 196, 1, min_size=9)
        draw_block(d, sx, 143, lines, f, (235, 235, 235), 12)

    # ---- leads, 2x2
    for i, lead in enumerate(LEADS):
        cx = X1 + (i % 2) * 498
        cy = 172 + (i // 2) * 170
        SCENES[lead["scene"]](d, cx, cy, 150, 150)
        tx, tw = cx + 162, 320
        put_text(d, tx, cy + 2, lead["kicker"], font(SANS_B, 11), RED)
        hf, hlines, _ = fit_block(lead["headline"], SERIF_B, 20, tw, 2,
                                  min_size=16, line_h=24)
        draw_block(d, tx, cy + 20, hlines, hf, INK, 24)
        dy = cy + 20 + len(hlines) * 24 + 6
        df, dlines, _ = fit_block(lead["deck"], SANS, 12, tw, 4, min_size=11,
                                  line_h=16)
        draw_block(d, tx, dy, dlines, df, (58, 58, 58), 16)
        tag_y = cy + 162 - 14
        scol = RED if lead["status"] == "CONFIRMED" else AMBER
        put_text(d, tx, tag_y, lead["status"], font(SANS_B, 10), scol)
        put_text(d, tx + 78, tag_y, "· " + lead["day"], font(SANS_B, 10), GREY)

    # ---- MORE NEWS header
    d.line([(X1, 520), (X2, 520)], fill=INK, width=2)
    put_text(d, X1, 528, "MORE NEWS", font(SERIF_B, 16), INK)
    rf = font(SANS, 11)
    put_text(d, X2 - rf.getlength("10 FEATURES"), 532, "10 FEATURES", rf, GREY)

    # ---- features, 2 columns x 5 rows
    for i, feat in enumerate(FEATURES):
        cx = X1 + (i % 2) * 498
        cy = 548 + (i // 2) * 43
        icon(d, feat["icon"], cx, cy + 4, 34)
        tx, tw = cx + 44, 438
        tag_s = feat["status"] + " · " + feat["day"]
        tagf = font(SANS_B, 10)
        tag_w = tagf.getlength(tag_s)
        hf, hlines, _ = fit_block(feat["headline"], SANS_B, 13, tw - tag_w - 10,
                                  1, min_size=11)
        draw_block(d, tx, cy, hlines, hf, INK, 16)
        scol = RED if feat["status"] == "CONFIRMED" else AMBER
        put_text(d, tx + tw - tag_w, cy + 1, tag_s, tagf, scol)
        df, dlines, _ = fit_block(feat["deck"], SANS, 11, tw, 1, min_size=10)
        draw_block(d, tx, cy + 19, dlines, df, (88, 88, 88), 14)
        d.line([(cx, cy + 41), (cx + 482, cy + 41)], fill=FAINT, width=1)

    # ---- bottom band divider
    d.line([(X1, 768), (X2, 768)], fill=INK, width=2)

    # ---- map panel (left, 430 wide)
    put_text(d, X1, 776, "WHERE IT HAPPENED", font(SERIF_B, 14), INK)
    mx, my, mw, mh = X1, 798, 430, 150
    for lon in (-120, -60, 0, 60, 120):
        gx = mx + (lon + 180) / 360 * mw
        d.line([(gx, my), (gx, my + mh)], fill=FAINT, width=1)
    for lat in (60, 30, 0, -30):
        gy = my + (78 - lat) / 136 * mh
        d.line([(mx, gy), (mx + mw, gy)], fill=FAINT, width=1)
    step = 5
    gx = 0
    while gx <= mw:
        gy = 0
        while gy <= mh:
            lon = gx / mw * 360 - 180
            lat = 78 - gy / mh * 136
            if on_land(lon, lat):
                d.rectangle([mx + gx, my + gy, mx + gx + 1, my + gy + 1],
                            fill=(90, 90, 90))
            gy += step
        gx += step
    nf = font(SANS_B, 8)
    for num, place, lon, lat, dx, dy in PINS:
        px = mx + (lon + 180) / 360 * mw
        py = my + (78 - lat) / 136 * mh
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        lw = nf.getlength(label)
        if dx or dy:
            lx, ly = px + dx, py + dy
            d.line([(px, py), (lx, ly)], fill=RED, width=1)
            d.rectangle([lx - lw / 2 - 2, ly - 6, lx + lw / 2 + 2, ly + 6],
                        fill=(255, 255, 255), outline=RED, width=1)
            d.text((lx - lw / 2, ly - 6), label, font=nf, fill=RED)
            BLOCKS.append({"text": label, "font": SANS_B, "size": 8,
                           "w": lw, "max_lines": 1, "lines": 1, "lh": 8,
                           "h": 8, "ellipsis": False})
        else:
            d.text((px - lw / 2, py - 6), label, font=nf, fill=(255, 255, 255))
            BLOCKS.append({"text": label, "font": SANS_B, "size": 8,
                           "w": lw, "max_lines": 1, "lines": 1, "lh": 8,
                           "h": 8, "ellipsis": False})
    leg1 = "1 Antalya · 2 Banten · 3 Hormuz · 4 Tripoli · 5 Seoul · 6 Washington"
    leg2 = "7 Geneva · 8 Patna · 9 Kyiv · 10 Chicago · 11 Singapore · 12 Khartoum"
    put_text(d, X1, 954, leg1, font(SANS, 10), INK)
    put_text(d, X1, 970, leg2, font(SANS, 10), INK)

    # ---- ALSO TODAY panel (right, 534 wide)
    ax = 468
    put_text(d, ax, 776, "ALSO TODAY", font(SERIF_B, 14), INK)
    rf = font(SANS, 11)
    put_text(d, 1002 - rf.getlength("30 MORE STORIES"), 780, "30 MORE STORIES",
             rf, GREY)
    for i, (num, text) in enumerate(ALSO):
        col, row = divmod(i, 15)
        ix = ax + col * 272
        iy = 798 + row * 13
        nf = font(SANS_B, 9)
        put_text(d, ix, iy, str(num) + ".", nf, RED)
        f, lines, _ = fit_block(text, SANS, 9, 240, 1, min_size=8)
        draw_block(d, ix + 20, iy, lines, f, INK, 11)

    # ---- footer
    foot = ("All 44 stories happened or were first reported 22–24 Nov 2026 · "
            "Sources: BBC, Reuters, FT, NYT, Finimize, One Turn")
    ff = font(SANS, 9)
    put_text(d, (W - ff.getlength(foot)) / 2, 1002, foot, ff, GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG")
    n = os.path.getsize(out)
    print("wrote %s (%d bytes, %s, %s)" % (out, n, img.size, img.mode))
    bad = [b for b in BLOCKS if b["ellipsis"]]
    print("text blocks: %d, ellipsized: %d" % (len(BLOCKS), len(bad)))
    for b in bad:
        print("  TRUNCATED:", b["text"][:60])


if __name__ == "__main__":
    main()
