# Tools — the card factory

Every card face in Lucky Draw is rendered by code, not designed by hand.
Feed the renderer a JSON entry and a hero photo; it produces the 1080×1440
card face used by the draw, the lightbox and the collection.

- **`make_card.py`** — the original renderer (Chinese names/dishes, English
  structure). Fixed type scale; callers must respect the width budget, and
  the pipeline audits rendered lines so text can never silently overflow.
  Uses the SC face of Noto Sans CJK (font index 2) — the default face is the
  JP cut and draws several glyphs in their Japanese forms.
- **`make_card_en.py`** — the English edition. Same layout system, but every
  text element auto-fits: long shop names shrink until they fit the face.
  English names are simply longer; a fixed scale would clip them.

Entry format (per place):

```json
{
  "kicker": "MILK TEA · SAN GABRIEL",
  "name": "Bopomofo Cafe",
  "tagline": "Playful Taiwanese-American drinks, real tea",
  "rating": 4.3, "price": "$9", "cuisine": "Drinks",
  "mustTry": ["Carrot Matcha Latte", "Ba-La Matcha", "Orange Wang"],
  "address": "841 W Las Tunas Dr",
  "tip": "Popular, so drinks come out slow",
  "hero": "hero.jpg",
  "accent": "#C96F4A"
}
```

Design rules baked into both renderers: one accent color per card; hero photo
cover-cropped into the face (never letterboxed); the meta line is Latin-only;
the footer is address + one honest tip, trimmed at clause boundaries.
