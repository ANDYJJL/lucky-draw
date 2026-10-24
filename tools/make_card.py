#!/usr/bin/env python3
"""Render an Apple-style place card (1080x1440 JPG) from a JSON entry + hero image.

Usage:
  make_card.py --data entry.json --hero hero.jpg --out card.jpg

entry.json fields:
  kicker   e.g. "THAI · PASADENA, CA"  or bilingual "奶茶 TEA · SAN GABRIEL"
  name     e.g. "Kwan Kitchen" (Chinese shops: Chinese name main, English sub ok)
  tagline  one short line, e.g. "No-fail Thai. Every dish lands."
  rating   e.g. 4.5 (optional)
  meta     e.g. "$$ · $20–30    Open daily until 9 PM" (rating rendered separately)
  mustTry  list of up to 3 short strings (bilingual for Chinese shops)
  footer   e.g. "777 S Arroyo Pkwy, Unit 101 · Easy plaza parking"
"""
import argparse, json, math, os
from PIL import Image, ImageDraw, ImageFont

NOTO = "/usr/share/fonts/truetype/noto"
def font(name, size):
    return ImageFont.truetype(os.path.join(NOTO, name), size)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    e = json.load(open(a.data))

    W, H = 1080, 1440
    # Chinese glyphs: NotoSansCJK if present else NotoSans (falls back poorly) — prefer CJK
    cjk_b = "NotoSansCJK-Bold.ttc" if os.path.exists(f"{NOTO}/../noto-cjk/NotoSansCJK-Bold.ttc") else "NotoSans-Bold.ttf"
    F_TRACK = font("NotoSans-Bold.ttf", 27)
    F_NAME  = font("NotoSans-Bold.ttf", 72)
    F_SUB   = font("NotoSans-Regular.ttf", 32)
    F_META  = font("NotoSans-Bold.ttf", 30)
    F_LABEL = font("NotoSans-Bold.ttf", 24)
    F_ITEM  = font("NotoSans-Regular.ttf", 33)
    F_FOOT  = font("NotoSans-Regular.ttf", 26)
    try:
        # index=2 = the SC face. Index 0 is the JP face, whose variant glyphs
        # misrender some Simplified characters (e.g. 门 loses its diagonal dot).
        F_NAME = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 72, index=2)
        F_ITEM = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 33, index=2)
        F_SUB  = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 32, index=2)
        F_TRACK= ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 27, index=2)
        F_FOOT = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 26, index=2)
    except Exception:
        pass

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
    y = ch + 42
    def tracked(text, yy, fnt, fill, spacing=6):
        xx = 48
        for c in text:
            d.text((xx, yy), c, font=fnt, fill=fill)
            xx += d.textlength(c, font=fnt) + spacing
    if e.get("kicker"):
        tracked(e["kicker"], y, F_TRACK, ACCENT); y += 52
    d.text((48, y), e["name"], font=F_NAME, fill=INK); y += 96
    if e.get("tagline"):
        d.text((48, y), e["tagline"], font=F_SUB, fill=GRAY); y += 62
    # meta line with optional star+rating
    mx = 48
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
        d.text((mx, y), e["meta"], font=F_META, fill=INK)
    y += 66
    d.line([(48, y), (card.size[0] - 48, y)], fill=(232, 232, 234), width=2); y += 34
    items = e.get("mustTry") or []
    if items:
        tracked("MUST TRY", y, F_LABEL, FAINT, spacing=5); y += 42
        for item in items[:3]:
            d.ellipse([48, y + 13, 60, y + 25], fill=ACCENT)
            d.text((76, y), item, font=F_ITEM, fill=INK); y += 52
        y += 14
    if e.get("footer"):
        d.text((48, y), e["footer"], font=F_FOOT, fill=GRAY)

    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0], card.size[1]], radius=48, fill=255)
    bg.paste(card, (24, 24), mask)
    bg.save(a.out, quality=92)
    print("saved", a.out)

if __name__ == "__main__":
    main()
