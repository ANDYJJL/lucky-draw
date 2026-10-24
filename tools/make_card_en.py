#!/usr/bin/env python3
"""English-card variant of make_card.py — identical layout, but every text
element auto-shrinks its font to fit the card width (long English names /
taglines / footers must never clip). Chinese cards keep using the original
fixed-size renderer.

Usage: make_card_en.py --data entry.json --hero hero.jpg --out card.jpg"""
import argparse, json, math, os
from PIL import Image, ImageDraw, ImageFont

NOTO = "/usr/share/fonts/truetype/noto"
CJK_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
CJK_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
LAT_B = os.path.join(NOTO, "NotoSans-Bold.ttf")

SPECS = {  # key -> (path, ttc index or None, base size)
    "track": (CJK_B, 2, 27),
    "name": (CJK_B, 2, 72),
    "sub": (CJK_R, 2, 32),
    "meta": (LAT_B, None, 30),
    "label": (LAT_B, None, 24),
    "item": (CJK_R, 2, 33),
    "foot": (CJK_R, 2, 26),
}

def make_font(key, size):
    path, idx, _ = SPECS[key]
    return ImageFont.truetype(path, size, index=idx) if idx is not None else ImageFont.truetype(path, size)

def fit_font(key, text, maxw, minsize, spacing=0):
    _, _, size = SPECS[key]
    while size > minsize:
        f = make_font(key, size)
        if spacing:
            w = sum(f.getlength(c) + spacing for c in text)
        else:
            w = f.getlength(text)
        if w <= maxw:
            return f
        size -= 2
    return make_font(key, minsize)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    e = json.load(open(a.data))

    W, H = 1080, 1440
    bg = Image.new("RGB", (W, H), (245, 245, 247))
    card = Image.new("RGB", (W - 48, H - 48), (255, 255, 255))
    hero = Image.open(a.hero).convert("RGB")
    cw, ch = card.size[0], 740
    scale = max(cw / hero.size[0], ch / hero.size[1])
    hero = hero.resize((int(hero.size[0] * scale), int(hero.size[1] * scale)))
    x = (hero.size[0] - cw) // 2; y = (hero.size[1] - ch) // 3
    card.paste(hero.crop((x, y, x + cw, y + ch)), (0, 0))

    d = ImageDraw.Draw(card)
    INK = (28, 28, 30); GRAY = (110, 110, 115); FAINT = (174, 174, 178); ACCENT = (214, 69, 36)
    MAXW = card.size[0] - 48 - 16  # text from x=48, keep a right margin
    y = ch + 42

    def tracked(text, yy, fnt, fill, spacing=6):
        xx = 48
        for c in text:
            d.text((xx, yy), c, font=fnt, fill=fill)
            xx += d.textlength(c, font=fnt) + spacing

    if e.get("kicker"):
        tracked(e["kicker"], y, fit_font("track", e["kicker"], MAXW, 19, spacing=6), ACCENT); y += 52
    d.text((48, y), e["name"], font=fit_font("name", e["name"], MAXW, 40), fill=INK); y += 96
    if e.get("tagline"):
        d.text((48, y), e["tagline"], font=fit_font("sub", e["tagline"], MAXW, 23), fill=GRAY); y += 62
    mx = 48
    F_META = make_font("meta", SPECS["meta"][2])
    if e.get("rating"):
        cx, cy, r = 60, y + 16, 13
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=ACCENT)
        d.text((84, y), str(e["rating"]), font=F_META, fill=INK)
        mx = 84 + int(d.textlength(str(e["rating"]), font=F_META)) + 28
    if e.get("meta"):
        d.text((mx, y), e["meta"], font=fit_font("meta", e["meta"], card.size[0] - mx - 16, 21), fill=INK)
    y += 66
    d.line([(48, y), (card.size[0] - 48, y)], fill=(232, 232, 234), width=2); y += 34
    items = e.get("mustTry") or []
    if items:
        tracked("MUST TRY", y, make_font("label", SPECS["label"][2]), FAINT, spacing=5); y += 42
        for item in items[:3]:
            d.ellipse([48, y + 13, 60, y + 25], fill=ACCENT)
            d.text((76, y), item, font=fit_font("item", item, card.size[0] - 76 - 16, 24), fill=INK); y += 52
        y += 14
    if e.get("footer"):
        d.text((48, y), e["footer"], font=fit_font("foot", e["footer"], MAXW, 19), fill=GRAY)

    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0], card.size[1]], radius=48, fill=255)
    bg.paste(card, (24, 24), mask)
    bg.save(a.out, quality=92)
    print("saved", a.out)

if __name__ == "__main__":
    main()
