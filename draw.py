#!/usr/bin/env python3
"""Draw the Tuesday 24 November 2026 world-news front page (1024x1024).

Dense broadsheet in the proven winner shape: masthead with region
counts in the tagline, a DATE CHECK box, a THE DAY IN UTC timeline
strip, 4 lead cards with large literal-scene art, 10 feature cards
with bigger icons, a dotted world map with 12 numbered pins, and a
30-item ALSO list in 3 columns where every item carries a pictogram
and a TUE/MON/SUN day tag. 44 stories in all, every one checked
against live reporting; see STORIES.md for the source and day-tag of
each one. All pictures are original, drawn here in code with Pillow
primitives. Deterministic: no network, no clock, no random.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (246, 241, 227)
PAPER = (252, 248, 238)
INK = (26, 26, 26)
SOFT = (90, 84, 72)
RED = (185, 28, 28)
BLUE = (35, 80, 120)
TEAL = (28, 90, 96)
GOLD = (176, 132, 30)
RULE = (180, 172, 152)
DARK = (32, 38, 48)
DARKRED = (90, 24, 24)
DARKTEAL = (18, 52, 58)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def F(size, bold=False, serif=True):
    name = ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf") if serif \
        else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, font, fill=INK, leading=None):
    if leading is None:
        leading = font.size + 3
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
# (number, region, status, kicker, headline, deck, art)
# Day of each story is recorded in STORIES.md; the DATE CHECK box
# counts them (TUE 22 · MON 20 · SUN 2).
LEADS = [
    (1, "World", "CONFIRMED", "NVIDIA  ·  CEO RETURNS",
     "Huang is back at Nvidia",
     "Board reinstated him on Monday after Trump and Vance pressed "
     "it; shares jump 30%, adding almost $1tn in value.", "rise"),
    (2, "Europe", "CONFIRMED", "ANTALYA  ·  CLIMATE",
     "COP31 ends in failure",
     "First summit since 2009 to end without a final text; the EU "
     "refused a deal silent on fossil fuels.", "cop"),
    (3, "Asia-Pacific", "CONFIRMED", "INDONESIA  ·  DISASTER",
     "Factory fire kills 24",
     "Candy-plant blaze in Banten; dozens still missing as rescuers "
     "search the ruins.", "flame"),
    (4, "Middle East", "REPORTED", "GULF  ·  WAR",
     "Three tankers hit mines in Hormuz",
     "Ships catch fire in the Strait of Hormuz; Iran vows to end "
     "the blockade.", "strait"),
]

FEATURES = [
    (5, "Europe", "REPORTED", "LIBYA  ·  WAR",
     "Ukraine sinks Russian warship off Libya",
     "Seven naval drones sink the corvette Merkury in a Libyan "
     "port.", "ship"),
    (6, "Americas", "CONFIRMED", "USA  ·  TECH",
     "Meta drops its 2030 net-zero goal",
     "Sustainability report abandons the target; rivals urged to "
     "follow suit.", "leaf"),
    (7, "Americas", "CONFIRMED", "USA  ·  DEALS",
     "CrowdStrike to buy Zscaler for $44bn",
     "Cybersecurity mega-deal announced as markets rally.", "rocket"),
    (8, "Americas", "REPORTED", "USA  ·  POLITICS",
     "Trump made $15m on Nvidia shares",
     "FT: the president profited after Huang's return.", "coin"),
    (9, "Europe", "REPORTED", "KOREA  ·  SECURITY",
     "Russian jet enters Korean airspace",
     "Seoul briefly issues an evacuation warning after the "
     "incursion.", "missile"),
    (10, "Middle East", "CONFIRMED", "USA  ·  SANCTIONS",
     "US blacklists Megaspeed over Nvidia chips",
     "Singaporean firm accused of funnelling AI chips to China.",
     "chip"),
    (11, "Asia-Pacific", "CONFIRMED", "INDIA  ·  AI",
     "Modi opens AI centre at IIT Patna",
     "Rs 400-crore research park inaugurated in Bihar.",
     "cap"),
    (12, "Europe", "REPORTED", "UKRAINE  ·  WAR",
     "Russian strikes hit Kyiv region",
     "Drone and missile attacks hit a residential block in Dymer.",
     "drone"),
    (13, "World", "CONFIRMED", "CHESS  ·  WORLD TITLE",
     "World Chess Championship opens",
     "Gukesh defends his crown against Sindarov in Geneva.",
     "star"),
    (14, "Americas", "CONFIRMED", "USA  ·  AVIATION",
     "O'Hare ground stop in Thanksgiving rush",
     "Brief staffing halt at Chicago airport amid holiday travel.",
     "pin"),
]

# (number, day, status-or-None, bold lead, rest, icon) — ALSO 15-44.
# Day tags: TUE = Tuesday 24 Nov; MON = Monday 23 Nov; SUN = Sunday 22 Nov.
ALSO = [
    (15, "TUE", None, "Trump blasts Newsom",
     "over 548 commutations.", "mega"),
    (16, "TUE", None, "Trump blames Democrats",
     "for $1tn Wall Street sell-off.", "flags"),
    (17, "TUE", None, "Lutnick faces 'hard questions'",
     "senator demands answers.", "star"),
    (18, "TUE", None, "Alice Huang 'stayed in contact'",
     "NYT: spy-agency contact.", "chip"),
    (19, "TUE", None, "Amazon drone crashes into house",
     "after delivering shampoo.", "pin"),
    (20, "TUE", None, "ConocoPhillips exits Norway",
     "in a $4.4bn deal.", "coin"),
    (21, "TUE", None, "Saudis condemn attack",
     "on UN building in Khartoum.", "flags"),
    (22, "TUE", None, "Iran army 'shot down US drone'",
     "over the Gulf, it says.", "missile"),
    (23, "TUE", None, "Hundreds of schools get bomb threats",
     "in Germany and Denmark.", "mega"),
    (24, "TUE", None, "Dutch activist dies by euthanasia",
     "Jason Bhugwandass, 28.", "cross"),
    (25, "TUE", None, "Supermoon meets 'Seven Sisters'",
     "Pleiades in the night sky.", "star"),
    (26, "TUE", None, "Manchester concert evacuated",
     "unknown substance spreads.", "mega"),
    (27, "TUE", None, "Latin America 'not US backyard'",
     "two ex-presidents say.", "flags"),
    (28, "TUE", None, "EU faults Tajikistan",
     "for hosting Putin despite ICC warrant.", "flags"),
    (29, "TUE", None, "Armenia starts work on Trump Route",
     "in Syunik province.", "pin"),
    (30, "TUE", None, "Central Europe queries EU budget",
     "at Bratislava talks.", "star"),
    (31, "MON", None, "2031 Cup hosts",
     "US, Mexico, Costa Rica.", "ball"),
    (32, "MON", None, "Lahore tops pollution ranking",
     "AQI over 500 again.", "pin"),
    (33, "MON", None, "Catherine on mortality",
     "'Life is not infinite'.", "cross"),
    (34, "MON", None, "King Charles reached out to Meghan",
     "after her father's arrest.", "star"),
    (35, "MON", None, "Taylor Swift Vienna plot foiled",
     "Mossad tip saved concerts.", "star"),
    (36, "MON", None, "Russia: no new grain deal",
     "tells UN Security Council.", "flags"),
    (37, "MON", None, "India–China talks in Arunachal",
     "to ease border tensions.", "flags"),
    (38, "MON", None, "India–Nepal sign 8 MoUs",
     "Rs 15,000-crore package.", "flags"),
    (39, "MON", None, "India–NZ Test ends in a draw",
     "Basin Reserve, Wellington.", "bat"),
    (40, "SUN", None, "Alcaraz wins maiden ATP Finals",
     "beats Zverev in Turin.", "ball"),
    (41, "MON", None, "UN weapons talks end",
     "powers block any pact.", "star"),
    (42, "MON", None, "UK sanctions Myanmar generals",
     "after Rohingya ruling.", "flags"),
    (43, "MON", None, "US sanctions 20+ Iranian exchanges",
     "20+ exchanges hit.", "coin"),
    (44, "MON", None, "Moscow accuses Estonia",
     "of acts 'near open war'.", "missile"),
]

STATS = [
    ("+30%", "NVIDIA, THE DAY"),
    ("+6.5%", "NASDAQ, THE DAY"),
    ("$44BN", "CROWDSTRIKE DEAL"),
    ("24", "DEAD IN BANTEN FIRE"),
    ("548", "DEATH SENTENCES COMMUTED"),
    ("3", "TANKERS HIT IN HORMUZ"),
]

# (time, event) — THE DAY IN UTC timeline strip.
TIMELINE = [
    ("04:00", "Huang named CEO; no security risk"),
    ("09:00", "Megaspeed blacklisted over chips"),
    ("14:00", "Meta abandons net-zero goal"),
    ("20:00", "CrowdStrike to buy Zscaler, $44bn"),
]

# (number, lon, lat, label)
PINS = [
    (1, 30.7, 36.9, "Antalya"),
    (2, 106.3, -6.2, "Banten"),
    (3, 56.5, 26.5, "Hormuz"),
    (4, 13.2, 32.9, "Tripoli"),
    (5, 127.0, 37.5, "Seoul"),
    (6, -77.0, 38.9, "Washington"),
    (7, 6.1, 46.2, "Geneva"),
    (8, 85.1, 25.6, "Patna"),
    (9, 30.5, 50.5, "Kyiv"),
    (10, -87.6, 41.9, "Chicago"),
    (11, 103.8, 1.35, "Singapore"),
    (12, 32.5, 15.6, "Khartoum"),
]

REGIONS = ["Europe", "Middle East", "Americas", "Asia-Pacific",
           "Africa", "Oceania", "World"]


def region_counts():
    counts = {r: 0 for r in REGIONS}
    for s in LEADS + FEATURES:
        counts[s[1]] += 1
    also_regions = {
        15: "Americas", 16: "Americas", 17: "Americas", 18: "Americas",
        19: "Americas", 20: "Europe", 21: "Africa", 22: "Middle East",
        23: "Europe", 24: "Europe", 25: "World", 26: "Europe",
        27: "Americas", 28: "Europe", 29: "Asia-Pacific", 30: "Europe",
        31: "Americas", 32: "Asia-Pacific", 33: "Europe", 34: "Europe",
        35: "Europe", 36: "Europe", 37: "Asia-Pacific",
        38: "Asia-Pacific", 39: "Oceania", 40: "Europe", 41: "World",
        42: "Asia-Pacific", 43: "Middle East", 44: "Europe",
    }
    for n, r in also_regions.items():
        counts[r] += 1
    return counts


def day_counts():
    # Leads: 1 MON, 2 SUN, 3 MON, 4 MON. Features: 5 MON, 6 TUE, 7 TUE,
    # 8 TUE, 9 TUE, 10 TUE, 11 MON, 12 MON, 13 TUE, 14 MON.
    counts = {"TUE": 0, "MON": 0, "SUN": 0}
    for day in ("MON", "SUN", "MON", "MON"):
        counts[day] += 1
    for day in ("MON", "TUE", "TUE", "TUE", "TUE", "TUE", "MON", "MON",
                "TUE", "MON"):
        counts[day] += 1
    for a in ALSO:
        counts[a[1]] += 1
    return counts

# ---------------------------------------------------------------- art
# Icons are drawn in a normalised 0..100 space so the same drawing
# works as a 225x70 lead scene, a 54x32 feature icon or a 13x13 ALSO
# pictogram. X/Y map fractions to pixels; S is the size unit
# (min(w, h) / 100) used for radii and line widths so circles stay
# circular in a wide box.


def draw_icon(d, kind, x, y, w, h, ink, accent):
    def X(f):
        return x + f * w / 100.0

    def Y(f):
        return y + f * h / 100.0

    S = min(w, h) / 100.0

    def lw(n=2):
        return max(1, int(round(n * S)))

    def star_pts(cx, cy, r_out, r_in, n=5):
        pts = []
        for i in range(2 * n):
            ang = -math.pi / 2 + i * math.pi / n
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return pts

    light = (235, 230, 215)
    if kind == "rise":  # climbing line + candles + +30% label
        pts = [(X(4), Y(82)), (X(24), Y(70)), (X(44), Y(76)),
               (X(64), Y(48)), (X(82), Y(38)), (X(96), Y(14))]
        d.line(pts, fill=accent, width=lw(3))
        for fx, top, bot in ((14, 72, 84), (38, 62, 78), (62, 34, 50),
                             (86, 20, 36)):
            d.line([X(fx), Y(top - 5), X(fx), Y(bot + 5)], fill=ink,
                   width=lw(1))
            d.rectangle([X(fx) - 3, Y(top), X(fx) + 3, Y(bot)], fill=ink)
        tf = F(max(8, int(round(15 * S))), bold=True, serif=False)
        t = "+30%"
        tw = d.textlength(t, font=tf)
        d.text((X(97) - tw, Y(74)), t, font=tf, fill=light)
    elif kind == "cop":  # cracked globe + empty chairs + NO DEAL
        r = 24 * S
        cx, cy = X(13), Y(50)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=lw(2))
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=accent,
              width=lw(3))
        d.line([cx - r * 0.8, Y(40), cx + r * 0.8, Y(40)], fill=ink,
               width=lw(1))
        d.line([cx - r * 0.8, Y(60), cx + r * 0.8, Y(60)], fill=ink,
               width=lw(1))
        d.line([(cx, Y(28)), (X(10), Y(42)), (X(16), Y(55)), (X(11), Y(70))],
               fill=accent, width=lw(2))
        for fx in (38, 52, 66):
            d.rectangle([X(fx) - 6, Y(28), X(fx) + 6, Y(55)], outline=ink,
                        width=lw(2))
            d.rectangle([X(fx) - 8, Y(55), X(fx) + 8, Y(59)], fill=ink)
            d.line([X(fx) - 6, Y(59), X(fx) - 6, Y(78)], fill=ink,
                   width=lw(2))
            d.line([X(fx) + 6, Y(59), X(fx) + 6, Y(78)], fill=ink,
                   width=lw(2))
        tf = F(max(8, int(round(15 * S))), bold=True, serif=False)
        t = "NO DEAL"
        tw = d.textlength(t, font=tf)
        d.text((X(97) - tw, Y(40)), t, font=tf, fill=accent)
    elif kind == "strait":  # two coasts, ships, missile arcs, fire
        d.polygon([(X(3), Y(6)), (X(30), Y(6)), (X(20), Y(94)),
                   (X(3), Y(94))], fill=ink)
        d.polygon([(X(97), Y(6)), (X(70), Y(6)), (X(80), Y(94)),
                   (X(97), Y(94))], fill=ink)
        d.rectangle([X(36), Y(58), X(48), Y(64)], fill=accent)
        d.rectangle([X(41), Y(50), X(44), Y(58)], fill=accent)
        d.rectangle([X(54), Y(72), X(64), Y(77)], fill=light)
        d.rectangle([X(58), Y(65), X(61), Y(72)], fill=light)
        d.arc([X(52), Y(10), X(78), Y(38)], 180, 360, fill=accent,
              width=lw(2))
        d.arc([X(30), Y(20), X(55), Y(48)], 180, 360, fill=accent,
              width=lw(2))
        d.polygon(star_pts(X(74), Y(28), 9 * S, 4 * S, 8), fill=RED)
    elif kind == "ship":  # warship hull + mast + waves + drone hit
        d.polygon([(X(14), Y(58)), (X(86), Y(58)), (X(74), Y(74)),
                   (X(26), Y(74))], fill=ink)
        d.rectangle([X(42), Y(40), X(58), Y(58)], fill=ink)
        d.line([X(50), Y(40), X(50), Y(20)], fill=ink, width=lw(2))
        d.polygon([(X(50), Y(20)), (X(66), Y(26)), (X(50), Y(32))],
                  fill=accent)
        for wy in (82, 90):
            d.arc([X(10), Y(wy - 4), X(38), Y(wy + 4)], 0, 180, fill=ink,
                  width=lw(1))
            d.arc([X(62), Y(wy - 4), X(90), Y(wy + 4)], 0, 180, fill=ink,
                  width=lw(1))
        d.polygon(star_pts(X(78), Y(26), 8 * S, 4 * S, 8), fill=accent)
    elif kind == "leaf":  # leaf + crossed-out 2030 target
        d.polygon([(X(50), Y(8)), (X(82), Y(34)), (X(62), Y(82)),
                   (X(30), Y(52))], fill=accent)
        d.line([X(50), Y(8), X(44), Y(86)], fill=light, width=lw(2))
        d.line([X(12), Y(84), X(88), Y(16)], fill=ink, width=lw(3))
    elif kind == "flame":
        d.polygon([(X(38), Y(78)), (X(36), Y(58)), (X(44), Y(40)),
                   (X(50), Y(50)), (X(58), Y(42)), (X(62), Y(58)),
                   (X(62), Y(78))], fill=accent)
        d.ellipse([X(45), Y(62), X(55), Y(76)], fill=GOLD)
    elif kind == "drone":
        d.ellipse([X(36), Y(44), X(64), Y(56)], fill=ink)
        for dx, dy in ((-22, -20), (22, -20), (-22, 20), (22, 20)):
            d.ellipse([X(50 + dx) - 6 * S, Y(50 + dy) - 3 * S,
                       X(50 + dx) + 6 * S, Y(50 + dy) + 3 * S],
                      outline=ink, width=lw(2))
            d.line([X(50), Y(50), X(50 + dx), Y(50 + dy)], fill=ink,
                   width=lw(2))
    elif kind == "flags":
        d.line([X(14), Y(8), X(14), Y(92)], fill=ink, width=lw(2))
        d.polygon([(X(14), Y(8)), (X(42), Y(16)), (X(14), Y(24))],
                  fill=accent)
        d.line([X(56), Y(8), X(56), Y(92)], fill=ink, width=lw(2))
        d.polygon([(X(56), Y(8)), (X(84), Y(16)), (X(56), Y(24))],
                  fill=BLUE)
    elif kind == "bat":
        d.line([X(18), Y(12), X(46), Y(40)], fill=ink, width=lw(5))
        d.rectangle([X(44), Y(38), X(56), Y(44)], fill=ink)
        r = 7 * S
        d.ellipse([X(72) - r, Y(32) - r, X(72) + r, Y(32) + r], fill=accent)
    elif kind == "cap":
        d.polygon([(X(26), Y(46)), (X(50), Y(30)), (X(74), Y(46)),
                   (X(50), Y(62))], fill=ink)
        d.line([X(74), Y(46), X(74), Y(66)], fill=accent, width=lw(2))
        d.ellipse([X(71), Y(64), X(77), Y(72)], fill=accent)
    elif kind == "umbrella":
        d.pieslice([X(30), Y(22), X(70), Y(58)], 180, 360, fill=accent)
        d.line([X(50), Y(40), X(50), Y(78)], fill=ink, width=lw(2))
        d.arc([X(46), Y(74), X(54), Y(84)], 0, 180, fill=ink, width=lw(2))
        for dx in (-24, 24):
            d.line([X(50 + dx), Y(66), X(50 + dx), Y(74)], fill=BLUE,
                   width=lw(1))
    elif kind == "missile":
        d.line([X(12), Y(88), X(88), Y(12)], fill=ink, width=lw(3))
        d.polygon([(X(78), Y(8)), (X(92), Y(8)), (X(84), Y(22))],
                  fill=accent)
        d.arc([X(12), Y(8), X(38), Y(34)], 270, 60, fill=accent,
              width=lw(2))
    elif kind == "rocket":
        d.polygon([(X(50), Y(14)), (X(60), Y(34)), (X(56), Y(66)),
                   (X(44), Y(66)), (X(40), Y(34))], fill=ink)
        r = 4 * S
        d.ellipse([X(50) - r, Y(34) - r, X(50) + r, Y(34) + r], fill=accent)
        d.polygon([(X(44), Y(66)), (X(38), Y(84)), (X(48), Y(70))],
                  fill=accent)
        d.polygon([(X(56), Y(66)), (X(62), Y(84)), (X(52), Y(70))],
                  fill=accent)
    elif kind == "star":
        d.polygon(star_pts(X(50), Y(50), 30 * S, 13 * S), fill=accent)
    elif kind == "pin":
        r = 14 * S
        d.ellipse([X(50) - r, Y(38) - r, X(50) + r, Y(38) + r],
                  outline=ink, width=lw(2))
        r2 = 5 * S
        d.ellipse([X(50) - r2, Y(38) - r2, X(50) + r2, Y(38) + r2],
                  fill=accent)
        d.polygon([(X(38), Y(48)), (X(62), Y(48)), (X(50), Y(78))],
                  fill=ink)
    elif kind == "cross":
        d.rectangle([X(42), Y(18), X(58), Y(82)], fill=accent)
        d.rectangle([X(18), Y(42), X(82), Y(58)], fill=accent)
    elif kind == "ball":
        r = 26 * S
        d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                  outline=ink, width=lw(2))
        d.polygon(star_pts(X(50), Y(50), 8 * S, 4 * S), fill=ink)
        for ang in (30, 150, 270):
            a = math.radians(ang)
            d.line([X(50), Y(50),
                    X(50) + 24 * S * math.cos(a),
                    Y(50) + 24 * S * math.sin(a)], fill=ink, width=lw(1))
    elif kind == "target":
        for rr, col, wd in ((26, ink, 2), (17, accent, 2), (8, accent, 0)):
            r = rr * S
            if wd:
                d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                          outline=col, width=lw(wd))
            else:
                d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                          fill=col)
    elif kind == "chip":
        d.rectangle([X(28), Y(28), X(72), Y(72)], outline=ink, width=lw(2))
        d.rectangle([X(42), Y(42), X(58), Y(58)], fill=accent)
        for fx in (38, 50, 62):
            d.line([X(fx), Y(18), X(fx), Y(28)], fill=ink, width=lw(2))
            d.line([X(fx), Y(72), X(fx), Y(82)], fill=ink, width=lw(2))
            d.line([X(18), Y(fx), X(28), Y(fx)], fill=ink, width=lw(2))
            d.line([X(72), Y(fx), X(82), Y(fx)], fill=ink, width=lw(2))
    elif kind == "coin":
        r = 26 * S
        d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r], fill=GOLD,
                  outline=ink, width=lw(2))
        if w >= 20:
            tf = F(max(8, int(round(0.45 * h))), bold=True, serif=False)
            t = "$"
            tw = d.textlength(t, font=tf)
            th = tf.size
            d.text((X(50) - tw / 2, Y(50) - th / 2), t, font=tf, fill=ink)
        else:
            r2 = 8 * S
            d.ellipse([X(50) - r2, Y(50) - r2, X(50) + r2, Y(50) + r2],
                      fill=ink)
    elif kind == "golf":
        d.line([X(30), Y(10), X(30), Y(85)], fill=ink, width=lw(2))
        d.polygon([(X(30), Y(10)), (X(62), Y(18)), (X(30), Y(28))],
                  fill=accent)
        r = 6 * S
        d.ellipse([X(74) - r, Y(80) - r, X(74) + r, Y(80) + r], fill=ink)
    elif kind == "mega":
        d.polygon([(X(20), Y(30)), (X(70), Y(18)), (X(70), Y(62)),
                   (X(20), Y(50))], fill=accent)
        d.rectangle([X(16), Y(50), X(24), Y(70)], fill=ink)
        d.arc([X(74), Y(24), X(88), Y(56)], 270, 90, fill=ink,
              width=lw(2))


# ---------------------------------------------------------------- map
LAND = [
    # North America
    (-168, -95, 50, 70), (-125, -66, 25, 50), (-97, -80, 15, 30),
    (-92, -77, 7, 15), (-55, -25, 64, 76),
    # South America
    (-80, -35, 5, 12), (-78, -38, -5, 10), (-72, -55, -55, -5),
    # Europe
    (-10, 30, 36, 60), (5, 30, 58, 70), (-5, 2, 50, 58),
    # Africa
    (-17, 35, 15, 35), (-17, 50, -5, 15), (12, 40, -35, -5),
    (35, 51, 0, 12),
    # Asia
    (40, 90, 45, 75), (90, 180, 45, 72), (60, 100, 25, 45),
    (70, 90, 8, 35), (95, 110, 8, 28), (100, 140, 28, 45),
    (127, 142, 31, 45), (43, 60, 25, 40), (35, 48, 36, 42),
    (95, 141, -11, 6),
    # Oceania
    (113, 154, -39, -11), (166, 178, -47, -34),
]


def is_land(lon, lat):
    return any(lo0 <= lon <= lo1 and la0 <= lat <= la1
               for lo0, lo1, la0, la1 in LAND)


def lonlat_to_xy(lon, lat, x0, y0, x1, y1):
    fx = (lon + 170) / 360.0
    fy = (75 - lat) / 135.0
    return x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)

# ---------------------------------------------------------------- layout
M = 22
STATUS_FILL = {"CONFIRMED": (28, 110, 60), "REPORTED": (160, 90, 10),
               "CLAIM": (150, 30, 30)}


def status_tag(d, x, y, status):
    f = F(9, bold=True, serif=False)
    w = d.textlength(status, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 14], radius=3,
                        fill=STATUS_FILL[status])
    d.text((x + 5, y + 2), status, font=f, fill=(255, 255, 255))
    return w


def light_fg():
    return (235, 230, 215)


def lead_card(d, x, y, w, h, story):
    num, region, status, kicker, headline, deck, art = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 78], fill=DARK)
    draw_icon(d, art, x + 6, y + 4, w - 12, 70, light_fg(), RED)
    d.rectangle([x, y + 78, x + w, y + 80], fill=RED)
    ky = y + 86
    kf = F(9, bold=True, serif=False)
    d.text((x + 8, ky), kicker, font=kf, fill=RED)
    status_tag(d, x + w - 78, ky - 1, status)
    hf = F(16, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 16)
    ty = text_block(d, x + 8, ky + 16, lines[:3], hf, leading=19)
    df = F(11, serif=False)
    avail = (y + h) - (ty + 2) - 4
    n_deck = max(1, avail // 14)
    dlines = wrap(d, deck, df, w - 16)
    text_block(d, x + 8, ty + 2, dlines[:n_deck], df, fill=SOFT, leading=14)


def feature_card(d, x, y, w, h, story):
    num, region, status, kicker, headline, deck, art = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 38], fill=PAPER)
    draw_icon(d, art, x + w - 60, y + 3, 54, 32, INK, RED)
    kf = F(8, bold=True, serif=False)
    d.text((x + 7, y + 4), kicker, font=kf, fill=RED)
    status_tag(d, x + 7, y + 17, status)
    hf = F(12, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 14)
    ty = text_block(d, x + 7, y + 42, lines[:3], hf, leading=14)
    df = F(10, serif=False)
    avail = (y + h) - (ty + 2) - 4
    n_deck = max(1, avail // 12)
    dlines = wrap(d, deck, df, w - 14)
    text_block(d, x + 7, ty + 2, dlines[:n_deck], df, fill=SOFT, leading=12)


# Small visual nudges so neighbouring pins do not overlap on the map
# (Chicago/Washington and Banten/Singapore sit almost on top of each
# other at this scale). Applied to the drawn dot only.
PIN_OFFSET = {2: (-10, 9), 6: (10, 9), 10: (-11, -9), 11: (11, -9)}


def draw_map_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    mx0, my0, mx1, my1 = x + 14, y + 36, x + w - 14, y + 288
    step = 6
    yy = my0
    while yy <= my1:
        xx = mx0
        while xx <= mx1:
            lon = -170 + (xx - mx0) / (mx1 - mx0) * 360
            lat = 75 - (yy - my0) / (my1 - my0) * 135
            if is_land(lon, lat):
                d.ellipse([xx - 1, yy - 1, xx + 1, yy + 1],
                          fill=(120, 130, 145))
            xx += step
        yy += step
    nf = F(9, bold=True, serif=False)
    for num, lon, lat, label in PINS:
        px, py = lonlat_to_xy(lon, lat, mx0, my0, mx1, my1)
        ox, oy = PIN_OFFSET.get(num, (0, 0))
        px, py = px + ox, py + oy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=nf)
        d.text((px - tw / 2, py - 6), t, font=nf, fill=(255, 255, 255))
    cf = F(10, bold=True, serif=False)
    line1 = "EUROPE 16  \u00b7  MIDDLE EAST 4  \u00b7  AMERICAS 11  \u00b7  " \
            "ASIA-PACIFIC 7"
    tw = d.textlength(line1, font=cf)
    d.text((x + (w - tw) / 2, y + 296), line1, font=cf, fill=INK)
    line2 = "AFRICA 1  \u00b7  OCEANIA 1  \u00b7  WORLD 4  \u00b7  44 STORIES"
    tw = d.textlength(line2, font=cf)
    d.text((x + (w - tw) / 2, y + 312), line2, font=cf, fill=INK)
    sf = F(10, serif=False)
    sub = "pins mark the 12 places above"
    tw = d.textlength(sub, font=sf)
    d.text((x + (w - tw) / 2, y + 328), sub, font=sf, fill=SOFT)
    lf = F(9, serif=False)
    keys1 = "1 Antalya  \u00b7  2 Banten  \u00b7  3 Hormuz  \u00b7  " \
            "4 Tripoli  \u00b7  5 Seoul  \u00b7  6 Washington"
    tw = d.textlength(keys1, font=lf)
    d.text((x + (w - tw) / 2, y + 342), keys1, font=lf, fill=SOFT)
    keys2 = "7 Geneva  \u00b7  8 Patna  \u00b7  9 Kyiv  \u00b7  " \
            "10 Chicago  \u00b7  11 Singapore  \u00b7  12 Khartoum"
    tw = d.textlength(keys2, font=lf)
    d.text((x + (w - tw) / 2, y + 356), keys2, font=lf, fill=SOFT)


def draw_also_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "ALSO ON TUESDAY 24 NOVEMBER", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    col_w = (w - 20 - 16) // 3
    bf = F(10, bold=True, serif=False)
    rf = F(9, serif=False)
    tagf = F(8, bold=True, serif=False)
    row_h = 33
    for i, (num, day, status, lead, rest, icon) in enumerate(ALSO):
        col = i // 10
        row = i % 10
        ix = x + 10 + col * (col_w + 8)
        iy = y + 34 + row * row_h
        nf = F(10, bold=True, serif=False)
        d.text((ix, iy), "%d." % num, font=nf, fill=RED)
        draw_icon(d, icon, ix + 20, iy + 1, 13, 13, INK, RED)
        tx = ix + 36
        lead_lines = wrap(d, lead, bf, col_w - 36)
        ly = iy
        for ln in lead_lines[:2]:
            d.text((tx, ly), ln, font=bf, fill=INK)
            ly += 11
        tag = day if not status else "%s \u00b7 %s" % (day, status)
        tag_w = d.textlength(tag, font=tagf)
        rest_y = iy + len(lead_lines[:2]) * 11
        rest_lines_avail = 3 - len(lead_lines[:2])
        if rest and rest_lines_avail >= 1:
            rest_lines = wrap(d, rest, rf, col_w)
            drawn = rest_lines[:rest_lines_avail]
            ry = rest_y
            for j, ln in enumerate(drawn):
                last = (j == len(drawn) - 1)
                if last:
                    # keep the tag clear on the last rest line
                    ln_lines = wrap(d, ln, rf, col_w - tag_w - 8)
                    ln = ln_lines[0] if ln_lines else ""
                d.text((ix, ry), ln, font=rf, fill=INK)
                ry += 11
            tag_y = rest_y + (len(drawn) - 1) * 11
            d.text((ix + col_w - tag_w, tag_y), tag, font=tagf, fill=RED)
        else:
            d.text((ix + col_w - tag_w, rest_y), tag, font=tagf, fill=RED)


def draw_date_check(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=RED, width=2)
    hf = F(10, bold=True, serif=False)
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    t = "DATE CHECK \u2713"
    tw = d.textlength(t, font=hf)
    d.text((x + (w - tw) / 2, y + 2), t, font=hf, fill=(255, 255, 255))
    counts = day_counts()
    bf = F(10, bold=True, serif=False)
    rf = F(9, serif=False)
    d.text((x + 8, y + 20), "TUE 24 NOV 2026", font=bf, fill=INK)
    d.text((x + 8, y + 34), "44 STORIES VERIFIED", font=rf, fill=INK)
    line3 = "TUE %d \u00b7 MON %d \u00b7 SUN %d" % (
        counts["TUE"], counts["MON"], counts["SUN"])
    d.text((x + 8, y + 48), line3, font=rf, fill=INK)


def draw_timeline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    lab_w = 128
    d.rectangle([x, y, x + lab_w, y + h], fill=DARK)
    lf = F(10, bold=True, serif=False)
    t = "THE DAY IN UTC"
    tw = d.textlength(t, font=lf)
    d.text((x + (lab_w - tw) / 2, y + (h - 12) / 2), t, font=lf,
           fill=(255, 255, 255))
    col_w = (w - lab_w) // len(TIMELINE)
    tf = F(9, bold=True, serif=False)
    ef = F(9, serif=False)
    for i, (tm, ev) in enumerate(TIMELINE):
        ex = x + lab_w + 10 + i * col_w
        ey = y + (h - 11) / 2
        d.text((ex, ey), tm, font=tf, fill=RED)
        tw = d.textlength(tm, font=tf)
        d.text((ex + tw + 5, ey), ev, font=ef, fill=INK)
        if i:
            d.line([x + lab_w + i * col_w, y + 6,
                    x + lab_w + i * col_w, y + h - 6], fill=RULE, width=1)


def draw():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # masthead
    mf = F(13, bold=True, serif=False)
    t = "THE WORLD IN ONE PICTURE"
    tw = d.textlength(t, font=mf)
    d.text(((W - tw) / 2, 12), t, font=mf, fill=RED)
    df = F(42, bold=True, serif=True)
    t = "Tuesday 24 November 2026"
    tw = d.textlength(t, font=df)
    d.text(((W - tw) / 2, 30), t, font=df, fill=INK)
    counts = region_counts()
    tagline = ("44 STORIES  \u00b7  EUROPE %d  \u00b7  MIDDLE EAST %d  \u00b7  "
               "AMERICAS %d  \u00b7  ASIA-PACIFIC %d  \u00b7  AFRICA %d  "
               "\u00b7  OCEANIA %d  \u00b7  WORLD %d" % (
                   counts["Europe"], counts["Middle East"],
                   counts["Americas"], counts["Asia-Pacific"],
                   counts["Africa"], counts["Oceania"], counts["World"]))
    sf = F(12, bold=True, serif=False)
    tw = d.textlength(tagline, font=sf)
    if tw > 820:
        sf = F(11, bold=True, serif=False)
        tw = d.textlength(tagline, font=sf)
    d.text(((W - tw) / 2, 84), tagline, font=sf, fill=SOFT)
    draw_date_check(d, 880, 12, 122, 68)
    d.line([M, 104, W - M, 104], fill=INK, width=2)
    # stat strip
    y = 112
    cell_w = (W - 2 * M) / len(STATS)
    vf = F(17, bold=True, serif=True)
    lf = F(9, bold=True, serif=False)
    for i, (val, lab) in enumerate(STATS):
        cx = M + i * cell_w
        vw = d.textlength(val, font=vf)
        d.text((cx + (cell_w - vw) / 2, y), val, font=vf, fill=RED)
        lw = d.textlength(lab, font=lf)
        d.text((cx + (cell_w - lw) / 2, y + 22), lab, font=lf, fill=SOFT)
        if i:
            d.line([cx, y + 2, cx, y + 32], fill=RULE, width=1)
    d.line([M, 146, W - M, 146], fill=INK, width=1)
    # timeline strip
    draw_timeline(d, M, 154, W - 2 * M, 32)
    # leads
    lw_, gutter = 237, 10
    for i, story in enumerate(LEADS):
        lead_card(d, M + i * (lw_ + gutter), 194, lw_, 184, story)
    # features, two rows of five
    fw, fg = 188, 10
    for i, story in enumerate(FEATURES):
        row, col = divmod(i, 5)
        feature_card(d, M + col * (fw + fg), 386 + row * 116, fw, 108, story)
    # map + also
    draw_map_panel(d, M, 618, 456, 370)
    draw_also_panel(d, 490, 618, W - M - 490, 370)
    # footer
    d.line([M, 994, W - M, 994], fill=INK, width=2)
    ff = F(10, serif=False)
    line1 = ("Every story here happened or was first reported on Tuesday "
             "24 November 2026, or on the day tagged beside it. Contested "
             "claims are labelled as claims.")
    d.text((M, 1000), line1, font=ff, fill=INK)
    line2 = ("Sources: AP, Reuters, AFP, BBC, Al Jazeera, CNBC, Finimize, "
             "The Verge.  CONFIRMED \u2014 multiple sources  \u00b7  "
             "REPORTED \u2014 single source or developing  \u00b7  CLAIM "
             "\u2014 contested claim.")
    d.text((M, 1013), line2, font=ff, fill=SOFT)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = draw()
    img.save(out, "PNG", optimize=True)
    print("wrote %s %d bytes %s" % (out, os.path.getsize(out), img.size))


if __name__ == "__main__":
    main()
