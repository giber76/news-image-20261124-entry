#!/usr/bin/env python3
"""news-image-20261124 v5 — 'THE WORLD IN ONE DAY', 46 stories.
Draws a 1024x1024 newspaper front page for Tuesday 24 November 2026.
Written fresh for v5: 3 illustrated features, 12 illustrated cards
(stories 4-15), a 31-item brief (stories 16-46), dotted world map with
numbered pins, 8-moment UTC timeline, numbers strip and DATE CHECK box.
Every story carries number, region, claim label and source.
Python 3 + Pillow only. Usage: python3 draw.py [out.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else "entry.png"

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

PAPER = (246, 241, 231)
INK = (20, 20, 20)
RED = (168, 30, 30)
TEAL = (14, 107, 98)
AMBER = (176, 84, 8)
NAVY = (18, 35, 61)
GOLD = (201, 162, 39)
GREY = (105, 105, 100)
LGREY = (210, 205, 192)
CARD = (255, 253, 247)
DARK = (24, 24, 26)

_fonts = {}
def F(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key not in _fonts:
        path = SERIF_B if serif else (SANS_B if bold else SANS)
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]

def tw(t, f):
    return f.getlength(t)

def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if tw(trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def fit(text, maxw, size, bold=False, serif=False, minimum=7):
    s = size
    while s > minimum and tw(text, F(s, bold, serif)) > maxw:
        s -= 1
    return F(s, bold, serif)

def centre(d, cx, y, text, font, fill=INK):
    d.text((cx - tw(text, font) / 2, y), text, font=font, fill=fill)

def pill(d, x, y, label, bg):
    f = F(8, True)
    w = tw(label, f) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6, fill=bg)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

LBL_BG = {"CONFIRMED": TEAL, "REPORTED": AMBER, "CLAIM": RED}
LBL_SHORT = {"CONFIRMED": "CONF", "REPORTED": "REP", "CLAIM": "CLM"}
REG_SHORT = {"N. AMERICA": "NA", "EUROPE": "EU", "ASIA": "AS",
             "AFRICA": "AF", "MIDDLE EAST": "ME", "LATIN AMERICA": "LA",
             "WORLD": "WO"}

# ---------------------------------------------------------------- data
# (n, headline, region, claim, source, detail, scene)
FEATURES = [
    (1, "NVIDIA SOARS 30% — BEST DAY IN OVER A YEAR", "N. AMERICA",
     "CONFIRMED", "REUTERS · AP",
     "HUANG RETURNS AS CEO 10 DAYS AFTER QUITTING, REPORTEDLY AFTER "
     "PRESSURE FROM TRUMP. NASDAQ +6.51%; ~$1 TRILLION GAINED.", "nvidia"),
    (2, "COP31 COLLAPSES IN ANTALYA — NO DEAL, NO PACT", "WORLD",
     "CONFIRMED", "REUTERS · AP",
     "90+ NATIONS REJECT THE DRAFT AFTER ~50 HOURS OVERTIME — IT NEVER "
     "SAYS THE WORDS 'FOSSIL FUELS'.", "cop"),
    (3, "THREE TANKERS HIT MINES IN THE STRAIT OF HORMUZ", "MIDDLE EAST",
     "REPORTED", "REUTERS · AP",
     "SHIPS CATCH FIRE; IRAN VOWS 'ALL AVAILABLE MEANS' AGAINST THE US "
     "BLOCKADE AND RULES OUT TALKS UNTIL 7 CONDITIONS ARE MET.", "hormuz"),
]

# (n, headline, region, claim, source, scene, band caption)
CARDS = [
    (4, "5.3 QUAKE SHAKES NEPAL AT DAWN; NO DEATHS", "ASIA", "CONFIRMED",
     "EMSC", "quake", "M5.3 · 07:02 LOCAL"),
    (5, "ISRAELI STRIKES KILL HAMAS SECURITY CHIEF", "MIDDLE EAST",
     "REPORTED", "REUTERS", "gaza", "7 DEAD IN GAZA"),
    (6, "ICJ RULES MYANMAR COMMITTED GENOCIDE", "ASIA", "CONFIRMED",
     "ICJ", "icj", "LANDMARK VERDICT"),
    (7, "NATO VOWS TO DEFEND SPACE FROM RUSSIA", "EUROPE", "REPORTED",
     "REUTERS", "space", "ORBIT THREAT?"),
    (8, "ZAPORIZHZHIA STRIKE KILLS 2, WOUNDS 40", "EUROPE", "REPORTED",
     "REUTERS", "zap", "4 CHILDREN WOUNDED"),
    (9, "BANTEN FACTORY FIRE TOLL RISES TO 26", "ASIA", "CONFIRMED",
     "REUTERS", "banten", "FIRE WAS SAT 21 NOV"),
    (10, "US LOSES MEASLES-FREE STATUS AFTER 25 YEARS", "N. AMERICA",
     "CONFIRMED", "REUTERS", "measles", "9TH DEATH IN PA"),
    (11, "SANOFI BUYS INSMED FOR $41 BILLION", "EUROPE", "CONFIRMED",
     "REUTERS", "sanofi", "BIGGEST IN ~3 YRS"),
    (12, "UKRAINE: DRONES SANK RUSSIAN CORVETTE OFF LIBYA", "AFRICA",
     "CLAIM", "REUTERS", "corvette", "KYIV'S ACCOUNT"),
    (13, "FIGHTING IN ITURI TRAPS EBOLA RESPONDERS", "AFRICA", "REPORTED",
     "WHO", "ebola", "WHO WARNS"),
    (14, "CAS RESTORES SENEGAL AS AFCON CHAMPIONS", "AFRICA", "CONFIRMED",
     "CAS", "afcon", "COURT OVERTURNS BAN"),
    (15, "SOUTH AFRICA BOWL BANGLADESH OUT FOR 91", "AFRICA", "CONFIRMED",
     "REUTERS", "cricket", "CENTURION TEST"),
]

# (n, short headline <=42 chars, region, claim, source)
BRIEF = [
    (16, "OREGON, VIRGINIA SUE SPACEX OVER GROK", "N. AMERICA", "REPORTED", "REUTERS"),
    (17, "US BLACKLISTS MEGASPEED OVER AI CHIPS", "ASIA", "CONFIRMED", "REUTERS"),
    (18, "ARM EXTENDS CHIEF HAAS'S TENURE TO 2033", "EUROPE", "CONFIRMED", "REUTERS"),
    (19, "GUTERRES URGES GLOBAL AI SAFETY RULES", "WORLD", "REPORTED", "UN"),
    (20, "TRUMP ORDERS DOJ TO SPEED DEATH SENTENCES", "N. AMERICA", "REPORTED", "REUTERS"),
    (21, "PENTAGON: CANADA FALLING SHORT ON DEFENCE", "N. AMERICA", "CLAIM", "PENTAGON"),
    (22, "SEVEN STATES BACK EU LIMITS ON RUSSIAN VISAS", "EUROPE", "REPORTED", "REUTERS"),
    (23, "IRAQ PM: OIL MINISTRY TO RUN KURD FIELDS", "MIDDLE EAST", "REPORTED", "REUTERS"),
    (24, "UN URGES PROBE INTO BENGHAZI PORT ATTACKS", "AFRICA", "REPORTED", "UN"),
    (25, "SEOUL OFFERS $375K REWARDS TO CATCH AI CHEATS", "ASIA", "CONFIRMED", "REUTERS"),
    (26, "MEXICO TO TRY 'EL CHAPO ISIDRO' DESPITE US BID", "LATIN AMERICA", "REPORTED", "REUTERS"),
    (27, "IRAN FLOGS SINGER PARASTOO AHMADI, 74 LASHES", "MIDDLE EAST", "REPORTED", "REUTERS"),
    (28, "SOMALIA, UGANDA STEP UP OPS VS AL-SHABAAB", "AFRICA", "REPORTED", "REUTERS"),
    (29, "UN: 47,000 WOMEN KILLED BY PARTNERS IN 2025", "WORLD", "CONFIRMED", "UN"),
    (30, "FDA APPROVES FIRST LIMB-GIRDLE DRUG", "N. AMERICA", "CONFIRMED", "FDA"),
    (31, "MOST DISTANT QUASAR FOUND AFTER BIG BANG", "WORLD", "CONFIRMED", "REUTERS"),
    (32, "RUSSIAN JETS ENTER S. KOREA AIR-DEFENCE ZONE", "ASIA", "REPORTED", "REUTERS"),
    (33, "NORWAY IN DIALOGUE WITH UKRAINE ON STABILITY", "EUROPE", "REPORTED", "REUTERS"),
    (34, "VANCE, RUBIO MEET QATARI PM AT WHITE HOUSE", "N. AMERICA", "REPORTED", "REUTERS"),
    (35, "BRENTFORD 4-0 EVERTON; MONZA 3-0 FIORENTINA", "EUROPE", "CONFIRMED", "REUTERS"),
    (36, "BRAZIL LOSE 3-2 TO JAPAN; ANCELOTTI UNDER FIRE", "LATIN AMERICA", "REPORTED", "REUTERS"),
    (37, "INDIA SEAL ODI SERIES 3-1 AGAINST NEW ZEALAND", "ASIA", "CONFIRMED", "REUTERS"),
    (38, "SPAIN CAMPAIGN HEATS UP AHEAD OF 29 NOV VOTE", "EUROPE", "REPORTED", "REUTERS"),
    (39, "ZVEREV WINS ATP FINALS OPENER IN TURIN", "EUROPE", "CONFIRMED", "REUTERS"),
    (40, "CANARY ISLANDS LOG RECORD MIGRANT ARRIVALS", "EUROPE", "REPORTED", "REUTERS"),
    (41, "POPE LEO XIV VISITS PERU ON POVERTY, SLAVERY", "LATIN AMERICA", "REPORTED", "REUTERS"),
    (42, "PHILIPPINES WIN FIRST EUROVISION ASIA", "ASIA", "CONFIRMED", "REUTERS"),
    (43, "ASEAN SUMMIT OPENS IN MANILA", "ASIA", "CONFIRMED", "REUTERS"),
    (44, "GREMIO BEAT SANTOS 2-0 IN THE BRASILEIRAO", "LATIN AMERICA", "CONFIRMED", "REUTERS"),
    (45, "PERSIJA JAKARTA THRASH SUMSEL UNITED 7-0", "ASIA", "CONFIRMED", "REUTERS"),
    (46, "PYRAMIDS STUN AL AHLY 2-0 IN EGYPT", "AFRICA", "CONFIRMED", "REUTERS"),
]

NUMBERS = [
    ("30%", "NVIDIA SOARS; NASDAQ +6.51%"),
    ("50H", "HOURS OF COP31 OVERTIME"),
    ("3", "TANKERS HIT MINES IN HORMUZ"),
    ("5.3", "NEPAL QUAKE AT DAWN"),
    ("26", "BANTEN FIRE TOLL RISES TO"),
    ("$41B", "SANOFI BUYS INSMED"),
]

REGIONS = [("ASIA", 10, (14, 107, 98)), ("EUROPE", 10, (37, 99, 235)),
           ("N. AMERICA", 7, (168, 30, 30)), ("AFRICA", 7, (201, 162, 39)),
           ("MIDDLE EAST", 4, (120, 60, 140)), ("LATIN AMERICA", 4, (34, 139, 34)),
           ("WORLD", 4, (90, 90, 90))]

# (day-part, short label) — Nepal time is the one precise clock time known
TIMELINE = [
    ("DAWN · 07:02", "NEPAL QUAKE"),
    ("MORNING", "NVIDIA +30%"),
    ("MORNING", "COP31: 50H+"),
    ("MIDDAY", "ICJ VERDICT"),
    ("AFTERNOON", "HORMUZ HIT"),
    ("AFTERNOON", "GAZA STRIKES"),
    ("EVENING", "BANTEN: 26"),
    ("EVENING", "SANOFI $41B"),
]

# ---------------------------------------------------------------- scenes
def flame(d, cx, cy, s, col=(255, 140, 0)):
    # simple flame: triangle-ish polygon + inner flame
    d.polygon([(cx, cy - s), (cx + s * 0.55, cy + s * 0.3), (cx + s * 0.25, cy + s * 0.55),
               (cx - s * 0.25, cy + s * 0.55), (cx - s * 0.55, cy + s * 0.3)], fill=col)
    d.polygon([(cx, cy - s * 0.45), (cx + s * 0.28, cy + s * 0.25), (cx - s * 0.28, cy + s * 0.25)],
              fill=(255, 210, 60))

def scene_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    base = y + h - 8
    bars = [7, 11, 9, 16, 14, 22, 20, 29, 33, 40]
    bw = (w - 16) // len(bars)
    for i, bh in enumerate(bars):
        bx = x + 8 + i * bw
        d.rectangle([bx, base - bh, bx + bw - 4, base], fill=(38, 90, 150))
    pts = [(x + 8 + i * bw + (bw - 4) / 2, base - bh - 3) for i, bh in enumerate(bars)]
    d.line(pts, fill=(60, 200, 120), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] + 11, pts[-1][1] - 8),
               (pts[-1][0] + 1, pts[-1][1] + 3)], fill=(60, 200, 120))
    d.text((x + 12, y + 5), "+30%", font=F(28, True), fill=(60, 220, 130))
    d.text((x + 12, y + 34), "NASDAQ  +6.51%", font=F(12, True), fill=(255, 255, 255))

def scene_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 42, 66))
    cx, cy, r = x + w // 2 - 40, y + h // 2 + 2, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 180, 220),
              outline=(220, 235, 245), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(90, 140, 190), width=1)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=(90, 140, 190), width=1)
    d.line([cx - r, cy, cx + r, cy], fill=(90, 140, 190), width=1)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 180, fill=(90, 140, 190), width=1)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 180, 360, fill=(90, 140, 190), width=1)
    # land blobs
    d.ellipse([cx - 30, cy - 26, cx - 2, cy - 4], fill=(90, 170, 110))
    d.ellipse([cx + 4, cy + 6, cx + 30, cy + 26], fill=(90, 170, 110))
    # NO DEAL stamp, rotated, kept fully inside the scene
    stamp = Image.new("RGBA", (150, 44), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([3, 3, 146, 40], outline=(230, 60, 50), width=3)
    sd.text((75, 9), "NO DEAL", font=F(20, True), fill=(230, 60, 50), anchor="ma")
    stamp = stamp.rotate(-10, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (x + w - 162, y + h - 50), stamp)

def scene_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 90, 110))
    d.ellipse([x + w - 52, y + 8, x + w - 16, y + 44], fill=(255, 200, 80))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(10, 60, 80))
    for i, tx in enumerate([x + 22, x + w // 2 - 40, x + w - 130]):
        d.rectangle([tx, y + h - 62, tx + 92, y + h - 38], fill=(18, 18, 18))
        d.rectangle([tx + 60, y + h - 76, tx + 78, y + h - 62], fill=(18, 18, 18))
        flame(d, tx + 30 + i * 6, y + h - 66, 13)
        flame(d, tx + 62, y + h - 70, 9, col=(255, 90, 0))
    d.text((x + 12, y + h - 30), "STRAIT OF HORMUZ", font=F(12, True), fill=(255, 255, 255))

FEATURE_SCENES = {"nvidia": scene_nvidia, "cop": scene_cop, "hormuz": scene_hormuz}

def band_scene(d, x, y, w, h, kind):
    """Small 245x26 drawn scene strip at the top of a card."""
    if kind == "quake":
        d.rectangle([x, y, x + w, y + h], fill=(20, 30, 44))
        pts = [(x + 8, y + 16), (x + 30, y + 16), (x + 40, y + 5), (x + 52, y + 22),
               (x + 64, y + 8), (x + 76, y + 18), (x + 96, y + 16), (x + 120, y + 16)]
        d.line(pts, fill=(255, 210, 60), width=2)
        d.polygon([(x + 118, y + h), (x + 128, y + 6), (x + 138, y + h)], fill=(60, 80, 110))
    elif kind == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(40, 38, 36))
        for bx in (x + 12, x + 52, x + 92):
            d.rectangle([bx, y + 8, bx + 30, y + h], fill=(70, 68, 64))
            for wy in (y + 12, y + 18):
                d.rectangle([bx + 5, wy, bx + 12, wy + 3], fill=(255, 220, 120))
                d.rectangle([bx + 18, wy, bx + 25, wy + 3], fill=(255, 220, 120))
        flame(d, x + 122, y + 14, 9)
        flame(d, x + 136, y + 16, 6, col=(255, 90, 0))
    elif kind == "icj":
        d.rectangle([x, y, x + w, y + h], fill=(24, 40, 70))
        cx = x + 60
        d.line([cx, y + 4, cx, y + h - 3], fill=GOLD, width=2)
        d.line([cx - 26, y + 7, cx + 26, y + 7], fill=GOLD, width=2)
        d.polygon([(cx - 34, y + 9), (cx - 18, y + 9), (cx - 26, y + 20)], fill=GOLD)
        d.polygon([(cx + 18, y + 9), (cx + 34, y + 9), (cx + 26, y + 20)], fill=GOLD)
        d.ellipse([cx - 3, y + 2, cx + 3, y + 8], fill=GOLD)
    elif kind == "space":
        d.rectangle([x, y, x + w, y + h], fill=(10, 20, 46))
        for sx, sy in ((x + 14, y + 6), (x + 40, y + 18), (x + 210, y + 6), (x + 228, y + 18)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        cx = x + 95
        d.rectangle([cx - 26, y + 9, cx - 8, y + 17], fill=(120, 160, 200))
        d.rectangle([cx + 8, y + 9, cx + 26, y + 17], fill=(120, 160, 200))
        d.rectangle([cx - 8, y + 7, cx + 8, y + 19], fill=(200, 210, 220))
        d.ellipse([cx - 2, y + 10, cx + 2, y + 14], fill=RED)
        d.line([cx + 8, y + 13, cx + 26, y + 4], fill=(200, 210, 220), width=1)
    elif kind == "zap":
        d.rectangle([x, y, x + w, y + h], fill=(30, 32, 40))
        d.rectangle([x + 16, y + 6, x + 76, y + h], fill=(85, 82, 76))
        for wy in (y + 10, y + 17):
            for wx in (x + 22, x + 38, x + 54):
                d.rectangle([wx, wy, wx + 10, wy + 4], fill=(255, 220, 120))
        flame(d, x + 118, y + 13, 11)
    elif kind == "banten":
        d.rectangle([x, y, x + w, y + h], fill=(44, 30, 26))
        d.rectangle([x + 14, y + 12, x + 74, y + h], fill=(80, 70, 62))
        d.rectangle([x + 78, y + 4, x + 88, y + h], fill=(80, 70, 62))
        flame(d, x + 44, y + 12, 10)
        flame(d, x + 112, y + 14, 8, col=(255, 90, 0))
        flame(d, x + 130, y + 16, 6)
    elif kind == "measles":
        d.rectangle([x, y, x + w, y + h], fill=(250, 244, 230))
        for vx, vy, vr in ((x + 30, y + 13, 6), (x + 60, y + 9, 4), (x + 85, y + 16, 5)):
            d.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=RED)
            d.ellipse([vx - 1, vy - 1, vx + 1, vy + 1], fill=(255, 255, 255))
        d.rectangle([x + 124, y + 8, x + 130, y + 20], fill=RED)
        d.rectangle([x + 118, y + 11, x + 136, y + 17], fill=RED)
    elif kind == "sanofi":
        d.rectangle([x, y, x + w, y + h], fill=(232, 240, 248))
        d.rounded_rectangle([x + 18, y + 8, x + 62, y + 18], radius=5, fill=(200, 60, 60))
        d.rounded_rectangle([x + 62, y + 8, x + 106, y + 18], radius=5, fill=(255, 255, 255),
                            outline=(200, 60, 60))
    elif kind == "corvette":
        d.rectangle([x, y, x + w, y + h], fill=(14, 70, 96))
        d.rectangle([x, y + h - 10, x + w, y + h], fill=(10, 48, 70))
        d.polygon([(x + 30, y + 12), (x + 110, y + 6), (x + 100, y + 18), (x + 40, y + 20)],
                  fill=(24, 24, 24))
        d.rectangle([x + 62, y + 2, x + 72, y + 8], fill=(24, 24, 24))
        d.ellipse([x + 128, y + 6, x + 132, y + 10], fill=(255, 255, 255))
        d.line([x + 130, y + 10, x + 112, y + 12], fill=(255, 255, 255), width=1)
    elif kind == "ebola":
        d.rectangle([x, y, x + w, y + h], fill=(232, 244, 232))
        d.rectangle([x + 24, y + 7, x + 32, y + 19], fill=(20, 120, 60))
        d.rectangle([x + 18, y + 10, x + 38, y + 16], fill=(20, 120, 60))
        d.ellipse([x + 70, y + 6, x + 96, y + 20], outline=(20, 120, 60), width=2)
        d.line([x + 76, y + 13, x + 90, y + 13], fill=(20, 120, 60), width=2)
        d.line([x + 83, y + 7, x + 83, y + 19], fill=(20, 120, 60), width=2)
    elif kind == "afcon":
        d.rectangle([x, y, x + w, y + h], fill=(20, 90, 50))
        cx = x + 60
        d.polygon([(cx - 14, y + 4), (cx + 14, y + 4), (cx + 10, y + 16), (cx - 10, y + 16)],
                  fill=GOLD)
        d.arc([cx - 20, y + 4, cx - 8, y + 14], 90, 270, fill=GOLD, width=2)
        d.arc([cx + 8, y + 4, cx + 20, y + 14], 270, 90, fill=GOLD, width=2)
        d.rectangle([cx - 3, y + 16, cx + 3, y + 21], fill=GOLD)
        d.rectangle([cx - 10, y + 21, cx + 10, y + 23], fill=GOLD)
        d.rectangle([x + 100, y + 8, x + 132, y + 12], fill=(255, 210, 0))
        d.rectangle([x + 100, y + 12, x + 132, y + 16], fill=(0, 140, 60))
        d.rectangle([x + 100, y + 16, x + 132, y + 20], fill=(220, 40, 40))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(30, 110, 60))
        for sx in (x + 40, x + 48, x + 56):
            d.rectangle([sx, y + 6, sx + 3, y + 20], fill=(240, 220, 140))
        d.ellipse([x + 96, y + 8, x + 106, y + 18], fill=(200, 40, 40))
        d.line([x + 118, y + 20, x + 136, y + 5], fill=(210, 170, 110), width=4)

# ---------------------------------------------------------------- map
# Land cells as (row, col_start, col_end); grid 48 cols x 20 rows.
LAND = [
    (0, 12, 15), (0, 28, 46),
    (1, 2, 13), (1, 22, 27), (1, 28, 46),
    (2, 2, 14), (2, 13, 16), (2, 22, 27), (2, 28, 45),
    (3, 3, 13), (3, 23, 27), (3, 28, 44),
    (4, 4, 12), (4, 23, 26), (4, 29, 44), (4, 44, 45),
    (5, 5, 11), (5, 24, 26), (5, 29, 42),
    (6, 5, 10), (6, 29, 41), (6, 31, 33),
    (7, 6, 9), (7, 24, 30), (7, 32, 40),
    (8, 7, 9), (8, 24, 30), (8, 35, 38), (8, 36, 42),
    (9, 9, 13), (9, 24, 29),
    (10, 9, 14), (10, 24, 29),
    (11, 10, 14), (11, 24, 28),
    (12, 10, 13), (12, 25, 28), (12, 39, 44),
    (13, 11, 12), (13, 25, 27), (13, 39, 43),
    (14, 11, 12), (14, 40, 42),
    (15, 11, 12),
    (16, 11, 12),
]

# (n, lon, lat, dx, dy) pins for stories 1-15 (offsets spread collisions)
PINS = [
    (1, -100, 39, -6, -8), (2, 30.7, 36.9, -22, 2), (3, 56.5, 26.5, -8, 4),
    (4, 85, 27.5, -10, -8), (5, 34.5, 31.5, 8, -6), (6, 96, 20, 10, 8),
    (7, 4.4, 50.8, -16, -8), (8, 35.2, 47.8, 6, -10), (9, 106, -6.2, 0, 0),
    (10, -77.5, 40.5, 8, 8), (11, 2.3, 48.9, 16, 2), (12, 15, 33, -18, 10),
    (13, 29.5, 1.8, 0, 0), (14, -16, 14.7, 0, 0), (15, 28.2, -25.9, 0, 0),
]

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 216), outline=INK, width=1)
    cell_w, cell_h = w / 48.0, h / 20.0
    for (r, c0, c1) in LAND:
        for c in range(c0, c1 + 1):
            cx = x + c * cell_w + cell_w / 2
            cy = y + r * cell_h + cell_h / 2
            d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=(150, 138, 110))
    for (n, lon, lat, dx, dy) in PINS:
        px = x + (lon + 180) / 360.0 * w + dx
        py = y + (84 - lat) / 144.0 * h + dy
        d.ellipse([px - 6.5, py - 6.5, px + 6.5, py + 6.5], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = F(7, True)
        t = str(n)
        d.text((px - tw(t, f) / 2, py - 4.5), t, font=f, fill=(255, 255, 255))
    d.text((x + 6, y + h - 13), "PINS 1–15 = FEATURES & CARDS",
           font=F(8, True), fill=GREY)

# ---------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- masthead
centre(d, W // 2, 4, "46 STORIES  ·  7 REGIONS  ·  15 DRAWN SCENES  ·  CLAIMS LABELLED",
       F(10, True), fill=GREY)
d.text((W // 2 - tw("THE WORLD IN ONE DAY", F(41, True, True)) / 2, 16),
       "THE WORLD IN ONE DAY", font=F(41, True, True), fill=INK)
centre(d, W // 2, 60, "T U E S D A Y   2 4   N O V E M B E R   2 0 2 6",
       F(15, True), fill=RED)
centre(d, W // 2, 78,
       "NVIDIA SOARS 30%  —  COP31 COLLAPSES  —  TANKERS HIT IN HORMUZ  —  ICJ: MYANMAR GENOCIDE",
       F(10, True), fill=INK)
d.line([14, 94, W - 14, 94], fill=INK, width=2)

# ---- numbers strip
d.text((14, 100), "THE DAY IN NUMBERS", font=F(10, True), fill=RED)
ny = 112
cellw = 996 / 6
for i, (num, cap) in enumerate(NUMBERS):
    cx = 14 + i * cellw
    if i:
        d.line([cx, ny, cx, ny + 40], fill=LGREY, width=1)
    fnum = fit(num, cellw - 12, 30, bold=True)
    centre(d, cx + cellw / 2, ny, num, fnum, fill=INK)
    centre(d, cx + cellw / 2, ny + 30, cap, F(8, True), fill=GREY)
d.line([14, 156, W - 14, 156], fill=INK, width=1)

# ---- region bar
rx, ry = 14, 162
total = sum(c for _, c, _ in REGIONS)
for name, count, col in REGIONS:
    segw = 996 * count / total
    d.rectangle([rx, ry, rx + segw, ry + 9], fill=col)
    rx += segw
rtext = "   ·   ".join(f"{name} {count}" for name, count, _ in REGIONS)
centre(d, W // 2, 174, rtext, F(9, True), fill=INK)

# ---- timeline
d.text((14, 192), "THE DAY IN UTC — 8 MOMENTS", font=F(10, True), fill=RED)
ty = 214
d.line([30, ty, W - 30, ty], fill=INK, width=2)
step = (W - 60) / len(TIMELINE)
for i, (when, what) in enumerate(TIMELINE):
    cx = 30 + step * i + step / 2
    d.ellipse([cx - 5, ty - 5, cx + 5, ty + 5], fill=RED, outline=(255, 255, 255), width=1)
    centre(d, cx, ty + 9, when, F(8, True), fill=GREY)
    for j, ln in enumerate(wrap(what, F(9, True), step - 8)):
        centre(d, cx, ty + 20 + j * 11, ln, F(9, True), fill=INK)

# ---- features
fy, fh, fscene_h = 252, 150, 78
fw, fgap = 326, 9
for i, (n, head, reg, lbl, src, detail, kind) in enumerate(FEATURES):
    fx = 14 + i * (fw + fgap)
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=CARD, outline=INK, width=1)
    FEATURE_SCENES[kind](d, fx + 1, fy + 1, fw - 2, fscene_h)
    my = fy + fscene_h + 4
    d.text((fx + 7, my), f"{n} · {reg}", font=F(9, True), fill=INK)
    pill(d, fx + 7 + tw(f"{n} · {reg}  ", F(9, True)), my - 1, lbl, LBL_BG[lbl])
    d.text((fx + fw - 7 - tw(src, F(8)), my + 1), src, font=F(8), fill=GREY)
    hy = my + 16
    lines = wrap(head, F(12, True), fw - 14)
    for j, ln in enumerate(lines[:2]):
        d.text((fx + 7, hy + j * 14), ln, font=F(12, True), fill=INK)
    dy = hy + len(lines[:2]) * 14 + 2
    for j, ln in enumerate(wrap(detail, F(8), fw - 14)[:2]):
        d.text((fx + 7, dy + j * 10), ln, font=F(8), fill=(60, 60, 60))

# ---- cards (stories 4-15), 4 cols x 3 rows
cy0, ch, cgap = 406, 78, 6
cw = 245
cx0 = (W - (4 * cw + 3 * cgap)) // 2
for idx, (n, head, reg, lbl, src, kind, cap) in enumerate(CARDS):
    row, col = divmod(idx, 4)
    x = cx0 + col * (cw + cgap)
    y = cy0 + row * (ch + 4)
    d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=INK, width=1)
    band_scene(d, x + 1, y + 1, cw - 2, 24, kind)
    capf = F(7, True)
    capw = tw(cap, capf) + 10
    d.rounded_rectangle([x + cw - 7 - capw, y + 5, x + cw - 7, y + 19],
                        radius=6, fill=(20, 20, 20))
    d.text((x + cw - 7 - capw + 5, y + 8), cap, font=capf, fill=(255, 255, 255))
    hy = y + 28
    for j, ln in enumerate(wrap(head, F(11, True), cw - 12)[:2]):
        d.text((x + 6, hy + j * 13), ln, font=F(11, True), fill=INK)
    my = y + ch - 15
    d.text((x + 6, my), f"{n} · {reg}", font=F(8, True), fill=INK)
    pill(d, x + 6 + tw(f"{n} · {reg}  ", F(8, True)), my - 1, lbl, LBL_BG[lbl])
    d.text((x + cw - 6 - tw(src, F(8)), my + 1), src, font=F(8), fill=GREY)

# ---- map + brief
by = 656
d.text((14, by), "WHERE IT HAPPENED", font=F(10, True), fill=RED)
d.text((276, by), "ALSO — IN BRIEF · STORIES 16–46", font=F(10, True), fill=RED)
draw_map(d, 14, by + 16, 252, 218)
bx0, bw = 276, 362
bcol_gap = 10
for i, (n, head, reg, lbl, src) in enumerate(BRIEF):
    col, row = divmod(i, 16)
    x = bx0 + col * (bw + bcol_gap)
    y = by + 16 + row * 14
    tag = f" · {REG_SHORT[reg]} · {LBL_SHORT[lbl]} · {src}"
    f = fit(f"{n}. {head}{tag}", bw, 9, bold=False)
    d.text((x, y), f"{n}.", font=F(9, True), fill=RED)
    d.text((x + tw(f"{n}. ", F(9, True)), y), head, font=f, fill=INK)
    hx = x + tw(f"{n}. {head} ", f)
    d.text((hx, y), tag, font=F(8), fill=GREY)

# ---- date check
dy0 = 894
d.rectangle([14, dy0, W - 14, dy0 + 56], outline=RED, width=2)
d.text((22, dy0 + 4), "DATE CHECK", font=F(11, True), fill=RED)
d.text((22, dy0 + 17),
       "WIRES READ TO 22:00 UTC. EVERY STORY HERE WAS REPORTED ON TUESDAY 24 NOVEMBER 2026.",
       font=F(9), fill=INK)
d.text((22, dy0 + 30),
       "BANTEN'S FIRE WAS SAT 21 NOV — SHOWN ONLY FOR ITS 24 NOV TOLL UPDATE. SPAIN VOTES 29 NOV — NOT YET HELD.",
       font=F(9), fill=INK)
d.text((22, dy0 + 43),
       "ALL 46 STORIES INCLUDED — THE 11 CUT FOR SPACE IN V4 ARE BACK.",
       font=F(9, True), fill=INK)

# ---- footer
d.text((14, 956),
       "CONFIRMED = NAMED-SOURCE VERIFIED  ·  REPORTED = WIRE-REPORTED, NOT YET CONFIRMED  ·  "
       "CLAIM = ONE SIDE'S ACCOUNT",
       font=F(9), fill=INK)
d.text((14, 968),
       "SOURCES: REUTERS · AP · EMSC · ICJ · FDA · UN · WHO · CAS · PENTAGON",
       font=F(9), fill=INK)
d.text((14, 980),
       "SCENES ARE DRAWN ILLUSTRATIONS OF REPORTED EVENTS, NOT PHOTOGRAPHS · "
       "STORIES NUMBERED 1–46 · MAP PINS 1–15 · TUESDAY 24 NOVEMBER 2026",
       font=F(9), fill=GREY)

img.save(OUT)
print("saved", OUT, img.size)
