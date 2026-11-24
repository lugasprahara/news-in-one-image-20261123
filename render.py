#!/usr/bin/env python3
"""render.py — draws entry.png (1024x1024) for the make.fun news-image-20261123 entry.

"The Day in One Image": one front page for Monday 23 November 2026, in the
house format — paper background, deep-teal masthead with the day huge at the
left, a coral story-count block, a wide hero panel, twelve numbered story
panels, a briefs block, a dark dotted world atlas with numbered markers, and
a sources footer. All story content lives in stories.json (day-checked, see
SOURCES.md); this script only does layout, so re-running it reproduces the
identical image.

Usage: python3 render.py [output-path]   (default: entry.png beside this file)
Requires: Python 3 + Pillow. Fonts: Noto Sans / DejaVu Sans (system fonts).
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette ---
PAPER = (245, 237, 220)      # #f5eddc
CARD = (255, 253, 246)       # #fffdf6
BORDER = (216, 205, 178)     # #d8cdb2
INK = (16, 46, 51)           # #102e33
TEAL = (12, 56, 61)          # #0c383d
TEAL_MID = (13, 110, 107)    # #0d6e6b
CORAL = (228, 87, 46)        # #e4572e
CORAL_SOFT = (255, 140, 90)  # #ff8c5a
AMBER = (233, 161, 59)       # #e9a13b
CREAM = (253, 246, 227)      # #fdf6e3
MUTED = (76, 90, 84)         # #4c5a54
FAINT = (188, 216, 210)      # #bcd8d2
ACCENTS = {"teal": TEAL_MID, "coral": CORAL, "amber": (198, 127, 26)}

F_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_XBOLD = "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf"
F_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
F_DREG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W = H = 1024
PAD = 12
GAP = 7


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def spaced(draw, xy, s, f, fill, tracking=2.0):
    """Draw letter-spaced uppercase text; returns total width drawn."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += text_w(draw, ch, f) + tracking
    return x - tracking - xy[0]


def spaced_w(draw, s, f, tracking=2.0):
    return sum(text_w(draw, ch, f) for ch in s) + tracking * max(0, len(s) - 1)


def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def chip(draw, cx, cy, n, r=10):
    """Coral number disc, centred at (cx, cy)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CORAL)
    f = font(F_XBOLD, 12 if n < 10 else 10)
    s = str(n)
    w = text_w(draw, s, f)
    draw.text((cx - w / 2, cy - 8 if n < 10 else -7 + cy), s, font=f, fill=(255, 247, 236))


# ------------------------------------------------------------- hero scene ---
def hero_scene(draw, box):
    """Stylised globe with a broken coral ring — the world failing to agree."""
    x0, y0, x1, y1 = box
    rrect(draw, box, 0, fill=TEAL)
    cx, cy, R = (x0 + x1) // 2, (y0 + y1) // 2 + 4, 52
    # latitude / longitude lines
    for k in (-0.66, -0.33, 0.0, 0.33, 0.66):
        yy = cy + k * R
        half = math.sqrt(max(0.0, R * R - (k * R) ** 2))
        draw.line([cx - half, yy, cx + half, yy], fill=FAINT, width=1)
    for k in (-0.7, -0.35, 0.0, 0.35, 0.7):
        rx = abs(k) * R if k else 1
        draw.ellipse([cx - rx, cy - R, cx + rx, cy + R], outline=FAINT, width=1)
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], outline=CREAM, width=2)
    # broken coral ring around the globe
    draw.arc([cx - R - 13, cy - R - 13, cx + R + 13, cy + R + 13],
             start=305, end=115, fill=CORAL, width=4)
    draw.arc([cx - R - 13, cy - R - 13, cx + R + 13, cy + R + 13],
             start=150, end=272, fill=CORAL, width=4)
    # a few stars
    for sx, sy in ((x0 + 26, y0 + 18), (x1 - 30, y0 + 26), (x0 + 40, y1 - 20),
                   (x1 - 52, y1 - 30), (x1 - 20, cy - 8)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=AMBER)
    f = font(F_BOLD, 9)
    label = "A N T A L Y A"
    draw.text((cx - spaced_w(draw, label, f, 2) / 2, y1 - 20), label, font=f, fill=FAINT)


def band_motif(draw, box, accent):
    """Thin scene band on a story panel: accent fill + quiet white dot rhythm."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=accent)
    cy = (y0 + y1) // 2
    x = x0 + 12
    i = 0
    while x < x1 - 12:
        r = 2 if i % 3 else 3
        draw.ellipse([x - r, cy - r, x + r, cy + r], fill=(255, 255, 255))
        x += 17
        i += 1


