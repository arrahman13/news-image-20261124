#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261124.

Renders a 1024x1024 newspaper front page summarising Tuesday 24 Nov 2026:
3 leads with AI photos, 13 cards, 19 briefs, a realistic world map built from
real GeoJSON country outlines with numbered pins 1-35, a legend and a
DATE CHECK box. Deterministic: same inputs -> byte-identical output.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976

PAPER = (250, 248, 242)
INK = (18, 18, 18)
MUTED = (90, 88, 82)
RULE = (40, 40, 40)
LIGHT_RULE = (180, 176, 166)
OCEAN = (205, 226, 236)
LAND = (216, 204, 178)
COAST = (125, 116, 98)
TAG_COLORS = {"REPORTED": (30, 107, 52), "CLAIM": (180, 83, 9), "FORECAST": (29, 78, 216)}

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tag(draw, x, y, tag):
    """Draw a small filled tag chip; returns its width."""
    f = font(SANS_B, 8)
    tw = draw.textlength(tag, font=f)
    w, h = int(tw) + 10, 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=TAG_COLORS[tag])
    draw.text((x + 5, y + 2), tag, font=f, fill=(255, 255, 255))
    return w


def draw_badge(draw, cx, cy, n, d=15):
    draw.ellipse([cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2],
                 fill=(18, 18, 18), outline=(255, 255, 255), width=1)
    f = font(SANS_B, 9 if n < 10 else 8)
    tw = draw.textlength(str(n), font=f)
    draw.text((cx - tw / 2, cy - 5 if n < 10 else cy - 4.5), str(n),
              font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- stories
LEADS = [
    {"n": 1, "region": "World",
     "headline": "HUANG'S COMEBACK TURNS TO QUESTIONS",
     "summary": "Nvidia reinstates Jensen Huang after Trump's intervention \u2014 then shares slide 7% as US politicians question the president's role and the attorney general dodges questions.",
     "tag": "REPORTED", "photo": "assets/lead1.png", "lon": -122.0, "lat": 37.4},
    {"n": 2, "region": "Europe",
     "headline": "WAR SPREADS TO LIBYA'S SHORES",
     "summary": "Libya demands answers from Kyiv after Ukraine's drone strike sank a Russian warship off Benghazi; Kyiv releases video of the attack.",
     "tag": "REPORTED", "photo": "assets/lead2.png", "lon": 20.1, "lat": 32.1},
    {"n": 3, "region": "Middle East",
     "headline": "IRAN BRINKMANSHIP",
     "summary": "Trump warns Tehran of a \u2018very traumatic\u2019 outcome if no nuclear deal and weighs a second carrier; Netanyahu urges new strikes; Vance and Rubio meet Qatar's PM.",
     "tag": "REPORTED", "photo": "assets/lead3.png", "lon": 56.3, "lat": 26.6},
]

CARDS = [
    {"n": 4, "region": "Europe", "headline": "NUCLEAR SATELLITE ALARM",
     "summary": "Western intel warns Russia may launch a nuclear-armed satellite as early as December; NATO vows to defend in space.",
     "tag": "CLAIM", "lon": 37.6, "lat": 55.75},
    {"n": 5, "region": "Europe", "headline": "RUSSIA'S WAR DEAD NEAR 500,000",
     "summary": "Moscow's own figures show almost half a million dead in the Ukraine war, leaked data reveals.",
     "tag": "REPORTED", "lon": 30.52, "lat": 50.45},
    {"n": 6, "region": "Europe", "headline": "LUKASHENKO'S PEACE FLIGHT",
     "summary": "Belarus leader offers to fly with Zelenskiy to Moscow for talks; says Russia is winning.",
     "tag": "REPORTED", "lon": 27.56, "lat": 53.9},
    {"n": 7, "region": "Europe", "headline": "ZAPORIZHZHIA HIT OVERNIGHT",
     "summary": "Russian attack kills 2 and wounds 40, including four children, in Zaporizhzhia.",
     "tag": "REPORTED", "lon": 35.12, "lat": 47.85},
    {"n": 8, "region": "Middle East", "headline": "HAMAS SECURITY CHIEF KILLED",
     "summary": "Israeli airstrike kills Hamas internal security director Naeem Abu Nahel and six others in Gaza.",
     "tag": "REPORTED", "lon": 34.47, "lat": 31.5},
    {"n": 9, "region": "Middle East", "headline": "HOUTHIS CLOSE ON ADEN",
     "summary": "Houthi fighters push within 60 km of Aden; Yemeni army vows the city will hold as Saudi jets strike back.",
     "tag": "REPORTED", "lon": 45.03, "lat": 12.8},
    {"n": 10, "region": "Asia-Pacific", "headline": "CHINA PROBES TOP LEADER",
     "summary": "Shanghai party chief Chen Jining, a Politburo member, is under investigation \u2014 the fourth since 2025.",
     "tag": "REPORTED", "lon": 121.47, "lat": 31.23},
    {"n": 11, "region": "Asia-Pacific", "headline": "HUAWEI GUILTY OF THEFT",
     "summary": "New York jury convicts Huawei of stealing trade secrets; acquits it of racketeering.",
     "tag": "REPORTED", "lon": -74.0, "lat": 40.71},
    {"n": 12, "region": "Europe", "headline": "SANOFI'S $41BN BET",
     "summary": "French drugmaker Sanofi agrees an all-cash $41bn takeover of US biotech Insmed.",
     "tag": "REPORTED", "lon": 2.35, "lat": 48.86},
    {"n": 13, "region": "Asia-Pacific", "headline": "14 NATIONS BACK ROHINGYA RULING",
     "summary": "Fourteen countries recognise the ICJ's genocide ruling on Myanmar; UK sanctions top generals.",
     "tag": "REPORTED", "lon": 96.15, "lat": 16.8},
    {"n": 14, "region": "Africa", "headline": "SENEGAL AFCON CHAMPIONS AGAIN",
     "summary": "CAS reinstates Senegal as 2025 Africa Cup winners, ten months after the final.",
     "tag": "REPORTED", "lon": -17.45, "lat": 14.69},
    {"n": 15, "region": "Americas", "headline": "COMMANDERS STUN BENGALS",
     "summary": "Washington wins 22\u201320 on a last-play field goal in Monday Night Football.",
     "tag": "REPORTED", "lon": -77.04, "lat": 38.9},
    {"n": 16, "region": "Asia-Pacific", "headline": "SOLOMONS CUT CHINA PACT",
     "summary": "Solomon Islands will end its security pact with China.",
     "tag": "REPORTED", "lon": 160.06, "lat": -9.65},
]

BRIEFS = [
    (17, "World", "Guterres: UN needs a multilateral AI-risk framework within a year.", "REPORTED", -73.97, 40.75),
    (18, "Americas", "US attorney general dodges questions on the Nvidia investigation.", "REPORTED", -77.04, 38.9),
    (19, "Americas", "Trump administration poised to unveil new tariffs after excess-capacity probe.", "FORECAST", -77.04, 38.9),
    (20, "Americas", "Trump orders DOJ to speed federal death sentences, seek death penalty for child killers.", "REPORTED", -77.04, 38.9),
    (21, "Americas", "Kilmar Abrego Garcia to leave the US voluntarily and fly to Europe.", "REPORTED", -77.04, 38.9),
    (22, "Middle East", "Eisenkot seals first coalition deal in Israel, with Lieberman's party.", "REPORTED", 35.21, 31.77),
    (23, "Europe", "Britain opens inquiry into nuclear-test veterans' health.", "REPORTED", -0.12, 51.5),
    (24, "Asia-Pacific", "Magnitude 5.6 quake strikes Nepal near the Chinese border.", "REPORTED", 87.0, 27.9),
    (25, "Africa", "About 175 migrants unaccounted for after contact lost with a boat from Senegal.", "REPORTED", -17.45, 14.69),
    (26, "Americas", "Mexico inflation hits a six-month high at 3.96%.", "REPORTED", -99.13, 19.43),
    (27, "Asia-Pacific", "Bangladesh's Hasina says she will return on 16 December despite death sentence.", "REPORTED", 90.41, 23.81),
    (28, "Americas", "Court clears US Army to detonate five tons of unstable explosives in Iowa.", "REPORTED", -93.62, 41.59),
    (29, "Americas", "Pennsylvania measles outbreak: ninth death, 1,638 cases.", "REPORTED", -76.88, 40.27),
    (30, "Americas", "Car bomb wounds more than 20 in Villavicencio, Colombia.", "REPORTED", -73.64, 4.15),
    (31, "Africa", "DR Congo military plane missing; rebels claim they shot it down.", "CLAIM", 15.31, -4.32),
    (32, "Middle East", "Land-mine casualties soar in Syria, two years after the war.", "REPORTED", 36.29, 33.51),
    (33, "Europe", "Sarkozy and Carla Bruni to face trial next year.", "REPORTED", 2.35, 48.86),
    (34, "Africa", "Nigerian monarch, 92, suspended over alleged sexual assault of a tourist.", "REPORTED", 8.32, 13.04),
    (35, "Asia-Pacific", "Sooryavanshi, 15, smashes sixes record with 204 off 53 balls.", "REPORTED", 85.1, 25.6),
]

DATE_CHECK = [
    "Nvidia reinstates Huang (Mon 23 Nov) \u2014 Tuesday's slide is the story",
    "Ukraine sinks Russian ship Merkury off Libya (Sun) \u2014 Libya's demand is Tuesday",
    "Iran vows to fight US blockade (Mon 23 Nov)",
    "COP31 collapse (Sun 22 Nov)",
    "Skubal's $450m Mets deal (Sun 23 Nov)",
    "CrowdStrike buys Zscaler (Mon 23 Nov)",
    "49ers release Brandon Aiyuk (Mon 23 Nov)",
    "Cikande factory fire toll (Mon 23 Nov)",
    "Democrats take the House (Mon 23 Nov)",
    "Russian aircraft in South Korea's ADIZ (Mon 23 Nov)",
]

TALLY = [("EUROPE", 8), ("AMERICAS", 9), ("MIDDLE EAST", 5),
         ("ASIA-PACIFIC", 7), ("AFRICA", 4), ("WORLD", 2)]

# Pin offsets (dx, dy) in px from the true projected position, to keep
# clustered pins readable. A thin leader line joins pin to true spot.
PIN_OFFSETS = {
    11: (-4, -23), 17: (15, -17), 15: (23, 2), 18: (12, 20), 19: (-8, 22),
    20: (-22, 7), 21: (-19, -13),          # Washington DC / New York cluster
    29: (36, -24), 28: (-18, 10),          # Harrisburg / Des Moines
    12: (-10, 10), 33: (12, -6), 23: (-16, -14),   # Paris / London
    8: (-10, 12), 22: (-18, -16), 32: (16, 12),    # Gaza / Jerusalem / Damascus
    14: (-11, -8), 25: (11, 8),            # Dakar
    4: (12, -10), 5: (2, -14), 6: (-14, -8), 7: (12, 8),  # E. Europe
    24: (-16, -12), 35: (10, 12), 27: (18, -4), 13: (16, 12),  # S. Asia
}

ALL_PINS = []
for L in LEADS:
    ALL_PINS.append((L["n"], L["lon"], L["lat"]))
for C in CARDS:
    ALL_PINS.append((C["n"], C["lon"], C["lat"]))
for n, _r, _t, _tag, lon, lat in BRIEFS:
    ALL_PINS.append((n, lon, lat))


# ---------------------------------------------------------------- map
def render_map(map_w, map_h, lat_top=70.0, lat_bot=-50.0):
    """Realistic world map from GeoJSON country outlines (equirectangular)."""
    layer = Image.new("RGB", (map_w, map_h), OCEAN)
    d = ImageDraw.Draw(layer)
    with open(os.path.join(HERE, "countries.geo.json")) as f:
        geo = json.load(f)

    def proj(lon, lat):
        x = (lon + 180.0) / 360.0 * map_w
        y = (lat_top - lat) / (lat_top - lat_bot) * map_h
        return x, y

    def draw_ring(ring):
        # Split the ring wherever longitude jumps across the antimeridian.
        parts, cur = [], []
        prev_lon = None
        for lon, lat in ring:
            if prev_lon is not None and abs(lon - prev_lon) > 180:
                if len(cur) > 2:
                    parts.append(cur)
                cur = []
            cur.append(proj(lon, lat))
            prev_lon = lon
        if len(cur) > 2:
            parts.append(cur)
        for poly in parts:
            d.polygon(poly, fill=LAND, outline=COAST)

    for feat in geo["features"]:
        geom = feat["geometry"]
        if geom is None:
            continue
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                draw_ring(ring)
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                for ring in poly:
                    draw_ring(ring)
    return layer, proj


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead
    title_f = font(SERIF_B, 50)
    title = "THE WORLD IN ONE DAY"
    tw = draw.textlength(title, font=title_f)
    draw.text(((W - tw) / 2, 12), title, font=title_f, fill=INK)
    date_f = font(SANS_B, 14)
    date_line = "T U E S D A Y   2 4   N O V E M B E R   2 0 2 6"
    dw = draw.textlength(date_line, font=date_f)
    draw.text(((W - dw) / 2, 68), date_line, font=date_f, fill=MUTED)
    draw.line([(MARGIN, 90), (W - MARGIN, 90)], fill=RULE, width=2)
    draw.line([(MARGIN, 94), (W - MARGIN, 94)], fill=RULE, width=1)

    # ---- stat strip
    y = 100
    draw.text((MARGIN, y), "35 STORIES  \u00b7  6 REGIONS", font=font(SANS_B, 13), fill=INK)
    tally = "   \u00b7   ".join(f"{name} {n}" for name, n in TALLY)
    tw = draw.textlength(tally, font=font(SANS, 11))
    draw.text((W - MARGIN - tw, y + 1), tally, font=font(SANS, 11), fill=MUTED)
    draw.line([(MARGIN, 120), (W - MARGIN, 120)], fill=LIGHT_RULE, width=1)

    # ---- leads (top band, 3 columns)
    lead_w = (CW - 2 * 12) // 3  # 317
    photo_h = 110
    ly = 126
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (lead_w + 12)
        photo = Image.open(os.path.join(HERE, lead["photo"])).convert("RGB")
        # centre-crop to the box aspect, then downscale (keeps size small)
        pw, ph = photo.size
        target = lead_w / photo_h
        if pw / ph > target:
            nw = int(ph * target)
            photo = photo.crop(((pw - nw) // 2, 0, (pw - nw) // 2 + nw, ph))
        else:
            nh = int(pw / target)
            photo = photo.crop((0, (ph - nh) // 2, pw, (ph - nh) // 2 + nh))
        photo = photo.resize((lead_w, photo_h), Image.LANCZOS)
        img.paste(photo, (x, ly))
        draw.rectangle([x, ly, x + lead_w - 1, ly + photo_h - 1], outline=RULE, width=1)
        draw_badge(draw, x + 13, ly + 13, lead["n"], d=19)
        cap_f = font(SANS, 8)
        draw.text((x, ly + photo_h + 4), "PHOTO: AI ILLUSTRATION", font=cap_f, fill=MUTED)
        hy = ly + photo_h + 18
        hl_f = font(SERIF_B, 17)
        for j, line in enumerate(wrap(draw, lead["headline"], hl_f, lead_w)):
            draw.text((x, hy + j * 21), line, font=hl_f, fill=INK)
        sy = hy + 2 * 21 + 2
        sum_f = font(SANS, 9)
        for j, line in enumerate(wrap(draw, lead["summary"], sum_f, lead_w)[:4]):
            draw.text((x, sy + j * 12), line, font=sum_f, fill=(45, 45, 45))
        ty = sy + 4 * 12 + 5
        draw_tag(draw, x, ty, lead["tag"])
        reg_f = font(SANS_B, 9)
        draw.text((x + 62, ty + 2), lead["region"].upper(), font=reg_f, fill=MUTED)

    # ---- cards (3 cols x 5 rows; 13 cards)
    card_w = (CW - 2 * 8) // 3  # 320
    card_h, card_gap = 54, 5
    cy0 = 372
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 3)
        x = MARGIN + col * (card_w + 8)
        y = cy0 + row * (card_h + card_gap)
        draw.rectangle([x, y, x + card_w - 1, y + card_h - 1],
                       outline=LIGHT_RULE, width=1)
        draw_badge(draw, x + 11, y + 11, card["n"], d=15)
        # tag chip top-right
        tag_f = font(SANS_B, 8)
        tw = draw.textlength(card["tag"], font=tag_f)
        chip_w = int(tw) + 10
        draw.rounded_rectangle([x + card_w - chip_w - 5, y + 4,
                                x + card_w - 5, y + 17], radius=3,
                               fill=TAG_COLORS[card["tag"]])
        draw.text((x + card_w - chip_w, y + 6), card["tag"], font=tag_f,
                  fill=(255, 255, 255))
        hl_f = font(SERIF_B, 12)
        hl_w = card_w - 24 - chip_w - 8
        hl_lines = wrap(draw, card["headline"], hl_f, hl_w)[:2]
        for j, line in enumerate(hl_lines):
            draw.text((x + 22, y + 3 + j * 14), line, font=hl_f, fill=INK)
        sum_f = font(SANS, 9)
        sum_lines = wrap(draw, card["summary"], sum_f, card_w - 12)[:2]
        sy = y + 3 + max(1, len(hl_lines)) * 14 + 1
        for j, line in enumerate(sum_lines):
            draw.text((x + 6, sy + j * 11), line, font=sum_f, fill=(45, 45, 45))

    # ---- world map panel + right column (legend + date check)
    map_x, map_y = MARGIN, 660
    map_w, map_h = 616, 206
    sec_f = font(SANS_B, 12)
    draw.text((map_x, 642), "THE WORLD TODAY \u2014 EVERY STORY PINNED 1\u201335",
              font=sec_f, fill=INK)
    layer, proj = render_map(map_w, map_h)
    img.paste(layer, (map_x, map_y))
    draw.rectangle([map_x, map_y, map_x + map_w - 1, map_y + map_h - 1],
                   outline=RULE, width=1)
    md = ImageDraw.Draw(img)
    for n, lon, lat in ALL_PINS:
        bx, by = proj(lon, lat)
        bx += map_x
        by += map_y
        dx, dy = PIN_OFFSETS.get(n, (0, 0))
        px, py = bx + dx, by + dy
        if (dx, dy) != (0, 0):
            md.line([(bx, by), (px, py)], fill=(90, 88, 82), width=1)
            md.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(18, 18, 18))
        draw_badge(md, px, py, n, d=17 if n >= 10 else 15)

    rx = map_x + map_w + 12  # 652
    rw = W - MARGIN - rx     # 348
    # legend
    draw.rectangle([rx, map_y, rx + rw - 1, map_y + 62], outline=LIGHT_RULE, width=1)
    draw.text((rx + 8, map_y + 6), "HOW TO READ THIS PAGE", font=font(SANS_B, 10), fill=INK)
    lx = rx + 8
    ly2 = map_y + 26
    for tag, note in [("REPORTED", "confirmed"),
                      ("CLAIM", "unverified"),
                      ("FORECAST", "expected")]:
        w = draw_tag(draw, lx, ly2, tag)
        draw.text((lx + w + 5, ly2 + 1), note, font=font(SANS, 9), fill=MUTED)
        lx += w + 5 + draw.textlength(note, font=font(SANS, 9)) + 12
    draw.text((rx + 8, map_y + 44), "Pins 1\u201335 match the stories on this page.",
              font=font(SANS, 9), fill=MUTED)

    # date check box
    dc_y = map_y + 70
    dc_h = map_y + map_h - dc_y
    draw.rectangle([rx, dc_y, rx + rw - 1, dc_y + dc_h - 1],
                   outline=RULE, width=1)
    draw.text((rx + 8, dc_y + 6), "DATE CHECK \u2014 NOT TODAY'S NEWS",
              font=font(SANS_B, 10), fill=INK)
    dc_f = font(SANS, 8)
    for j, item in enumerate(DATE_CHECK):
        draw.text((rx + 8, dc_y + 24 + j * 11), "\u2022  " + item, font=dc_f,
                  fill=(70, 68, 62))

    # ---- briefs
    by0 = 874
    draw.text((MARGIN, by0), "IN BRIEF", font=sec_f, fill=INK)
    draw.line([(MARGIN, by0 + 16), (W - MARGIN, by0 + 16)], fill=LIGHT_RULE, width=1)
    br_f = font(SANS, 8)
    br_b = font(SANS_B, 8)
    col_w = (CW - 24) // 2
    for idx, (n, _r, text, tag, _lon, _lat) in enumerate(BRIEFS):
        col, row = divmod(idx, 10)
        x = MARGIN + col * (col_w + 24)
        y = by0 + 20 + row * 9
        num = f"{n}  "
        draw.text((x, y), num, font=br_b, fill=INK)
        nw = draw.textlength(num, font=br_b)
        line = text + "  [" + tag + "]"
        draw.text((x + nw, y), line, font=br_f, fill=(45, 45, 45))

    # ---- footer
    fy = 1002
    draw.line([(MARGIN, fy - 4), (W - MARGIN, fy - 4)], fill=LIGHT_RULE, width=1)
    foot = "Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 The Guardian \u00b7 Al Jazeera \u00b7 France 24 \u00b7 Xinhua \u00b7 CBS News"
    fw = draw.textlength(foot, font=font(SANS, 9))
    draw.text(((W - fw) / 2, fy + 2), foot, font=font(SANS, 9), fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("saved", out, img.size)


if __name__ == "__main__":
    build()
