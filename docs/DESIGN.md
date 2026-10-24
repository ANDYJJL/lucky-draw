# Design — glass, paper, and a deck of cards

Lucky Draw's look comes from a deliberate tension: **Apple-style glass UI**
(systematic, translucent, physical) carrying **warm, hand-made content**
(watercolor category art, a crayon-drawn app icon, real food photography).
The system feels precise; the content feels human. Neither half works alone —
glass around sterile stock photos is a tech demo, and scrapbook warmth without
a rigorous system is a mess.

## Foundations

- **Translucency with a hierarchy.** Panels are frosted glass over the user's
  own background photo. Blurred layers communicate stacking order without
  borders or shadows-for-decoration. Moving panels animate `opacity` and
  `transform` only — animating a `backdrop-filter` region makes the blur
  re-rasterize every frame and the color drifts.
- **Physical motion.** Transitions are springs, not eases: interruptible,
  velocity-aware, and spatially consistent — a card that flips open returns
  along the same path. The draw is a shuffle-and-flip with a duration that
  scales with deck size (capped at 8s): a 107-card deck should *feel* heavier
  than a 39-card one.
- **Typography does the talking.** Big optical-sized headlines, letterspaced
  small caps "kickers" (`MILK TEA · SAN GABRIEL`), and a strict rule on cards:
  one accent color, name → tagline → rating/price/hours → must-try → footer.
  On card faces the meta line is Latin-only by design — the display font's CJK
  glyphs would break the rhythm, so Chinese lives in the name and dishes where
  it belongs.
- **Restraint.** No gradients-for-fun, no emoji in the UI chrome, no badges
  begging for attention. Every element on the draw screen exists to serve one
  action.

## Details that were fought for

- **The close × that never jumps.** In the lightbox, the close button is
  anchored above the card's top-right corner and animates in sync with the
  card. An earlier version let it drift with layout; it read as sloppiness
  every single time it was seen.
- **Fixed action rows.** "Navigate / Menu" buttons occupy a reserved line under
  every card, rated or not — content never shifts because a place has a score.
  Layout stability is a form of politeness.
- **A chalk underline for today.** In the diary calendar, today is marked by a
  small hand-drawn chalk stroke under the numeral — the one deliberately
  imperfect element in the calendar, because a diary should feel kept by hand.
- **Pool checkboxes are circles, solid green, no checkmark.** A filled circle
  reads as "in the deck" from across the room; a checkmark reads as a form.
  This is a toy before it is a tool.
- **Card covers must earn it.** The cover photo rules are editorial: no
  burned-in title text or stickers (real signage is fine), no strangers'
  hands, and for food — it must look *appetizing*, not merely accurate.
  A technically correct photo of a sad dish quietly kills a card.
- **English is designed, not squeezed.** Tab labels have dedicated short forms
  ("Boba", "Play") so nothing wraps; atlas names clamp to two lines by rule;
  card-back hierarchy flips (small line = cuisine in English, big word = the
  pool's short name). Long English shop names auto-shrink on card faces until
  they fit — clipping is never an option.

## The icon & the art

The app icon is a crayon illustration of a card box — drawn, not rendered —
because the product is a game you play with dinner, and the home screen is a
serious place that benefits from one unserious icon. The four category decks
wear watercolor collages of their worlds (boba cups and San Gabriel Blvd;
observatories and piers for Play), so the *backs* of the cards are worth
looking at during the shuffle — the moment of anticipation is a designed
surface too.

## Accessibility & honesty

- Every image carries meaningful alt text, localized with the UI.
- Reduced-motion and small-viewport states are treated as real configurations,
  not edge cases.
- Nothing on a card is decorative-only: if a rating, price or hour is shown,
  it came from a checked source — design never invents data to fill a layout.