# ---------------------------------------------------------------- panels ----
def panel(draw, box, story, with_band=True):
    x0, y0, x1, y1 = box
    rrect(draw, box, 10, fill=CARD, outline=BORDER, width=2)
    ty = y0
    if with_band:
        # clip a band to the panel's top by drawing over with a rounded top
        band_motif(draw, (x0 + 2, y0 + 2, x1 - 2, y0 + 25), ACCENTS[story.get("accent", "teal")])
        draw.rectangle([x0 + 2, y0 + 14, x1 - 2, y0 + 25],
                       fill=ACCENTS[story.get("accent", "teal")])
        ty = y0 + 25
    tx = x0 + 11
    tw = (x1 - x0) - 22
    # number chip + tag on one line
    chip(draw, tx + 10, ty + 13, story["n"])
    tf = font(F_BOLD, 10)
    spaced(draw, (tx + 27, ty + 6), story["tag"], tf, TEAL_MID, 1.2)
    # headline (bold, shrink to fit <= 2 lines)
    hy = ty + 24
    size = 16
    while size > 10:
        hf = font(F_XBOLD, size)
        lines = wrap(draw, story["headline"], hf, tw)
        if len(lines) <= 2:
            break
        size -= 1
    for ln in lines:
        draw.text((tx, hy), ln, font=hf, fill=INK)
        hy += size + 2
    # summary (regular, shrink to fit the rest of the panel)
    avail = (y1 - 6) - (hy + 1)
    size = 11
    while size > 8:
        sf = font(F_REG, size)
        lines = wrap(draw, story["summary"], sf, tw)
        if len(lines) * (size + 2) <= avail:
            break
        size -= 1
    sy = hy + 1
    # hard guard: never draw past the panel's bottom edge — clip with an ellipsis
    max_lines = max(1, avail // (size + 2))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and text_w(draw, last + "…", sf) > tw:
            last = last[:-1].rstrip()
        lines[-1] = last + "…"
    for ln in lines:
        draw.text((tx, sy), ln, font=sf, fill=MUTED)
        sy += size + 2


# ----------------------------------------------------------------- atlas ----
# stylised dotted world map: (row, first col, last col) land spans, 100x19 grid
LAND = [
    (0, [(5, 20), (34, 42), (63, 97)]),
    (1, [(3, 30), (35, 41), (52, 57), (60, 98)]),
    (2, [(3, 33), (36, 39), (46, 47), (52, 58), (59, 99)]),
    (3, [(4, 10), (14, 34), (48, 60), (60, 97)]),
    (4, [(13, 36), (47, 61), (62, 95), (93, 96)]),
    (5, [(12, 31), (47, 60), (60, 66), (67, 92), (93, 95)]),
    (6, [(13, 29), (45, 63), (61, 68), (68, 90), (78, 92)]),
    (7, [(14, 24), (44, 64), (60, 67), (70, 79), (80, 90)]),
    (8, [(15, 23), (44, 55), (56, 64), (71, 78), (80, 88)]),
    (9, [(19, 23), (29, 36), (44, 62), (73, 76), (81, 87)]),
    (10, [(28, 38), (47, 60), (79, 95)]),
    (11, [(28, 39), (48, 59), (80, 98)]),
    (12, [(29, 39), (49, 58), (84, 93)]),
    (13, [(30, 38), (50, 57), (82, 94)]),
    (14, [(31, 37), (51, 56), (83, 95)]),
    (15, [(31, 36), (52, 55), (85, 94), (97, 99)]),
    (16, [(32, 35), (97, 99)]),
    (17, [(32, 34), (96, 98)]),
    (18, [(32, 34)]),
]


# hand nudges so dense clusters (US east coast, Europe, the Levant) stay legible
MARKER_OFFSETS = {5: (2, -3), 6: (-7, 6), 9: (-4, -5), 12: (0, 7), 16: (-5, 4),
                  17: (6, -4), 18: (-7, 1), 19: (6, 5)}


def atlas(draw, box, stories):
    x0, y0, x1, y1 = box
    rrect(draw, box, 10, fill=TEAL)
    f = font(F_BOLD, 9)
    spaced(draw, (x0 + 14, y0 + 8), "THE WORLD ON MONDAY — WHERE THE STORIES LANDED", f, FAINT, 1.5)
    gx0, gy0 = x0 + 14, y0 + 24
    gx1, gy1 = x1 - 14, y1 - 6
    gw, gh = gx1 - gx0, gy1 - gy0
    # land dots
    for row, spans in LAND:
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                px = gx0 + (c + 0.5) * gw / 100
                py = gy0 + (row + 0.5) * gh / 19
                draw.ellipse([px - 1.3, py - 1.3, px + 1.3, py + 1.3], fill=(62, 110, 108))
    # numbered markers
    for st in stories:
        n = st["n"]
        if st.get("lat") is None:
            # Mercury: a small ringed planet at the top-right of the atlas
            px, py = gx1 - 26, gy0 + 12
            draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=AMBER)
            draw.arc([px - 11, py - 4, px + 11, py + 5], start=200, end=520, fill=CREAM, width=2)
            draw.ellipse([px + 8, py - 13, px + 21, py + 0], fill=CORAL)
            sf = font(F_XBOLD, 8)
            draw.text((px + 10.5, py - 11), "8", font=sf, fill=(255, 247, 236))
            continue
        px = gx0 + (st["lon"] + 180) / 360 * gw
        py = gy0 + (78 - st["lat"]) / 140 * gh
        dx, dy = MARKER_OFFSETS.get(n, (0, 0))
        px, py = px + dx, py + dy
        r = 7.5
        draw.ellipse([px - r, py - r, px + r, py + r], fill=CORAL, outline=CREAM, width=1)
        sf = font(F_XBOLD, 8 if n >= 10 else 9)
        s = str(n)
        draw.text((px - text_w(draw, s, sf) / 2, py - 5), s, font=sf, fill=(255, 247, 236))


# ------------------------------------------------------------------ main ----
def main():
    data = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    mh = (PAD, PAD, W - PAD - 205, PAD + 84)
    rrect(draw, mh, 10, fill=TEAL)
    kf = font(F_BOLD, 11)
    spaced(draw, (mh[0] + 18, mh[1] + 8), "THE DAY IN ONE IMAGE · WORLD NEWS, ONE PAGE", kf, AMBER, 3.5)
    df = font(F_BLACK, 42)
    draw.text((mh[0] + 18, mh[1] + 25), data["date_line"], font=df, fill=CREAM)
    day_w = text_w(draw, data["date_line"], df)
    ff = font(F_XBOLD, 22)
    parts = data["full_date"].split(" ", 1)
    draw.text((mh[0] + 30 + day_w, mh[1] + 40), parts[0], font=ff, fill=CORAL_SOFT)
    w2 = text_w(draw, parts[0], ff)
    draw.text((mh[0] + 36 + day_w + w2, mh[1] + 40), " " + parts[1], font=ff, fill=CREAM)
    ef = font(F_BOLD, 9)
    spaced(draw, (mh[2] - 250, mh[3] - 19), "EVERY STORY DAY-CHECKED", ef, FAINT, 1.8)

    cb = (W - PAD - 198, PAD, W - PAD, PAD + 84)
    rrect(draw, cb, 10, fill=CORAL)
    cf = font(F_XBOLD, 26)
    draw.text((cb[0] + 14, cb[1] + 8), data["count_line"], font=cf, fill=(255, 247, 236))
    cf2 = font(F_XBOLD, 15)
    draw.text((cb[0] + 14, cb[1] + 40), data["continents_line"], font=cf2, fill=(255, 227, 194))
    sf = font(F_BOLD, 9)
    spaced(draw, (cb[0] + 14, cb[1] + 62), "ONE PAGE · NO NOISE", sf, (255, 227, 194), 1.6)

    # ---- hero ----------------------------------------------------------
    hy0 = PAD + 84 + GAP
    hero = data["hero"]
    hb = (PAD, hy0, W - PAD, hy0 + 124)
    rrect(draw, hb, 10, fill=CARD, outline=BORDER, width=2)
    hero_scene(draw, (hb[0] + 2, hb[1] + 2, hb[0] + 340, hb[3] - 2))
    tx = hb[0] + 356
    tw = hb[2] - tx - 16
    chip(draw, tx + 10, hb[1] + 22, hero["n"], r=11)
    tf = font(F_BOLD, 12)
    spaced(draw, (tx + 30, hb[1] + 14), hero["tag"], tf, TEAL_MID, 1.4)
    hf = font(F_BLACK, 27)
    lines = wrap(draw, hero["headline"], hf, tw)
    yy = hb[1] + 36
    for ln in lines:
        draw.text((tx, yy), ln, font=hf, fill=INK)
        yy += 30
    sf2 = font(F_REG, 12)
    for ln in wrap(draw, hero["summary"], sf2, tw):
        draw.text((tx, yy + 3), ln, font=sf2, fill=MUTED)
        yy += 16

    # ---- panel rows ------------------------------------------------------
    rows = [(130, data["panels"][0:3]), (134, data["panels"][3:6]),
            (132, data["panels"][6:9]), (128, data["panels"][9:11])]
    y = hy0 + 124 + GAP
    col_w = (W - 2 * PAD - 2 * GAP) // 3
    for rh, group in rows:
        wdt = col_w if len(group) == 3 else (W - 2 * PAD - GAP) // 2
        for i, st in enumerate(group):
            x = PAD + i * (wdt + GAP)
            panel(draw, (x, y, x + wdt, y + rh), st)
        y += rh + GAP

    # ---- briefs ----------------------------------------------------------
    bb = (PAD, y, W - PAD, y + 110)
    rrect(draw, bb, 10, fill=CARD, outline=BORDER, width=2)
    bf = font(F_BOLD, 11)
    spaced(draw, (bb[0] + 14, bb[1] + 9), "IN BRIEF — TEN MORE LINES FROM MONDAY", bf, TEAL_MID, 2.0)
    briefs = data["briefs"]
    colw = (W - 2 * PAD - 30) // 2
    for i, br in enumerate(briefs):
        col = i // 5
        row = i % 5
        bx = bb[0] + 14 + col * (colw + 8)
        by = bb[1] + 30 + row * 15
        nf = font(F_XBOLD, 10)
        draw.text((bx, by), str(br["n"]), font=nf, fill=CORAL)
        tf2 = font(F_REG, 10)
        s = br["text"]
        while text_w(draw, s, tf2) > colw - 26 and len(s) > 10:
            s = s[:-1]
        draw.text((bx + 24, by), s, font=tf2, fill=INK)
    y = bb[3] + GAP

    # ---- atlas -----------------------------------------------------------
    ab = (PAD, y, W - PAD, y + 74)
    atlas(draw, ab, [data["hero"]] + data["panels"] + data["briefs"])
    y = ab[3] + GAP

    # ---- footer ----------------------------------------------------------
    ff2 = font(F_DREG, 10)
    line = data["sources_line"]
    draw.text(((W - text_w(draw, line, ff2)) / 2, y + 4), line, font=ff2, fill=MUTED)
    ff3 = font(F_BOLD, 8)
    tail = "GENERATED FROM STORIES.JSON BY RENDER.PY · 1024 × 1024"
    draw.text(((W - spaced_w(draw, tail, ff3, 1.5)) / 2, y + 22), tail, font=ff3, fill=TEAL_MID)

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out}: {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
